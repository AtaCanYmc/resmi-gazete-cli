import click
from rich.console import Console
from resmi_gazete_cli import __version__

console = Console()


@click.group()
@click.version_option(__version__, "-v", "--version", message="%(prog)s %(version)s")
def cli():
    """T.C. Resmi Gazete CLI aracı."""
    pass


if __name__ == "__main__":
    cli()
