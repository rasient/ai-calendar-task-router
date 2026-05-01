import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


DB_PATH = Path("generated/events.json")


def initialize_database():
    DB_PATH.parent.mkdir(exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.write_text("[]", encoding="utf-8")


def _read():
    initialize_database()
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def _write(data):
    DB_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def save_event(event, source="local"):
    data = _read()
    record = {
        "id": str(uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "status": "created",
        "source": source,
        "event": event,
    }
    data.append(record)
    _write(data)
    return record


def list_events():
    return _read()
