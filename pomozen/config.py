# pomozen/config.py
import os
import sys
from pathlib import Path
import importlib
from typing import Dict, Any, Tuple, Optional

# --- TOML Handling ---
# Use built-in tomllib for reading if available (3.11+)
try:
    import tomllib
except ModuleNotFoundError:
    # Fallback to 'toml' package for reading if tomllib not present
    try:
        import toml as tomllib
    except ModuleNotFoundError:
        print(
            "Error: 'toml' package is required. Please install it (`pip install toml`)"
        )
        sys.exit(1)

# Use 'toml' package for writing (mandatory requirement now)
try:
    import toml
except ModuleNotFoundError:
    print(
        "Error: 'toml' package is required for saving configuration. Please install it (`pip install toml`)"
    )
    sys.exit(1)


# --- Configuration Defaults --- (Keep as before)
DEFAULT_CONFIG: Dict[str, Any] = {
    "durations": {
        "work": 25,
        "short_break": 5,
        "long_break": 15,
    },
    "settings": {
        "long_break_interval": 4,
        "sound_notification": False,
    },
}


# --- Configuration Path --- (Keep as before)
def get_config_path() -> Path:
    """Determines the platform-specific configuration path."""
    if sys.platform == "win32":
        config_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    elif sys.platform == "darwin":
        config_dir = Path.home() / "Library/Application Support"
    else:  # Assume Linux/Unix-like
        config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    return config_dir / "pomozen" / "config.toml"


# --- Load Configuration --- (Keep mostly as before, but use tomllib consistently)
def load_config() -> Dict[str, Any]:
    """Loads configuration from file, merging with defaults."""
    config_path = get_config_path()
    # Start with a deep copy of defaults to avoid modifying the original
    config = {
        k: v.copy() if isinstance(v, dict) else v for k, v in DEFAULT_CONFIG.items()
    }

    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                user_config = tomllib.load(f)  # Use tomllib (or its alias)

            # Deep merge user config into defaults
            for section, settings in user_config.items():
                if section in config and isinstance(config[section], dict):
                    config[section].update(settings)
                else:
                    config[section] = settings
        except Exception as e:
            print(
                f"Warning: Could not load config file at {config_path}. Using defaults. Error: {e}",
                file=sys.stderr,
            )

    # --- Validation (Keep as before) ---
    # durations
    for key, value in config.get("durations", {}).items():
        if not isinstance(value, int) or value <= 0:
            print(
                f"Warning: Invalid duration '{value}' for '{key}' in config. Using default.",
                file=sys.stderr,
            )
            config["durations"][key] = DEFAULT_CONFIG["durations"].get(key, 1)
    # long_break_interval
    interval = config.get("settings", {}).get("long_break_interval", 4)
    if not isinstance(interval, int) or interval <= 0:
        print(
            f"Warning: Invalid long_break_interval '{interval}' in config. Using default.",
            file=sys.stderr,
        )
        config["settings"]["long_break_interval"] = DEFAULT_CONFIG["settings"][
            "long_break_interval"
        ]
    # sound_notification (ensure boolean)
    sound = config.get("settings", {}).get("sound_notification", False)
    if not isinstance(sound, bool):
        print(
            f"Warning: Invalid sound_notification '{sound}' in config (should be true/false). Using default.",
            file=sys.stderr,
        )
        config["settings"]["sound_notification"] = DEFAULT_CONFIG["settings"][
            "sound_notification"
        ]

    return config


# --- Save Configuration --- (New Function)
def save_config(config_data: Dict[str, Any]) -> bool:
    """Saves the configuration dictionary to the config file."""
    config_path = get_config_path()
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            toml.dump(config_data, f)
        return True
    except OSError as e:
        print(
            f"Error: Could not write config file to {config_path}: {e}", file=sys.stderr
        )
        return False
    except Exception as e:
        print(f"An unexpected error occurred while saving config: {e}", file=sys.stderr)
        return False


# --- Update Setting --- (New Function)
def update_setting(setting_name: str, new_value_str: str) -> Tuple[bool, str]:
    """Loads config, updates a specific setting, validates, and saves."""
    config_data = load_config()
    original_setting_name = setting_name  # Keep original for messages
    setting_name = setting_name.lower()  # Work with lowercase internally

    target_section: Optional[Dict] = None
    target_key: Optional[str] = None
    is_boolean_setting = False

    # Find where the setting lives
    if setting_name in config_data.get("durations", {}):
        target_section = config_data["durations"]
        target_key = setting_name
    elif setting_name in config_data.get("settings", {}):
        target_section = config_data["settings"]
        target_key = setting_name
        # Check if this specific setting should be boolean
        if setting_name == "sound_notification":
            is_boolean_setting = True
    else:
        valid_keys = list(config_data.get("durations", {}).keys()) + list(
            config_data.get("settings", {}).keys()
        )
        return (
            False,
            f"Invalid setting name '{original_setting_name}'. Valid settings are: {', '.join(valid_keys)}",
        )

    # Validate and parse the new value
    new_value: Any = None
    if is_boolean_setting:
        lowered_value = new_value_str.lower()
        if lowered_value in ["true", "yes", "1", "on"]:
            new_value = True
        elif lowered_value in ["false", "no", "0", "off"]:
            new_value = False
        else:
            return (
                False,
                f"Invalid boolean value '{new_value_str}'. Use true/false, yes/no, 1/0.",
            )
    else:  # Assume integer for durations and interval
        try:
            new_value = int(new_value_str)
            if new_value <= 0:
                return (
                    False,
                    f"Value for '{original_setting_name}' must be a positive number.",
                )
        except ValueError:
            return (
                False,
                f"Invalid numeric value '{new_value_str}' for '{original_setting_name}'.",
            )

    # Update the dictionary
    if target_section is not None and target_key is not None:
        target_section[target_key] = new_value
    else:
        # Should not happen if logic above is correct, but safeguard
        return False, "Internal error: Could not find target location for setting."

    # Save the updated config
    if save_config(config_data):
        return True, f"Successfully updated '{original_setting_name}' to '{new_value}'."
    else:
        return False, "Failed to save the updated configuration."


# --- Create Default Config (Keep as before, but maybe use save_config?) ---
def create_default_config(config_path: Path):
    """Creates the config directory and saves the default config file."""
    # Use the save_config function for consistency
    print(f"Creating default configuration file at: {config_path}")
    if not save_config(DEFAULT_CONFIG):
        print(
            "Error: Failed to create the default configuration file.", file=sys.stderr
        )


# --- Load config on module import --- (Keep as before)
APP_CONFIG = load_config()

# --- Main block for testing --- (Update to test new functions)
if __name__ == "__main__":
    print("--- Initial Loaded Configuration ---")
    show_config(APP_CONFIG)  # Assuming show_config is defined elsewhere or imported

    print("\n--- Testing Updates ---")
    success, msg = update_setting("work", "30")
    print(f"Set 'work' to 30: {'Success' if success else 'Failed'} - {msg}")

    success, msg = update_setting("sound_notification", "true")
    print(
        f"Set 'sound_notification' to true: {'Success' if success else 'Failed'} - {msg}"
    )

    success, msg = update_setting("long_break", "invalid")
    print(
        f"Set 'long_break' to 'invalid': {'Success' if success else 'Failed'} - {msg}"
    )

    success, msg = update_setting("non_existent", "10")
    print(f"Set 'non_existent' to 10: {'Success' if success else 'Failed'} - {msg}")

    print("\n--- Configuration After Updates (Reloaded) ---")
    reloaded_config = load_config()
    show_config(
        reloaded_config
    )  # You'd need to import show_config from display for this test

    # print("\nConfig file path:", get_config_path())
    # create_default_config(get_config_path()) # Test creation
