import json
from datetime import time
from pathlib import Path


PREFS_PATH = Path("generated/preferences.json")


DEFAULT_PREFS = {
    "timezone": "Europe/Budapest",
    "default_duration": 30,
    "confidence_threshold": 0.85,
    "working_hours_start": "09:00",
    "working_hours_end": "17:00",
}


def _serialize_time(value):
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    return str(value)


def load_preferences():
    PREFS_PATH.parent.mkdir(exist_ok=True)
    if not PREFS_PATH.exists():
        PREFS_PATH.write_text(json.dumps(DEFAULT_PREFS, indent=2), encoding="utf-8")

    data = json.loads(PREFS_PATH.read_text(encoding="utf-8"))

    start_h, start_m = data.get("working_hours_start", "09:00").split(":")
    end_h, end_m = data.get("working_hours_end", "17:00").split(":")
    data["working_hours_start"] = time(int(start_h), int(start_m))
    data["working_hours_end"] = time(int(end_h), int(end_m))

    return data


def save_preferences(preferences):
    PREFS_PATH.parent.mkdir(exist_ok=True)
    data = {
        "timezone": preferences.get("timezone", DEFAULT_PREFS["timezone"]),
        "default_duration": preferences.get("default_duration", DEFAULT_PREFS["default_duration"]),
        "confidence_threshold": preferences.get("confidence_threshold", DEFAULT_PREFS["confidence_threshold"]),
        "working_hours_start": _serialize_time(preferences.get("working_hours_start", DEFAULT_PREFS["working_hours_start"])),
        "working_hours_end": _serialize_time(preferences.get("working_hours_end", DEFAULT_PREFS["working_hours_end"])),
    }
    PREFS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
