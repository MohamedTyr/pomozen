# PomoZen 🧘‍♂️🍅

**A stylish and effective Pomodoro timer for your terminal.**

PomoZen helps you manage focus and work/break cycles using the Pomodoro Technique, right from your command line. It provides clear visual feedback and simple controls without leaving your terminal.

## ![Pomozen User Interface](images/ui.png)

## Features

- **Classic Pomodoro:** Standard work, short break, and long break sessions.
- **Clear Terminal UI:** Live progress bar, session banners, and clean status updates.
- **Interactive Controls:** Pause/Resume (`p`), Skip Session (`s`), Quit (`q`/`Ctrl+C`).
- **Customizable Timers:** Set durations via a config file or command.
- **Desktop Notifications:** Optional alerts when sessions end.
- **Sound Alerts:** Optional audio cues (requires extra setup).

---

## Installation

**Prerequisites:**

- Python 3.8+
- `pip` (Python package installer)

**Steps:**

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MohamedTyr/pomozen
    cd pomozen
    ```

2.  **Create & Activate Virtual Environment (Recommended):**

    ```bash
    python -m venv .venv
    # Windows: .venv\Scripts\activate  (cmd) or .venv\Scripts\Activate.ps1 (PowerShell)
    # macOS/Linux: source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    - _Note:_ Desktop/sound notifications (`Plyer`/`Playsound`) might need extra system libraries (like GStreamer on Linux). See their documentation if needed. Sound is disabled by default.

---

## Configuration

Settings are stored in `config.toml`.

**Location:**

- **Linux:** `~/.config/pomozen/config.toml`
- **macOS:** `~/Library/Application Support/pomozen/config.toml`
- **Windows:** `%APPDATA%\pomozen\config.toml`

**How to Configure:**

1.  **Use the `set` command (Recommended):**

    ```bash
    # Example: Set work time to 30 minutes
    pomozen set work 30

    # Example: Enable sound notifications
    pomozen set sound_notification true
    ```

    - Valid settings: `work`, `short_break`, `long_break`, `long_break_interval`, `sound_notification`.

2.  **Edit the `config.toml` file:**
    - Create the file if it doesn't exist (or run `pomozen config --create-default`).
    - Edit with a text editor.

**Default Settings (`config.toml`):**

```toml
[durations]
# Session times in minutes
work = 25
short_break = 5
long_break = 15

[settings]
# Work sessions before a long break
long_break_interval = 4
# Enable sound (true/false) - Needs setup!
sound_notification = false
```

---

## Usage

**Run the Timer:**

```bash
# From the project directory
python -m pomozen start

# Or if installed (e.g., via `pip install .`)
pomozen start
```

**Timer Controls (Press key during session):**

- `p` : Pause / Resume
- `s` : Skip current session
- `q` or `Ctrl+C` : Quit PomoZen

**Other Commands:**

- `pomozen start -a`: Start timer and automatically continue sessions.
- `pomozen config`: Show current settings and config file location.
- `pomozen config --create-default`: Create a default config file.
- `pomozen set <setting> <value>`: Change a setting (e.g., `pomozen set short_break 7`).

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
