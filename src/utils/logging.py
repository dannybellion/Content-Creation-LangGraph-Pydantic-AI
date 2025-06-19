import logging
import json
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich.traceback import install
from rich.panel import Panel
from rich.pretty import Pretty
from pydantic import BaseModel

# Install rich traceback handler
install(show_locals=True)

# Create a custom theme for our logs
custom_theme = Theme(
    {
        "info": "bold cyan",
        "warning": "bold yellow",
        "error": "bold red",
        "critical": "bold white on red",
    }
)

# Create console with our theme
console = Console(theme=custom_theme)

# Configure the rich handler
rich_handler = RichHandler(
    console=console,
    rich_tracebacks=True,
    tracebacks_show_locals=True,
    markup=True,
)


# Configure the logging
def configure_logging(level=logging.INFO, logger_name="redlite"):
    """Configure logging with Rich formatting"""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler],
    )

    # Return a logger instance
    return logging.getLogger(logger_name)


# Create a default logger instance
logger = configure_logging()


def log_object(
    title: str,
    object: BaseModel = None,
    subtitle: str = "",
    border_color: str = "dim magenta",
):
    """Logs the final agent result using a rich Panel and Pretty.

    Args:
        title: The title for the panel (e.g., Agent Name).
        result_obj: The Pydantic BaseModel object returned by the agent.
        border_color: The color for the panel border.
    """
    panel = Panel(
        Pretty(object),
        title=f"[bold magenta]{title} Result[/bold magenta]",
        subtitle=subtitle,
        border_style=border_color,
        expand=False,
    )
    console.print(panel)


def log_data(label: str, data: Any):
    """
    Log a data object with nice formatting.

    Args:
        label (str): Label for the data
        data (Any): Data to log
    """
    if isinstance(data, (dict, list)):
        console.print(f"[bold blue]{label}:[/bold blue]")
        console.print(Pretty(data))
    elif isinstance(data, str) and (
        data.startswith("{") or data.startswith("[")
    ):
        # Try to parse JSON strings
        try:
            parsed = json.loads(data)
            console.print(f"[bold blue]{label}:[/bold blue]")
            console.print(Pretty(parsed))
        except json.JSONDecodeError:  # Catch specific error
            console.print(f"[bold blue]{label}:[/bold blue] {data}")
    else:
        console.print(f"[bold blue]{label}:[/bold blue] {data}")
