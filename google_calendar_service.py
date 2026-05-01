import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar.events", "https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = Path("credentials.json")
TOKEN_PATH = Path("token.json")
REDIRECT_URI = "http://localhost:8501"


def get_google_auth_status():
    return {
        "credentials_json_found": CREDENTIALS_PATH.exists(),
        "token_json_found": TOKEN_PATH.exists(),
        "redirect_uri": REDIRECT_URI,
        "scopes": SCOPES,
    }


def _build_flow():
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError("credentials.json not found.")

    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_PATH),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    return flow


def start_google_oauth():
    flow = _build_flow()

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    return auth_url


def complete_google_oauth(redirected_url):
    flow = _build_flow()
    flow.fetch_token(authorization_response=redirected_url)

    credentials = flow.credentials
    TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")

    return {
        "token_saved": True,
        "token_path": str(TOKEN_PATH),
        "scopes": list(credentials.scopes or []),
    }


def get_credentials():
    if not TOKEN_PATH.exists():
        raise FileNotFoundError("token.json not found. Complete OAuth first.")

    credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")

    if not credentials or not credentials.valid:
        raise RuntimeError("Google credentials are invalid. Delete token.json and run OAuth again.")

    return credentials


def get_calendar_service():
    credentials = get_credentials()
    return build("calendar", "v3", credentials=credentials)


def list_calendars():
    service = get_calendar_service()
    result = service.calendarList().list().execute()
    calendars = result.get("items", [])

    return [
        {
            "id": item.get("id"),
            "summary": item.get("summary"),
            "primary": item.get("primary", False),
            "accessRole": item.get("accessRole"),
        }
        for item in calendars
    ]


def create_google_calendar_event(event, calendar_id="primary"):
    service = get_calendar_service()

    body = {
        "summary": event.get("title", "Untitled event"),
        "description": event.get("description", ""),
        "location": event.get("location", ""),
        "start": {
            "dateTime": event["start"],
        },
        "end": {
            "dateTime": event["end"],
        },
    }

    created = service.events().insert(
        calendarId=calendar_id,
        body=body,
    ).execute()

    return created


def update_google_calendar_event(event_id, event, calendar_id="primary"):
    service = get_calendar_service()

    body = {
        "summary": event.get("title", "Untitled event"),
        "description": event.get("description", ""),
        "location": event.get("location", ""),
        "start": {
            "dateTime": event["start"],
        },
        "end": {
            "dateTime": event["end"],
        },
    }

    return service.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body=body,
    ).execute()


def delete_google_calendar_event(event_id, calendar_id="primary"):
    service = get_calendar_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return {"deleted": True, "event_id": event_id, "calendar_id": calendar_id}
