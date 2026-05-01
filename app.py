import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from ai_parser import parse_task_to_event, analyze_task_system
from calendar_service import create_ics_file
from routing import route_task
from analytics import initialize_analytics, record_event_created, get_analytics_summary


load_dotenv()

st.set_page_config(page_title="AI Calendar Task Router", page_icon="📅", layout="wide")

st.title("📅 AI Calendar Task Router")
st.write("Task text → AI parse → human review → calendar-ready output")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

initialize_analytics()

with st.sidebar:
    st.header("Settings")
    timezone = st.selectbox("Timezone", ["Europe/Budapest", "UTC"], index=0)
    default_duration = st.slider("Default duration in minutes", 15, 180, 30, step=15)
    confidence_threshold = st.slider("Auto-create confidence threshold", 0.50, 0.99, 0.85, step=0.01)
    st.caption("Current version still requires review before .ics export.")

tabs = st.tabs([
    "📥 Task Router",
    "🔁 Recurring Tasks",
    "🧠 Smart Understanding",
    "📨 Email → Calendar",
    "🎤 Voice Input",
    "🤖 Controlled Automation",
    "📊 Analytics",
])

with tabs[0]:
    st.subheader("📥 Task Router")
    st.write("Routes messy human intention into the right system: calendar, todo, reminder, or note.")

    task_text = st.text_area(
        "Task / teendő",
        "Holnap 10-kor küldjem el Katának a videót és kérjek visszajelzést.",
        height=140,
        key="main_task_text",
    )

    if st.button("🧠 Analyze and route task"):
        st.session_state["system_analysis"] = analyze_task_system(task_text, client, timezone, default_duration)
        st.session_state["route_result"] = route_task(task_text, st.session_state["system_analysis"])
        st.session_state["parsed_event"] = parse_task_to_event(task_text, client, timezone, default_duration)

    if "route_result" in st.session_state:
        st.markdown("### Routing result")
        st.json(st.session_state["route_result"])

    if "parsed_event" in st.session_state:
        event = st.session_state["parsed_event"]

        st.markdown("### Review calendar event")
        st.json(event)

        title = st.text_input("Title", event.get("title", "Untitled task"))
        start = st.text_input("Start ISO datetime", event.get("start", ""))
        end = st.text_input("End ISO datetime", event.get("end", ""))
        description = st.text_area("Description", event.get("description", ""), height=120)
        location = st.text_input("Location", event.get("location", ""))

        reviewed_event = {
            "title": title,
            "start": start,
            "end": end,
            "description": description,
            "location": location,
        }

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Create .ics calendar file"):
                output_dir = Path("generated")
                output_dir.mkdir(exist_ok=True)
                ics_path = output_dir / "calendar_event.ics"
                create_ics_file(reviewed_event, ics_path)
                record_event_created(reviewed_event)

                st.success("Calendar file created.")

                with open(ics_path, "rb") as file:
                    st.download_button(
                        "Download .ics file",
                        data=file,
                        file_name="calendar_event.ics",
                        mime="text/calendar",
                    )

        with col2:
            st.info("Future direct Google Calendar insert will live here after OAuth is added.")

with tabs[1]:
    st.subheader("🔁 Recurring Task Prototype")
    recurring_input = st.text_area(
        "Recurring task text",
        "Minden hétfőn 9-kor nézzem át a heti teendőket.",
        height=100,
    )

    if st.button("Detect recurrence"):
        analysis = analyze_task_system(recurring_input, client, timezone, default_duration)
        st.json({
            "recurrence_detected": analysis.get("recurrence_detected", False),
            "recurrence_rule_suggestion": analysis.get("recurrence_rule_suggestion", ""),
            "human_review_required": True,
        })

with tabs[2]:
    st.subheader("🧠 Smart Task Understanding")
    smart_input = st.text_area(
        "Analyze task complexity",
        "Péntekig készítsek egy rövid videót, küldjem el Katának, és kérjek visszajelzést.",
        height=120,
    )

    if st.button("Analyze priority, deadline, effort"):
        analysis = analyze_task_system(smart_input, client, timezone, default_duration)
        st.json({
            "priority": analysis.get("priority", "medium"),
            "deadline": analysis.get("deadline", ""),
            "estimated_effort_minutes": analysis.get("estimated_effort_minutes", default_duration),
            "suggested_subtasks": analysis.get("suggested_subtasks", []),
            "confidence": analysis.get("confidence", 0.65),
        })

with tabs[3]:
    st.subheader("📨 Email → Calendar Prototype")
    st.write("Paste an email or message. The app extracts a calendar-ready follow-up.")

    email_text = st.text_area(
        "Email / message text",
        "Szia Alexander, köszi a videót! Tudnánk holnap 11-kor 20 percet beszélni róla?",
        height=160,
    )

    if st.button("Extract follow-up event from email"):
        parsed = parse_task_to_event(email_text, client, timezone, default_duration)
        st.json(parsed)

with tabs[4]:
    st.subheader("🎤 Voice Input Prototype")
    st.write("Browser voice capture is not implemented in this MVP yet, but this tab defines the product flow.")

    st.markdown("""
    **Future flow:**

    1. User speaks a task
    2. Speech is transcribed
    3. AI parses the task
    4. User reviews
    5. Calendar event is created

    Current workaround: paste dictated text from your phone or OS speech-to-text.
    """)

    voice_like_text = st.text_input("Paste dictated text here", "Holnap reggel 9-kor ellenőrizzem a naptár app GitHub repót.")
    if st.button("Parse dictated text"):
        st.json(parse_task_to_event(voice_like_text, client, timezone, default_duration))

with tabs[5]:
    st.subheader("🤖 Controlled Automation Prototype")
    auto_task = st.text_area(
        "Task for confidence check",
        "Holnap 10-kor videó elküldése Katának.",
        height=100,
    )

    if st.button("Check automation confidence"):
        analysis = analyze_task_system(auto_task, client, timezone, default_duration)
        confidence = float(analysis.get("confidence", 0.65))
        decision = "auto-create eligible" if confidence >= confidence_threshold else "requires manual review"

        st.json({
            "confidence": confidence,
            "threshold": confidence_threshold,
            "decision": decision,
            "safety_rule": "Even if eligible, this MVP still asks for review before event export.",
        })

with tabs[6]:
    st.subheader("📊 Analytics & Feedback Loop")
    summary = get_analytics_summary()

    col1, col2, col3 = st.columns(3)
    col1.metric("Events created", summary["events_created"])
    col2.metric("Last title", summary["last_title"])
    col3.metric("System mode", "Human review")

    st.markdown("""
    Future analytics:

    - created events
    - edited events
    - skipped suggestions
    - rescheduled events
    - preferred task durations
    - preferred working hours
    """)

st.divider()
st.caption("Design principle: AI suggests → human reviews → user approves → system executes.")
