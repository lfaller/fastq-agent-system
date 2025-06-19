"""Command line interface for FASTQ Agent System."""

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="FASTQ Agent System - Multi-agent FASTQ file analysis")
console = Console()


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
