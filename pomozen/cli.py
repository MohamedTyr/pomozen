# pomozen/cli.py
import typer
import sys
from typing_extensions import Annotated
from typing import List

from .config import load_config, get_config_path, create_default_config, update_setting

# Import SessionStatus along with Timer, SessionType
from .timer import Timer, SessionType, SessionStatus
from .display import (
    live_display,
    show_config,
    console,
    show_welcome_banner_and_controls,  # Use new combined banner
    show_session_banner,
    show_completion_status,  # Use new status printer
    show_exit_message,
)
from .keyboard import KeyboardManager  # Import the context manager

from rich.prompt import Confirm

app = typer.Typer(
    name="pomozen",
    help="🧘‍♂️ A 'zen' Pomodoro timer for your terminal, with style! 🍅",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


# --- Helper (Keep as before) ---
def _get_timer() -> Timer:
    config = load_config()
    return Timer(config)


# --- Typer Commands ---


@app.command()
def start(
    auto_continue: Annotated[
        bool,
        typer.Option(
            "--auto",
            "-a",
            help="Automatically continue to the next session without prompting.",
        ),
    ] = False,
):
    """
    Starts the Pomodoro timer sequence with keyboard controls.
    """
    timer = _get_timer()
    show_welcome_banner_and_controls()  # Show banner and controls first

    # Use KeyboardManager to handle setup/restore of terminal
    with KeyboardManager():
        try:
            while True:
                # --- Show banner for the UPCOMING session ---
                current_session_type = timer.current_session_type or SessionType.WORK
                duration_minutes = timer.durations[current_session_type.name.lower()]
                show_session_banner(current_session_type, duration_minutes)

                # --- Run the session with Live display ---
                session_status = (
                    SessionStatus.QUIT
                )  # Default if loop exits unexpectedly
                finished_session_type = (
                    timer.current_session_type or SessionType.WORK
                )  # Store type before run

                with live_display() as progress_live:
                    # Define progress updater callback (exactly as before)
                    def progress_updater(action: str, task_id=None, **kwargs):
                        if action == "add_task":
                            return progress_live.add_task(**kwargs)
                        elif action == "update":
                            if task_id is not None:
                                progress_live.update(task_id, **kwargs)
                        elif action == "remove_task":
                            if task_id is not None:
                                try:
                                    progress_live.remove_task(task_id)
                                except KeyError:
                                    pass
                                except Exception:
                                    pass
                        elif action == "is_finished":
                            if task_id is not None:
                                try:
                                    return progress_live._tasks[task_id].finished
                                except KeyError:
                                    return True
                            return True

                    # Run the session, get the status back
                    session_status = timer.run_session(progress_updater)

                # --- Handle session end based on status ---
                # Show completion/skip status AFTER Live context exits
                show_completion_status(finished_session_type, session_status)

                if session_status == SessionStatus.QUIT:
                    # Exit initiated by 'q' or Ctrl+C within run_session
                    show_exit_message(quit_normally=False)
                    sys.exit(0)  # Exit cleanly

                if session_status == SessionStatus.SKIPPED:
                    # If skipped, move to next session determination immediately
                    # (The next type was already set in timer.py if work was skipped)
                    if finished_session_type != SessionType.WORK:
                        timer.current_session_type = timer._get_next_session_type()

                # --- Ask user if they want to continue (unless auto or skipped) ---
                if session_status == SessionStatus.COMPLETED:
                    next_session_name = timer.current_session_type.name.replace(
                        "_", " "
                    ).capitalize()
                    prompt_text = f"Continue to the next session ({next_session_name})?"

                    if auto_continue or Confirm.ask(
                        f"[bold yellow]{prompt_text}[/]", default=True
                    ):
                        console.print("-" * console.width)  # Separator
                        continue  # Loop to the next session
                    else:
                        show_exit_message(quit_normally=True)
                        break  # Exit the while loop
                else:
                    # If skipped, just add a separator and continue the loop
                    console.print("-" * console.width)  # Separator
                    continue

        except KeyboardInterrupt:
            # Catch Ctrl+C pressed outside the timer loop or re-raised
            console.show_cursor(True)  # Ensure cursor is visible
            print()  # Newline after potentially interrupted output
            show_exit_message(quit_normally=False)
            sys.exit(0)
        except Exception as e:
            console.show_cursor(True)  # Ensure cursor is visible
            console.print_exception(show_locals=False)
            console.print(f"\n[bold red]An unexpected error occurred: {e}[/]")
            sys.exit(1)
        finally:
            # KeyboardManager ensures restore_keyboard() is called on exit
            console.show_cursor(True)  # Belt-and-suspenders


# --- config command (Keep as before) ---
@app.command(name="config")
def config_command(
    create_default: Annotated[
        bool,
        typer.Option(
            "--create-default", help="Create a default config file if it doesn't exist."
        ),
    ] = False,
):
    """Displays the current configuration."""
    config_path = get_config_path()
    if create_default and not config_path.exists():
        create_default_config(config_path)
        console.print("---")
    config = load_config()
    show_config(config)


# --- set command (Keep as before) ---
@app.command(name="set")
def set_command(
    setting_name: Annotated[
        str,
        typer.Argument(help="The config setting (e.g., 'work', 'sound_notification')."),
    ],
    new_value: Annotated[str, typer.Argument(help="The new value for the setting.")],
):
    """Updates a configuration setting and saves it."""
    success, message = update_setting(setting_name, new_value)
    if success:
        console.print(f"[bold green]✔️ {message}[/]")
    else:
        console.print(f"[bold red]❌ Error: {message}[/]")
        sys.exit(1)


# --- Main execution hook (Keep as before) ---
if __name__ == "__main__":
    app()
