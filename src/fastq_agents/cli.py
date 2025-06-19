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

            console.print("\n[bold]AI Analysis:[/bold]")
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
