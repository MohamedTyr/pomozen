# pomozen/notifications.py
import sys
from typing import Optional
from .config import APP_CONFIG  # Use loaded config

# --- Conditional import for Plyer ---
try:
    from plyer import notification as plyer_notification

    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print(
        "Warning: 'plyer' package not found. Desktop notifications disabled.",
        file=sys.stderr,
    )
    print("Install it with: pip install plyer", file=sys.stderr)
except Exception as e:  # Catch potential platform-specific import errors within plyer
    PLYER_AVAILABLE = False
    print(f"Warning: Could not initialize Plyer notifications. {e}", file=sys.stderr)

# --- Conditional import for Playsound (Optional) ---
PLAYSOUND_AVAILABLE = False
if APP_CONFIG.get("settings", {}).get("sound_notification", False):
    try:
        # Note: playsound can have cross-platform issues and dependencies (like GStreamer on Linux)
        # Consider alternatives or making installation instructions very clear if using sound.
        from playsound import playsound

        PLAYSOUND_AVAILABLE = True
        # SOUND_FILE_WORK = "path/to/work_done.wav"
        # SOUND_FILE_BREAK = "path/to/break_done.wav"
    except ImportError:
        print(
            "Warning: 'playsound' package not found, but sound notifications are enabled in config.",
            file=sys.stderr,
        )
        print("Install it with: pip install playsound", file=sys.stderr)
    except Exception as e:
        print(
            f"Warning: Could not initialize Playsound. Sound disabled. {e}",
            file=sys.stderr,
        )


def send_desktop_notification(title: str, message: str):
    """Sends a desktop notification if plyer is available."""
    if not PLYER_AVAILABLE:
        # print(f"Notification (plyer unavailable): {title} - {message}") # Fallback
        return

    try:
        plyer_notification.notify(
            title=title,
            message=message,
            app_name="PomoZen",
            # timeout=10 # Notification duration in seconds
        )
    except NotImplementedError:
        print(
            f"Warning: Desktop notifications not supported on this platform by plyer.",
            file=sys.stderr,
        )
    except Exception as e:
        # Catch other potential errors during notification sending
        print(f"Error sending notification: {e}", file=sys.stderr)


def play_sound_alert(session_type: str):
    """Plays a sound alert based on session type if enabled and available."""
    if not APP_CONFIG.get("settings", {}).get("sound_notification", False):
        return
    if not PLAYSOUND_AVAILABLE:
        print(
            f"Sound Alert (playsound unavailable): {session_type} finished."
        )  # Fallback
        return

    # This part needs refinement based on actual sound files
    print(f"Playing sound for: {session_type}")  # Placeholder
    # try:
    #     if session_type == "Work":
    #         playsound(SOUND_FILE_WORK)
    #     else: # Break or Long Break
    #         playsound(SOUND_FILE_BREAK)
    # except Exception as e:
    #     print(f"Error playing sound: {e}", file=sys.stderr)


if __name__ == "__main__":
    print("Testing Notifications...")
    print(f"Plyer Available: {PLYER_AVAILABLE}")
    print(f"Playsound Available: {PLAYSOUND_AVAILABLE}")
    print(
        f"Sound Enabled in Config: {APP_CONFIG.get('settings', {}).get('sound_notification', False)}"
    )

    if PLYER_AVAILABLE:
        send_desktop_notification("PomoZen Test", "This is a test notification.")
        print("Desktop notification sent (check your system).")
    else:
        print("Skipping desktop notification test (plyer unavailable).")

    if PLAYSOUND_AVAILABLE and APP_CONFIG.get("settings", {}).get(
        "sound_notification", False
    ):
        print("Attempting to play 'Work' sound (requires sound file setup)...")
        play_sound_alert("Work")
    else:
        print("Skipping sound test (playsound unavailable or disabled).")
