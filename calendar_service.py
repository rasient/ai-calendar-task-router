from datetime import datetime
from pathlib import Path
from uuid import uuid4


def _ics_datetime(iso_value):
    dt = datetime.fromisoformat(iso_value)
    return dt.strftime("%Y%m%dT%H%M%S")


def _escape(value):
    value = value or ""
    return value.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def create_ics_file(event, output_path):
    output_path = Path(output_path)

    title = _escape(event.get("title", "Untitled event"))
    description = _escape(event.get("description", ""))
    location = _escape(event.get("location", ""))

    start = _ics_datetime(event["start"])
    end = _ics_datetime(event["end"])
    uid = f"{uuid4()}@ai-calendar-task-router"

    ics = f'''BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Calendar Task Router//EN
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{start}
DTSTART:{start}
DTEND:{end}
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
END:VEVENT
END:VCALENDAR
'''

    output_path.write_text(ics, encoding="utf-8")
    return output_path
