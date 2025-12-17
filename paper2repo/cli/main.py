"""Command-line interface for Paper2Repo."""
import sys
import logging
from pathlib import Path

# Try to import optional dependencies
try:
    import click
    from rich.console import Console
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    click = None

from paper2repo import __version__
from paper2repo.workflows.pipeline_orchestrator import PipelineOrchestrator

# Setup logging
if RICH_AVAILABLE:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    console = Console()
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console = None

logger = logging.getLogger(__name__)


def print_message(message: str, style: str = ""):
    """Print message with optional rich styling."""
    if RICH_AVAILABLE and console:
        console.print(message, style=style)
    else:
        print(message)


def cli_main():
    """Main CLI entry point (no dependencies)."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Paper2Repo - Transform research papers into code repositories"
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    parser.add_argument(
        '--help-full',
        action='store_true',
        help='Show full help including optional features'
    )
    
    args = parser.parse_args()
    
    if args.version:
        print(f"Paper2Repo v{__version__}")
        return 0
    
    if args.help_full:
        print(f"""Paper2Repo v{__version__}

A multi-agent system for transforming research papers into production-ready code.

Usage:
    python main.py --version                  Show version
    python main.py version                    Show version (if click installed)
    
Optional Features (require additional dependencies):
    - CLI commands: Install with 'pip install paper2repo[cli]'
    - Web UI: Install with 'pip install paper2repo[ui]'
    - PDF support: Install with 'pip install paper2repo[pdf]'

For full functionality:
    pip install 'paper2repo[all]'
""")
        return 0
    
    # Default: show basic help
    parser.print_help()
    return 0


if click and RICH_AVAILABLE:
    # Rich CLI with click
    @click.group()
    @click.version_option(version=__version__, prog_name="Paper2Repo")
    def cli():
        """Paper2Repo - Transform research papers into code repositories."""
        pass
    
    @cli.command()
    def version():
        """Show version information."""
        print_message(f"[bold green]Paper2Repo v{__version__}[/bold green]")
    
    @cli.command()
    @click.argument('paper_path', type=click.Path(exists=True))
    @click.option('--output', '-o', default='./output', help='Output directory')
    @click.option('--user-input', '-u', help='Additional user requirements')
    def generate(paper_path: str, output: str, user_input: str):
        """Generate code repository from research paper.
        
        PAPER_PATH: Path to research paper (PDF or text file)
        """
        print_message(f"[bold]Paper2Repo v{__version__}[/bold]", style="blue")
        print_message(f"Processing paper: {paper_path}")
        
        try:
            # Initialize pipeline
            pipeline = PipelineOrchestrator(
                output_dir=Path(output)
            )
            
            # Prepare input
            input_data = {
                'document_path': paper_path,
                'user_input': user_input or f"Generate code from {paper_path}"
            }
            
            # Run pipeline
            print_message("Starting pipeline...", style="yellow")
            results = pipeline.run(input_data)
            
            if results['success']:
                print_message(
                    f"[bold green]✓[/bold green] Code generated successfully!",
                    style="green"
                )
                print_message(f"Output directory: {pipeline.get_output_directory()}")
            else:
                print_message(
                    f"[bold red]✗[/bold red] Pipeline failed",
                    style="red"
                )
                for error in results.get('errors', []):
                    print_message(f"  Error: {error}", style="red")
            
        except Exception as e:
            print_message(f"[bold red]Error:[/bold red] {e}", style="red")
            logger.exception("Pipeline execution failed")
            sys.exit(1)
    
    @cli.command()
    def info():
        """Show system information."""
        print_message("[bold]Paper2Repo System Information[/bold]")
        print_message(f"Version: {__version__}")
        print_message(f"Python: {sys.version}")
        
        # Check optional dependencies
        deps = {
            'click': click is not None,
            'rich': RICH_AVAILABLE,
            'streamlit': False,
            'pymupdf': False
        }
        
        try:
            import streamlit
            deps['streamlit'] = True
        except ImportError:
            pass
        
        try:
            import fitz
            deps['pymupdf'] = True
        except ImportError:
            pass
        
        print_message("\n[bold]Optional Dependencies:[/bold]")
        for name, available in deps.items():
            status = "[green]✓[/green]" if available else "[red]✗[/red]"
            print_message(f"  {status} {name}")
    
    def main():
        """Main entry point with click."""
        cli()
else:
    # Fallback without click
    def main():
        """Main entry point without click."""
        sys.exit(cli_main())


if __name__ == '__main__':
    main()
