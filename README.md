# PomoZen 🧘‍♂️🍅

**A stylish and functional Pomodoro timer for your terminal, designed to bring focus and zen to your workflow.**

[![PomoZen Demo GIF](https://raw.githubusercontent.com/your-username/pomozen/main/docs/pomozen-demo.gif)](https://github.com/your-username/pomozen)
_(Replace the link above with an actual GIF demonstrating the UI!)_

PomoZen leverages the power of Python and the [Rich](https://github.com/Textualize/rich) library to provide a visually engaging, interactive, and customizable Pomodoro experience directly in your command line. Say goodbye to distracting browser tabs or clunky desktop apps – keep your focus sharp where you work.

## ✨ Key Features

- **Classic Pomodoro Technique:** Implements standard work/short break/long break cycles.
- **Dynamic & Engaging UI:** Built with [Rich](https://github.com/Textualize/rich) for:
  - Live-updating progress bars with remaining time (MM:SS).
  - Styled panels and banners for session transitions.
  - Clean status updates that replace finished timers, avoiding clutter.
  - Emoji support for visual cues (💪, ☕, 🧘‍♀️, ✨, 🎉).
- **Interactive Keyboard Controls:**
  - `p` : Pause / Resume the current timer.
  - `s` : Skip the current session (work or break).
  - `q` / `Ctrl+C`: Quit the application gracefully.
  - Non-blocking input ensures UI responsiveness.
- **Customizable Sessions:** Configure durations for work, short breaks, and long breaks.
- **Configurable Long Break Interval:** Set how many work sessions trigger a longer break.
- **Cross-Platform Desktop Notifications:** Uses [Plyer](https://github.com/kivy/plyer) to send native notifications when sessions end (requires platform support).
- **(Optional) Sound Notifications:** Uses [Playsound](https://github.com/TaylorSMarks/playsound) for audio cues (requires setup & compatible backend).
- **Persistent Configuration:**
  - Settings saved to a user-specific `config.toml` file.
  - Modify settings easily via the `pomozen set` command or by editing the file.
- **Clean CLI Interface:** Powered by [Typer](https://github.com/tiangolo/typer) for intuitive commands and auto-generated help.

## ⚙️ Installation

**Prerequisites:**

1.  **Python:** Version 3.8 or higher is recommended.
2.  **pip:** Python's package installer (usually comes with Python).
3.  **(Potentially) System Libraries for Dependencies:** See notes below for `Plyer` and `Playsound`.

**Steps:**

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/your-username/pomozen.git
    cd pomozen
    ```

    _(Replace `your-username` with your actual GitHub username)_

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv .venv
    # Activate it:
    # Windows (Command Prompt): .venv\Scripts\activate.bat
    # Windows (PowerShell):   .venv\Scripts\Activate.ps1
    # macOS/Linux (bash/zsh): source .venv/bin/activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    **Dependency Notes:**

    - **`toml`:** Mandatory for reading and _saving_ configuration via the `set` command.
    - **`Plyer`:** For desktop notifications. May require additional system packages depending on your OS for notification backend support (e.g., `dbus-python` or `notify-python` on some Linux systems). Consult the [Plyer documentation](https://plyer.readthedocs.io/en/latest/installation.html#installation-per-platform) if notifications don't work.
    - **`Playsound`:** For optional sound alerts. This library can be tricky:
      - It requires system backends (e.g., GStreamer on Linux, AppKit on macOS, MCI on Windows).
      - **Linux:** You might need packages like `python3-gi`, `gir1.2-gstreamer-1.0`, `gstreamer1.0-plugins-base`, `gstreamer1.0-plugins-good`. Example (Debian/Ubuntu):
      ```bash
      sudo apt update && sudo apt install python3-gi gir1.2-gstreamer-1.0 gstreamer1.0-plugins-good
      ```
      - Version `1.2.2` is used as `1.3.0` has known build issues on some systems.
      - Sound is **disabled by default** in the configuration.

4.  **(Optional) Editable Install for Development:**
    If you plan to modify the code, install it in editable mode:
    ```bash
    pip install -e .
    ```
    This links the installed package directly to your source code.

## 🔧 Configuration

PomoZen uses a `config.toml` file to store your preferences. It looks for this file in a standard user configuration directory:

- **Linux:** `~/.config/pomozen/config.toml` (or `$XDG_CONFIG_HOME/pomozen/config.toml`)
- **macOS:** `~/Library/Application Support/pomozen/config.toml`
- **Windows:** `%APPDATA%\pomozen\config.toml` (e.g., `C:\Users\YourUser\AppData\Roaming\pomozen\config.toml`)

**Creating the Configuration File:**

You have two options:

1.  **Automatic Generation:** Run `pomozen config --create-default`. This will create the necessary directories and populate `config.toml` with default values.
2.  **Manual Creation:** Copy the `config.example.toml` file from this repository to the correct location listed above and rename it to `config.toml`.

**Editing Settings:**

You can modify settings in two ways:

1.  **Using the `set` command:** This is the recommended way for quick changes.

    ```bash
    pomozen set <setting_name> <new_value>
    ```

    - **Example:** `pomozen set work 30` (Sets work duration to 30 minutes)
    - **Example:** `pomozen set sound_notification true` (Enables sound alerts)

2.  **Editing `config.toml` directly:** Open the file in a text editor.

**Default Configuration (`config.toml`):**

```toml
# Default PomoZen Configuration

[durations]
# Session durations in minutes
work = 25
short_break = 5
long_break = 15

[settings]
# Number of work sessions before a long break is triggered
long_break_interval = 4

# Enable sound notifications (true/false)
# Requires 'playsound' package and system dependencies!
sound_notification = false
```
