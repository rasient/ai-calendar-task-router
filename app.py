import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from ai_parser import parse_task_to_event, analyze_task_system
from analytics import initialize_analytics, record_event_created, record_suggestion, get_analytics_summary
from calendar_service import create_ics_file
from database import initialize_database, save_event, list_events
from google_calendar_service import (
    get_google_auth_status,
    start_google_oauth,
    complete_google_oauth,
    list_calendars,
    create_google_calendar_event,
)
from routing import route_task


load_dotenv()

st.set_page_config(
    page_title="AI Calendar Task Router",
    page_icon="📅",
    layout="wide",
)

st.title("📅 AI Calendar Task Router — Real Google Calendar")
st.write("Task text → AI parse → human review → .ics export or real Google Calendar insert")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

initialize_database()
initialize_analytics()

with st.sidebar:
    st.header("Settings")
    timezone = st.selectbox("Timezone", ["Europe/Budapest", "UTC"], index=0)
    default_duration = st.slider("Default duration in minutes", 15, 180, 30, step=15)
    confidence_threshold = st.slider("Automation confidence threshold", 0.50, 0.99, 0.85, step=0.01)

tabs = st.tabs([
    "📥 Task → Calendar",
    "🔐 Google OAuth",
    "🗃️ Event Database",
    "📊 Analytics",
])

with tabs[1]:
    st.subheader("🔐 Google Calendar OAuth")

    status = get_google_auth_status()
    st.json(status)

    if not status["credentials_json_found"]:
        st.error(
            "Missing credentials.json. Download OAuth Desktop credentials from Google Cloud "
            "and place credentials.json in the project folder."
        )

    if status["credentials_json_found"]:
        if st.button("1️⃣ Start Google OAuth"):
            auth_url = start_google_oauth()
            st.session_state["google_auth_started"] = True
            st.markdown("Open this URL, approve access, then paste the full redirected URL below:")
            st.code(auth_url, language="text")

        redirected_url = st.text_input(
            "2️⃣ Paste redirected URL after Google approval",
            placeholder="http://localhost:8501/?state=...&code=...&scope=...",
        )

        if st.button("3️⃣ Complete OAuth and save token"):
            if not redirected_url.strip():
                st.warning("Paste the redirected URL first.")
            else:
                result = complete_google_oauth(redirected_url)
                st.success("OAuth completed. token.json saved.")
                st.json(result)

    if status["token_json_found"]:
        st.success("Google token is available. You can insert events into Google Calendar.")

        try:
            calendars = list_calendars()
            st.subheader("Available calendars")
            st.json(calendars)
        except Exception as e:
            st.warning(f"Could not list calendars yet: {e}")

with tabs[0]:
    st.subheader("📥 Task → Calendar")

    task_text = st.text_area(
        "Task / teendő",
        "Holnap 10-kor küldjem el Katának a videót és kérjek visszajelzést.",
        height=140,
    )

    if st.button("🧠 Analyze and prepare event"):
        analysis = analyze_task_system(task_text, client, timezone, default_duration)
        route = route_task(task_text, analysis)
        parsed = parse_task_to_event(task_text, client, timezone, default_duration)

        record_suggestion(route)

        st.session_state["analysis"] = analysis
        st.session_state["route"] = route
        st.session_state["event"] = parsed

    if "analysis" in st.session_state:
        st.markdown("### Smart understanding")
        st.json(st.session_state["analysis"])

    if "route" in st.session_state:
        st.markdown("### Routing decision")
        st.json(st.session_state["route"])

    if "event" in st.session_state:
        event = st.session_state["event"]

        st.markdown("### Review before execution")
        st.info("Review-first design: AI suggests → human reviews → user approves → event is created.")

        edited_event = {
            "title": st.text_input("Title", event.get("title", "")),
            "start": st.text_input("Start ISO datetime", event.get("start", "")),
            "end": st.text_input("End ISO datetime", event.get("end", "")),
            "description": st.text_area("Description", event.get("description", ""), height=120),
            "location": st.text_input("Location", event.get("location", "")),
        }

        calendar_id = "primary"

        if get_google_auth_status()["token_json_found"]:
            try:
                calendars = list_calendars()
                calendar_options = {
                    f"{cal.get('summary', cal.get('id'))} ({cal.get('id')})": cal.get("id")
                    for cal in calendars
                }
                selected_calendar = st.selectbox("Google Calendar", list(calendar_options.keys()))
                calendar_id = calendar_options[selected_calendar]
            except Exception:
                calendar_id = "primary"

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Create .ics"):
                out = Path("generated/calendar_event.ics")
                create_ics_file(edited_event, out)
                save_event(edited_event, source="ics")
                record_event_created(edited_event)

                with open(out, "rb") as f:
                    st.download_button("Download .ics", f, "calendar_event.ics", "text/calendar")

        with col2:
            if st.button("Save to local DB"):
                saved = save_event(edited_event, source="local_db")
                st.success("Saved locally.")
                st.json(saved)

        with col3:
            if st.button("Insert into Google Calendar"):
                if not get_google_auth_status()["token_json_found"]:
                    st.error("Google OAuth is not completed yet. Go to the Google OAuth tab first.")
                else:
                    created = create_google_calendar_event(edited_event, calendar_id=calendar_id)
                    save_event(
                        {
                            **edited_event,
                            "google_event_id": created.get("id"),
                            "google_html_link": created.get("htmlLink"),
                        },
                        source="google_calendar",
                    )
                    record_event_created(edited_event)
                    st.success("Created in Google Calendar.")
                    st.json(created)
                    if created.get("htmlLink"):
                        st.markdown(f"[Open event in Google Calendar]({created['htmlLink']})")

with tabs[2]:
    st.subheader("🗃️ Local Event Database")
    events = list_events()
    st.dataframe(events, use_container_width=True)

with tabs[3]:
    st.subheader("📊 Analytics")
    st.json(get_analytics_summary())
