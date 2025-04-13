# pomozen/display.py
import time
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.text import Text
from rich.console import Console
from rich.table import Table
from rich.align import Align
from contextlib import contextmanager
from typing import Generator, Optional

# Import SessionType and SessionStatus if needed for type hints
from .timer import SessionType, SessionStatus

console = Console()

# --- ASCII Art --- (Keep as before)
TITLE_ART = """
   ▄███████▄  ▄██████▄    ▄▄▄▄███▄▄▄▄    ▄██████▄   ▄███████▄     ▄████████ ███▄▄▄▄   
  ███    ███ ███    ███ ▄██▀▀▀███▀▀▀██▄ ███    ███ ██▀     ▄██   ███    ███ ███▀▀▀██▄ 
  ███    ███ ███    ███ ███   ███   ███ ███    ███       ▄███▀   ███    █▀  ███   ███ 
  ███    ███ ███    ███ ███   ███   ███ ███    ███  ▀█▀▄███▀▄▄  ▄███▄▄▄     ███   ███ 
▀█████████▀  ███    ███ ███   ███   ███ ███    ███   ▄███▀   ▀ ▀▀███▀▀▀     ███   ███ 
  ███        ███    ███ ███   ███   ███ ███    ███ ▄███▀         ███    █▄  ███   ███ 
  ███        ███    ███ ███   ███   ███ ███    ███ ███▄     ▄█   ███    ███ ███   ███ 
 ▄████▀       ▀██████▀   ▀█   ███   █▀   ▀██████▀   ▀████████▀   ██████████  ▀█   █▀  
"""

# --- Keyboard Controls Help Text ---
CONTROLS_TEXT = "[bold yellow]Controls:[/]\n  [cyan]p[/] - Pause/Resume\n  [cyan]s[/] - Skip Session\n  [cyan]q[/] / [cyan]Ctrl+C[/] - Quit"


# --- Progress Bar Setup --- (Keep TimeRemainingColumn, update Progress slightly)
class TimeRemainingColumn(TextColumn):
    def render(self, task) -> Text:
        if task.total is None or task.completed is None:
            return Text("??:??", style="progress.remaining")
        remaining = task.total - task.completed
        minutes, seconds = divmod(int(remaining), 60)
        return Text(
            f"{minutes:02d}:{seconds:02d}", style="bold yellow"
        )  # Style time directly


progress = Progress(
    SpinnerColumn(spinner_name="dots", style="progress.spinner"),
    TextColumn(
        "[progress.description]{task.description}"
    ),  # Description set dynamically
    BarColumn(
        bar_width=None,
        complete_style="green",
        finished_style="bright_blue",
        pulse_style="yellow",
    ),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeRemainingColumn(
        "Remaining: {task.fields[remaining_text]}"
    ),  # Keep custom field name if needed by timer.py
    expand=True,
)

# --- Display Functions ---


def show_welcome_banner_and_controls():
    """Displays the stylized welcome banner and keyboard controls."""
    console.print(
        Panel(
            Align.center(Text(TITLE_ART, style="bold bright_magenta")),
            title="Welcome",
            border_style="magenta",
            padding=(1, 2),
        )
    )
    console.print(
        Align.center(
            Text("🧘‍♂️  Your focused time starts now... 🍅", style="italic cyan")
        )
    )
    console.print()
    console.print(
        Panel(CONTROLS_TEXT, title="Controls", border_style="yellow", padding=(0, 1))
    )
    console.print()  # Add spacing before the first session banner


def show_session_banner(session_type: SessionType, duration_minutes: int):
    """Displays a banner indicating the start of a new session."""
    session_name = session_type.name.replace("_", " ").capitalize()
    # (Keep the logic for emoji, panel_title, border_color, message as before)
    if session_type == SessionType.WORK:
        emoji = "💪"
        panel_title = "[bold red]Work Session[/]"
        border_color = "red"
        message_text = (
            f"Focus! Time for a {duration_minutes}-minute work session. {emoji}"
        )
    elif session_type == SessionType.SHORT_BREAK:
        emoji = "☕"
        panel_title = "[bold blue]Short Break[/]"
        border_color = "blue"
        message_text = f"Relax! Take a {duration_minutes}-minute short break. {emoji}"
    else:  # Long Break
        emoji = "🧘‍♀️"
        panel_title = "[bold green]Long Break[/]"
        border_color = "green"
        message_text = (
            f"Well deserved! Enjoy a {duration_minutes}-minute long break. {emoji}"
        )

    # Use Align.center for the text within the panel
    console.print(
        Panel(
            Align.center(
                Text(message_text, style="bold")
            ),  # Pass raw text, let Panel/Align handle style/justify
            title=panel_title,
            border_style=border_color,
            padding=(1, 1),
        )
    )
    console.print()  # Spacer


def show_completion_status(session_type: SessionType, status: SessionStatus):
    """Prints a status line after a session ends (replaces progress bar)."""
    session_name = session_type.name.replace("_", " ").capitalize()
    if status == SessionStatus.COMPLETED:
        console.print(f"[bold green] ✓ [/] [green]{session_name} completed![/]")
    elif status == SessionStatus.SKIPPED:
        console.print(f"[bold yellow] » [/] [yellow]{session_name} skipped.[/]")
    elif status == SessionStatus.QUIT:
        # The exit message will be handled by the main loop's exception handler
        pass
    console.print()  # Add spacing before next banner or prompt


def show_exit_message(quit_normally: bool = True):
    """Displays a styled exit message."""
    if quit_normally:
        message = Text(
            "🍅 PomoZen stopped. Keep up the great work! 🧘‍♂️",
            style="bold cyan",
            justify="center",
        )
        title = "Goodbye!"
        border = "cyan"
    else:  # Interrupted (Ctrl+C / q)
        message = Text("🛑 PomoZen interrupted.", style="bold yellow", justify="center")
        title = "Interrupted"
        border = "yellow"

    console.print(Panel(message, title=title, border_style=border, padding=(1, 2)))


# --- Config Display (Keep Table version as before) ---
def show_config(config: dict):
    table = Table(
        title="PomoZen Configuration",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
    )
    table.add_column("Setting", style="dim", width=25)
    table.add_column("Value", style="bold")
    # Durations
    table.add_row("[green]Durations[/]", "")
    for key, value in config.get("durations", {}).items():
        table.add_row(f"  - {key.replace('_', ' ').capitalize()} (min)", str(value))
    # Settings
    table.add_section()
    table.add_row("[green]Settings[/]", "")
    for key, value in config.get("settings", {}).items():
        table.add_row(f"  - {key.replace('_', ' ').capitalize()}", str(value))
    console.print(table)
    from .config import get_config_path

    console.print(f"\n[dim]Config file location: {get_config_path()}[/dim]\n")


# --- Live Display Context --- (Update to use transient=True)
@contextmanager
def live_display() -> Generator[Progress, None, None]:
    """Manages the Rich Live display context (progress bar is transient)."""
    # Start Live with transient=True so the progress bar disappears on exit
    with Live(
        progress,
        console=console,
        refresh_per_second=4,
        vertical_overflow="visible",
        transient=True,
    ) as live:
        try:
            yield progress
        finally:
            # No need to explicitly stop or clear, transient handles the progress bar.
            # Ensure cursor is visible though, Live might hide it.
            console.show_cursor(True)
