# pomozen/timer.py
import time
import sys
from enum import Enum, auto
from typing import Callable, Optional

from .config import APP_CONFIG
from .notifications import send_desktop_notification, play_sound_alert
from .keyboard import get_key_if_available  # Import the keyboard function


# --- Enums for State and Status ---
class SessionType(Enum):
    WORK = auto()
    SHORT_BREAK = auto()
    LONG_BREAK = auto()


class SessionStatus(Enum):
    COMPLETED = auto()
    SKIPPED = auto()
    QUIT = auto()  # Renamed from INTERRUPTED for clarity


class Timer:
    def __init__(self, config: dict):
        self.config = config
        self.durations = config["durations"]
        self.settings = config["settings"]
        self.work_sessions_completed = 0
        self.current_session_type: Optional[SessionType] = None
        self.is_paused: bool = False  # NEW: Pause state flag
        self._task_id = None

    # --- _get_duration (Keep as before) ---
    def _get_duration(self, session_type: SessionType) -> int:
        if session_type == SessionType.WORK:
            minutes = self.durations["work"]
        elif session_type == SessionType.SHORT_BREAK:
            minutes = self.durations["short_break"]
        elif session_type == SessionType.LONG_BREAK:
            minutes = self.durations["long_break"]
        else:
            return 0
        return minutes * 60

    # --- _get_next_session_type (Keep as before) ---
    def _get_next_session_type(self) -> SessionType:
        if self.current_session_type == SessionType.WORK:
            self.work_sessions_completed += 1
            if self.work_sessions_completed % self.settings["long_break_interval"] == 0:
                return SessionType.LONG_BREAK
            else:
                return SessionType.SHORT_BREAK
        else:
            return SessionType.WORK

    def run_session(
        self, progress_updater: Callable
    ) -> SessionStatus:  # Return SessionStatus
        """Runs a single Pomodoro session with live display and keyboard controls."""
        if self.current_session_type is None:
            self.current_session_type = SessionType.WORK

        session_name = self.current_session_type.name.replace("_", " ").capitalize()
        duration_sec = self._get_duration(self.current_session_type)
        elapsed_sec = 0
        self.is_paused = False  # Ensure not paused at start of session

        # Determine colors/styles
        if self.current_session_type == SessionType.WORK:
            progress_color = "[bold red]"
            finished_color = "[bold bright_red]"
        else:  # Breaks
            progress_color = "[bold blue]"
            finished_color = "[bold bright_blue]"

        desc_base = f"{progress_color}{session_name}"

        # Add task to Rich Progress
        self._task_id = progress_updater(
            "add_task",
            description=desc_base,
            total=duration_sec,
            completed=elapsed_sec,  # Start at 0
            remaining_text=f"{duration_sec // 60:02d}:00",
        )

        # --- Main Timer Loop ---
        try:
            while elapsed_sec < duration_sec:
                # --- Check for Keyboard Input ---
                key = get_key_if_available()
                if key:
                    if key == "p":
                        self.is_paused = not self.is_paused
                        # print(f"\rDEBUG: Paused state: {self.is_paused}   ") # Debug line
                    elif key == "s":
                        # print("\rDEBUG: Skip key pressed.") # Debug line
                        return SessionStatus.SKIPPED  # Exit loop and signal skip
                    elif key == "q":
                        # print("\rDEBUG: Quit key pressed.") # Debug line
                        # Raise KeyboardInterrupt to be caught by the outer handler in cli.py
                        raise KeyboardInterrupt("Quit requested by user")

                # --- Handle Pause State ---
                if self.is_paused:
                    progress_updater(
                        "update",
                        self._task_id,
                        description=f"{desc_base} [yellow](Paused)",  # Show paused status
                        # Do not advance time
                    )
                    time.sleep(0.2)  # Sleep briefly to avoid busy-waiting while paused
                    continue  # Skip the rest of the loop iteration

                # --- Update Progress (if not paused) ---
                elapsed_sec += 1
                progress_updater(
                    "update",
                    self._task_id,
                    advance=1,
                    description=desc_base,  # Reset description if resuming
                )
                time.sleep(1)

            # --- Session Finished Normally ---
            progress_updater(
                "update",
                self._task_id,
                description=f"{finished_color}{session_name} Complete!",
                remaining_text="Done!",
            )
            time.sleep(0.5)  # Keep final state visible briefly

            # Send Notifications (only on normal completion)
            send_desktop_notification(
                f"PomoZen: {session_name} Finished!", "Time for the next session!"
            )
            play_sound_alert(session_name)

            # Determine the type for the *next* session
            self.current_session_type = self._get_next_session_type()
            return SessionStatus.COMPLETED

        except KeyboardInterrupt:
            # This is now primarily caught by the cli.py handler
            # We just need to ensure the timer loop exits
            return SessionStatus.QUIT  # Signal that quit was initiated

        # Note: `finally` block removed as cleanup (like title reset) is removed or handled elsewhere
