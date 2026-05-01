import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from ai_parser import parse_task_to_event, analyze_task_system
from calendar_service import create_ics_file
from routing import route_task
from analytics import initialize_analytics, record_event_created, record_suggestion, get_analytics_summary
from database import initialize_database, save_event, list_events, update_event_record, delete_event_record
from preferences import load_preferences, save_preferences
from google_calendar_stub import create_google_calendar_event_stub, update_google_calendar_event_stub, delete_google_calendar_event_stub
from oauth_stub import show_oauth_status


load_dotenv()

st.set_page_config(page_title="AI Calendar Task Router Pro Prototype", page_icon="📅", layout="wide")

st.title("📅 AI Calendar Task Router — Production Prototype")
st.write("Task text → AI understanding → review → .ics export / Google Calendar integration scaffold")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

initialize_database()
initialize_analytics()
prefs = load_preferences()

with st.sidebar:
    st.header("Settings")

    timezone = st.selectbox(
        "Timezone",
        ["Europe/Budapest", "UTC"],
        index=0 if prefs.get("timezone", "Europe/Budapest") == "Europe/Budapest" else 1,
    )

    default_duration = st.slider(
        "Default duration in minutes",
        15,
        180,
        int(prefs.get("default_duration", 30)),
        step=15,
    )

    confidence_threshold = st.slider(
        "Auto-create confidence threshold",
        0.50,
        0.99,
        float(prefs.get("confidence_threshold", 0.85)),
        step=0.01,
    )

    working_hours_start = st.time_input("Working hours start", value=prefs.get("working_hours_start"))
    working_hours_end = st.time_input("Working hours end", value=prefs.get("working_hours_end"))

    if st.button("Save preferences"):
        save_preferences({
            "timezone": timezone,
            "default_duration": default_duration,
            "confidence_threshold": confidence_threshold,
            "working_hours_start": working_hours_start,
            "working_hours_end": working_hours_end,
        })
        st.success("Preferences saved.")

tabs = st.tabs([
    "📥 Task Router",
    "📅 Google Calendar Scaffold",
    "🗃️ Event Database",
    "📨 Gmail / Email Intake",
    "🎤 Voice Prototype",
    "🤖 Automation Control",
    "📊 Analytics",
    "📱 Mobile UI",
])

with tabs[0]:
    st.subheader("📥 Task Router")
    task_text = st.text_area(
        "Task / teendő",
        "Holnap 10-kor küldjem el Katának a videót és kérjek visszajelzést.",
        height=140,
    )

    if st.button("Analyze, route and prepare event"):
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
        st.markdown("### Route decision")
        st.json(st.session_state["route"])

    if "event" in st.session_state:
        event = st.session_state["event"]
        st.markdown("### Review event")

        edited_event = {
            "title": st.text_input("Title", event.get("title", "")),
            "start": st.text_input("Start ISO datetime", event.get("start", "")),
            "end": st.text_input("End ISO datetime", event.get("end", "")),
            "description": st.text_area("Description", event.get("description", ""), height=120),
            "location": st.text_input("Location", event.get("location", "")),
        }

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("Create .ics"):
                out = Path("generated/calendar_event.ics")
                create_ics_file(edited_event, out)
                save_event(edited_event, source="ics")
                record_event_created(edited_event)
                with open(out, "rb") as f:
                    st.download_button("Download .ics", f, "calendar_event.ics", "text/calendar")

        with col_b:
            if st.button("Save to local DB"):
                save_event(edited_event, source="local_db")
                st.success("Saved to local database.")

        with col_c:
            if st.button("Google Calendar insert scaffold"):
                result = create_google_calendar_event_stub(edited_event)
                st.json(result)

with tabs[1]:
    st.subheader("📅 Google Calendar Integration Scaffold")
    show_oauth_status()

    st.markdown("""
This tab implements the production integration structure without forcing OAuth setup yet.

Production flow:

```txt
OAuth login
→ choose calendar
→ events.insert
→ store Google event ID
→ allow update/delete
```
""")

    sample = {
        "title": "Sample Google Calendar event",
        "start": "2026-05-02T10:00:00+02:00",
        "end": "2026-05-02T10:30:00+02:00",
        "description": "Google Calendar integration scaffold.",
        "location": "",
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Simulate events.insert"):
            st.json(create_google_calendar_event_stub(sample))

    with col2:
        if st.button("Simulate events.update"):
            st.json(update_google_calendar_event_stub("fake_google_event_id", sample))

    with col3:
        if st.button("Simulate events.delete"):
            st.json(delete_google_calendar_event_stub("fake_google_event_id"))

with tabs[2]:
    st.subheader("🗃️ Persistent Local Event Database")
    st.write("This is the production-ready direction for tracking created, updated, skipped and reviewed events.")

    events = list_events()
    st.dataframe(events, use_container_width=True)

    if events:
        selected_id = st.selectbox("Select event ID", [event["id"] for event in events])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Mark selected as updated"):
                update_event_record(selected_id, {"status": "updated"})
                st.success("Updated.")

        with col2:
            if st.button("Delete selected locally"):
                delete_event_record(selected_id)
                st.success("Deleted locally.")

with tabs[3]:
    st.subheader("📨 Gmail / Email Intake Prototype")
    email_text = st.text_area(
        "Paste email or message",
        "Szia Alexander, köszi a videót! Tudnánk holnap 11-kor 20 percet beszélni róla?",
        height=160,
    )

    if st.button("Extract calendar follow-up"):
        parsed = parse_task_to_event(email_text, client, timezone, default_duration)
        analysis = analyze_task_system(email_text, client, timezone, default_duration)
        st.json({
            "parsed_event": parsed,
            "analysis": analysis,
            "source": "email_paste",
            "next_production_step": "Connect Gmail API and pull selected messages into this parser.",
        })

with tabs[4]:
    st.subheader("🎤 Voice Input Prototype")
    st.write("Real browser voice recording is a future production layer. Current version accepts dictated text.")

    dictated_text = st.text_input(
        "Paste dictated task",
        "Holnap délután 3-kor nézzem át a GitHub README-t.",
    )

    if st.button("Parse dictated task"):
        st.json(parse_task_to_event(dictated_text, client, timezone, default_duration))

with tabs[5]:
    st.subheader("🤖 Controlled Automation")
    automation_task = st.text_area(
        "Task for confidence decision",
        "Holnap 10-kor küldjem el Katának a videót.",
        height=100,
    )

    if st.button("Evaluate automation"):
        analysis = analyze_task_system(automation_task, client, timezone, default_duration)
        confidence = float(analysis.get("confidence", 0.65))

        if confidence >= confidence_threshold:
            decision = "Eligible for auto-create in production"
        else:
            decision = "Manual review required"

        st.json({
            "confidence": confidence,
            "threshold": confidence_threshold,
            "decision": decision,
            "safety_rule": "This prototype still keeps user approval before execution.",
        })

with tabs[6]:
    st.subheader("📊 Analytics")
    summary = get_analytics_summary()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Events created", summary.get("events_created", 0))
    c2.metric("Suggestions", summary.get("suggestions", 0))
    c3.metric("Last title", summary.get("last_title", "-"))
    c4.metric("Mode", "Review-first")

    st.json(summary)

with tabs[7]:
    st.subheader("📱 Mobile-first UI Prototype")
    st.write("This tab approximates the mobile quick-add workflow.")

    st.markdown("""
### Quick-add flow

```txt
Open app
→ type/speak task
→ AI suggests calendar event
→ swipe/approve
→ event created
```
""")

    quick_task = st.text_input("Quick task", "Holnap 9-kor reggeli tervezés.")
    if st.button("Mobile quick parse"):
        st.json(parse_task_to_event(quick_task, client, timezone, default_duration))

st.divider()
st.caption("Production principle: AI suggests → human reviews → user approves → system executes.")
