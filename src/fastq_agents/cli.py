"""Command line interface for FASTQ Agent System."""

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(help="FASTQ Agent System - Multi-agent FASTQ file analysis")
console = Console()


@app.command()
def benchmark(
    fastq_file: str = typer.Option(
        "tests/fixtures/sample.fastq", help="Path to FASTQ file to benchmark"
    ),
    skip_ai: bool = typer.Option(
        False, "--skip-ai", help="Skip AI analysis for speed test"
    ),
):
    """Benchmark report generation performance."""
    import asyncio
    import time

    from .agents.parser import FASTQParserAgent
    from .agents.reporter import FASTQReportAgent

    console.print(f"[bold blue]🏃‍♂️ Benchmarking:[/bold blue] {fastq_file}")
    if skip_ai:
        console.print("[yellow]⚡ AI analysis disabled for speed test[/yellow]")

    async def run_benchmark():
        total_start = time.time()

        # Step 1: Parse the FASTQ file
        console.print("\n[cyan]⏱️  Step 1: Parsing FASTQ file...[/cyan]")
        parse_start = time.time()

        parser = FASTQParserAgent()
        parse_result = await parser.process(
            {"file_path": fastq_file, "fast_mode": skip_ai}
        )

        parse_time = time.time() - parse_start
        console.print(
            f"[green]✅ Parsing completed in {parse_time:.2f} seconds[/green]"
        )

        if parse_result["parsing_status"] != "success":
            console.print(f"[red]❌ Parsing failed[/red]")
            return

        # Step 2: Generate report
        console.print("\n[cyan]⏱️  Step 2: Generating analysis report...[/cyan]")
        report_start = time.time()

        reporter = FASTQReportAgent()
        report_result = await reporter.process(
            {
                "fastq_data": parse_result["fastq_data"],
                "output_dir": "./benchmark_reports",
                "format": "html",
                "fast_mode": skip_ai,
            }
        )

        report_time = time.time() - report_start
        total_time = time.time() - total_start

        if report_result["status"] == "success":
            console.print(
                f"[green]✅ Report completed in {report_time:.2f} seconds[/green]"
            )

            # Performance Summary
            console.print(f"\n[bold]📊 Performance Summary:[/bold]")
            console.print(f"  [blue]Parsing time:[/blue] {parse_time:.2f}s")
            console.print(f"  [blue]Report generation:[/blue] {report_time:.2f}s")
            console.print(f"  [bold green]Total time:[/bold green] {total_time:.2f}s")

            # Calculate rates
            reads = parse_result["fastq_data"].metrics.total_reads
            console.print(
                f"  [blue]Processing rate:[/blue] {reads/total_time:.1f} reads/second"
            )

            # Show breakdown
            ai_time = report_time - 1.0  # Rough estimate of non-AI time
            if not skip_ai and ai_time > 0:
                console.print(
                    f"  [yellow]Estimated AI time:[/yellow] {ai_time:.2f}s ({ai_time/total_time*100:.1f}% of total)"
                )

        else:
            console.print(f"[red]❌ Report generation failed[/red]")

    asyncio.run(run_benchmark())


@app.command()
def generate_report(
    fastq_file: str = typer.Argument(..., help="Path to FASTQ file to analyze"),
    output_dir: str = typer.Option("./reports", help="Output directory for reports"),
    format: str = typer.Option("html", help="Report format: html, json, markdown"),
    fast_mode: bool = typer.Option(
        False, "--fast", help="Skip AI analysis for faster processing"
    ),
    open_report: bool = typer.Option(
        False, "--open", help="Open directly in a web browser"
    ),
):
    """Generate a comprehensive analysis report for a FASTQ file."""
    import asyncio
    import webbrowser
    from pathlib import Path

    from .agents.parser import FASTQParserAgent
    from .agents.reporter import FASTQReportAgent
    from .models.reports import ReportFormat

    console.print(f"[bold blue]Analyzing:[/bold blue] {fastq_file}")
    console.print(f"[bold blue]Output directory:[/bold blue] {output_dir}")
    console.print(f"[bold blue]Format:[/bold blue] {format}")

    async def run_analysis():
        try:
            # Validate format
            try:
                report_format = ReportFormat(format.lower())
            except ValueError:
                console.print(
                    f"[red]Invalid format '{format}'. Use: html, json, markdown[/red]"
                )
                return

            # Step 1: Parse the FASTQ file
            console.print("\n[yellow]Step 1: Parsing FASTQ file...[/yellow]")
            parser = FASTQParserAgent()
            parse_result = await parser.process({"file_path": fastq_file})

            if parse_result["parsing_status"] != "success":
                console.print(
                    f"[red]❌ Parsing failed: {parse_result.get('error_message')}[/red]"
                )
                return

            console.print("[green]✅ FASTQ parsing completed[/green]")

            # Step 2: Generate report
            console.print("\n[yellow]Step 2: Generating analysis report...[/yellow]")
            if fast_mode:
                console.print(
                    "[blue]⚡ Fast mode enabled - skipping detailed AI analysis[/blue]"
                )

            reporter = FASTQReportAgent()
            report_result = await reporter.process(
                {
                    "fastq_data": parse_result["fastq_data"],
                    "output_dir": output_dir,
                    "format": report_format,
                    "fast_mode": fast_mode,
                }
            )

            if report_result["status"] != "success":
                console.print(
                    f"[red]❌ Report generation failed: {report_result.get('error_message')}[/red]"
                )
                return

            # Show results
            console.print("[green]✅ Report generated successfully![/green]")
            console.print(
                f"\n[bold]Report saved to:[/bold] {report_result['output_path']}"
            )

            summary = report_result["summary"]
            console.print(f"\n[bold]Analysis Summary:[/bold]")
            console.print(f"  Quality Assessment: {summary['quality_assessment']}")
            console.print(
                f"  Total Recommendations: {summary['total_recommendations']}"
            )
            console.print(f"  High Priority Issues: {summary['high_priority_issues']}")

            # Open in browser if requested
            if open_report and format.lower() == "html":
                report_path = Path(report_result["output_path"])
                if report_path.exists():
                    webbrowser.open(f"file://{report_path.absolute()}")
                    console.print("\n[blue]📊 Opening report in browser...[/blue]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    asyncio.run(run_analysis())


@app.command()
def debug_env():
    """Debug environment variable loading."""
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        # Show only first and last 10 characters for security
        masked_key = f"{api_key[:10]}...{api_key[-10:]}" if len(api_key) > 20 else "***"
        console.print(f"[green]✅ API key found:[/green] {masked_key}")
        console.print(f"[blue]Key length:[/blue] {len(api_key)} characters")
        console.print(f"[blue]Starts with:[/blue] {api_key[:10]}")
    else:
        console.print("[red]❌ ANTHROPIC_API_KEY not found in environment[/red]")
        console.print("\n[yellow]Debugging info:[/yellow]")
        console.print("Current working directory:", os.getcwd())
        console.print("Looking for .env file at:", os.path.join(os.getcwd(), ".env"))
        console.print(".env file exists:", os.path.exists(".env"))


@app.command()
def test_parser(
    fastq_file: str = typer.Option(
        "tests/fixtures/sample.fastq", help="Path to FASTQ file to test parsing"
    )
):
    """Test the FASTQ parser agent with a sample file."""
    import asyncio

    from .agents.parser import FASTQParserAgent

    console.print(f"[bold blue]Testing parser with:[/bold blue] {fastq_file}")

    async def run_test():
        agent = FASTQParserAgent()
        result = await agent.process({"file_path": fastq_file})

        if result["parsing_status"] == "success":
            console.print("[bold green]✅ Parsing successful![/bold green]")
            console.print("\n[bold]Summary:[/bold]")
            summary = result["summary"]
            for key, value in summary.items():
                console.print(f"  {key.replace('_', ' ').title()}: {value}")

            console.print(f"\n[bold]AI Analysis:[/bold]")
            console.print(result["llm_analysis"])
        else:
            console.print(
                f"[bold red]❌ Parsing failed:[/bold red] {result.get('error_message')}"
            )

    try:
        asyncio.run(run_test())
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@app.command()
def hello():
    """Test command to verify the CLI is working."""
    console.print(
        Panel(
            "🧬 FASTQ Agent System is ready!\n\n"
            "This is a test command to verify your setup is working.",
            title="Welcome",
            border_style="green",
        )
    )


@app.command()
def analyze(
    fastq_file: str = typer.Argument(..., help="Path to FASTQ file to analyze"),
    output_dir: str = typer.Option("./reports", help="Output directory for reports"),
):
    """Analyze a FASTQ file using the agent system."""
    console.print(f"[bold blue]Analyzing:[/bold blue] {fastq_file}")
    console.print(f"[bold blue]Output directory:[/bold blue] {output_dir}")

    # TODO: Implement actual analysis
    console.print("[yellow]Analysis functionality coming soon![/yellow]")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
