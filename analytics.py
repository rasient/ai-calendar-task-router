import json
from pathlib import Path


ANALYTICS_PATH = Path("generated/analytics.json")


def initialize_analytics():
    ANALYTICS_PATH.parent.mkdir(exist_ok=True)

    if not ANALYTICS_PATH.exists():
        ANALYTICS_PATH.write_text(
            json.dumps({"events_created": 0, "last_title": "-"}, indent=2),
            encoding="utf-8",
        )


def _read():
    initialize_analytics()
    return json.loads(ANALYTICS_PATH.read_text(encoding="utf-8"))


def _write(data):
    ANALYTICS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_event_created(event):
    data = _read()
    data["events_created"] = int(data.get("events_created", 0)) + 1
    data["last_title"] = event.get("title", "-")
    _write(data)


def get_analytics_summary():
    return _read()
