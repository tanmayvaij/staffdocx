import json
import os
from pathlib import Path

SETTINGS_FILE = Path("settings.json")

def load_settings() -> dict:
    """Load settings from the JSON file."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def save_settings(settings: dict) -> None:
    """Save settings to the JSON file."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def get_setting(key: str, default=None):
    """Retrieve a specific setting."""
    settings = load_settings()
    return settings.get(key, default)

def set_setting(key: str, value) -> None:
    """Update a specific setting."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
