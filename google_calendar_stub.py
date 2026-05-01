def create_google_calendar_event_stub(event):
    return {
        "status": "stub_only",
        "operation": "events.insert",
        "message": "OAuth is not configured yet. This shows the future Google Calendar API payload.",
        "google_calendar_payload": {
            "summary": event.get("title"),
            "description": event.get("description"),
            "location": event.get("location"),
            "start": {"dateTime": event.get("start")},
            "end": {"dateTime": event.get("end")},
        },
    }


def update_google_calendar_event_stub(event_id, event):
    return {
        "status": "stub_only",
        "operation": "events.update",
        "event_id": event_id,
        "payload": event,
    }


def delete_google_calendar_event_stub(event_id):
    return {
        "status": "stub_only",
        "operation": "events.delete",
        "event_id": event_id,
    }
