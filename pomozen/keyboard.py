# pomozen/keyboard.py
import sys
import time

# --- Platform-specific non-blocking key detection ---

_PLATFORM = sys.platform
_IS_WINDOWS = _PLATFORM == "win32"
_IS_LINUX_OR_MAC = _PLATFORM.startswith("linux") or _PLATFORM == "darwin"

if _IS_WINDOWS:
    import msvcrt
elif _IS_LINUX_OR_MAC:
    import select
    import tty
    import termios

    # Store original terminal settings
    _ORIGINAL_TTY_SETTINGS = None
else:
    # Fallback for other platforms (might block or not work)
    try:
        import readchar
    except ImportError:
        print(
            "Warning: 'readchar' not installed. Keyboard controls might be limited on this platform.",
            file=sys.stderr,
        )
        readchar = None


def setup_keyboard():
    """Set up terminal for non-blocking input (Unix/macOS)."""
    if _IS_LINUX_OR_MAC:
        global _ORIGINAL_TTY_SETTINGS
        try:
            _ORIGINAL_TTY_SETTINGS = termios.tcgetattr(sys.stdin)
            # Set terminal to raw mode allows reading byte by byte
            tty.setraw(sys.stdin.fileno())
        except termios.error as e:
            print(
                f"Warning: Could not set terminal to raw mode: {e}. Key controls might not work.",
                file=sys.stderr,
            )
            _ORIGINAL_TTY_SETTINGS = None
        except Exception as e:  # Catch potential issues like stdin not being a tty
            print(
                f"Warning: Could not setup keyboard input: {e}. Key controls might not work.",
                file=sys.stderr,
            )
            _ORIGINAL_TTY_SETTINGS = None


def restore_keyboard():
    """Restore original terminal settings (Unix/macOS)."""
    if _IS_LINUX_OR_MAC and _ORIGINAL_TTY_SETTINGS:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _ORIGINAL_TTY_SETTINGS)
        except termios.error as e:
            print(f"Warning: Could not restore terminal settings: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Error restoring keyboard settings: {e}", file=sys.stderr)


def get_key_if_available() -> str | None:
    """Checks for and returns a key press without blocking. Returns None if no key is pressed."""
    key = None
    if _IS_WINDOWS:
        if msvcrt.kbhit():
            try:
                # Read the byte, decode assuming common encodings or handle potential errors
                key_byte = msvcrt.getch()
                try:
                    key = key_byte.decode("utf-8")
                except UnicodeDecodeError:
                    # Handle potential non-utf8 keys or special keys if needed
                    # For simplicity, we might ignore them or represent them differently
                    # print(f"Debug: Non-UTF8 key byte: {key_byte}")
                    key = None  # Or some placeholder if needed
            except Exception as e:
                # print(f"Debug: Error reading key on Windows: {e}")
                key = None  # Ignore errors for now
    elif _IS_LINUX_OR_MAC:
        # Check if stdin has data ready to be read with a timeout of 0
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            try:
                # Read a single byte in raw mode
                key_byte = sys.stdin.read(1)
                key = key_byte  # In raw mode, it's already a string
                # Handle potential escape sequences for special keys if needed (more complex)
                # e.g., arrow keys might send multiple bytes like '\x1b[A'
                # For basic controls (p, s, q), single bytes are usually sufficient.
                if key == "\x03":  # Handle Ctrl+C explicitly in raw mode
                    raise KeyboardInterrupt
            except Exception as e:
                # print(f"Debug: Error reading key on Unix/Mac: {e}")
                key = None  # Ignore errors
    else:
        # Basic fallback using readchar if available (likely blocks)
        # This path is less ideal for responsive UI
        if readchar:
            # readchar doesn't easily support non-blocking checks across platforms
            # This part remains a limitation without more complex threading
            pass  # Cannot reliably check non-blockingly here with readchar easily

    # Normalize common quit keys
    if key is not None:
        key = key.lower()
        if key == "\x03":  # Ctrl+C might be read differently
            raise KeyboardInterrupt

    return key


# Context manager for setup/restore
class KeyboardManager:
    def __enter__(self):
        setup_keyboard()
        return self  # Not strictly necessary to return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        restore_keyboard()


# --- Example Usage (for testing this module directly) ---
if __name__ == "__main__":
    print("Testing keyboard input for 10 seconds. Press keys (p, s, q, others)...")
    with KeyboardManager():  # Ensure cleanup
        start_time = time.time()
        while time.time() - start_time < 10:
            key = get_key_if_available()
            if key:
                if key == "q":
                    print("\n'q' pressed. Exiting.")
                    break
                # Use carriage return `\r` to overwrite the line
                print(f"Key pressed: '{repr(key)}'   ", end="\r")
            else:
                # Optionally print dots to show it's running
                print(f"Waiting... {time.time() - start_time:.1f}s ", end="\r")

            time.sleep(0.1)  # Small delay to prevent busy-waiting
    print("\nFinished keyboard test.")
