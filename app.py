import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from ai_parser import parse_task_to_event
from calendar_service import create_ics_file


load_dotenv()

st.set_page_config(page_title="AI Calendar Task Router", page_icon="📅", layout="wide")

st.title("📅 AI Calendar Task Router")
st.write("Task text → AI parse → human review → downloadable .ics calendar event")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

timezone = st.selectbox("Timezone", ["Europe/Budapest", "UTC"], index=0)
default_duration = st.slider("Default duration in minutes", 15, 180, 30, step=15)

task_text = st.text_area(
    "Task / teendő",
    "Holnap 10-kor küldjem el Katának a videót és kérjek visszajelzést.",
    height=140,
)

if st.button("🧠 Parse task"):
    st.session_state["parsed_event"] = parse_task_to_event(
        task_text=task_text,
        client=client,
        timezone=timezone,
        default_duration=default_duration,
    )

if "parsed_event" in st.session_state:
    event = st.session_state["parsed_event"]

    st.subheader("Review before calendar export")
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

    if st.button("✅ Create .ics calendar file"):
        output_dir = Path("generated")
        output_dir.mkdir(exist_ok=True)

        ics_path = output_dir / "calendar_event.ics"
        create_ics_file(reviewed_event, ics_path)

        st.success("Calendar file created.")

        with open(ics_path, "rb") as file:
            st.download_button(
                "Download .ics file",
                data=file,
                file_name="calendar_event.ics",
                mime="text/calendar",
            )

st.divider()

st.subheader("🧭 Recommended future features")
st.info("This is an MVP. Future system direction is shown below.")

st.markdown("""
### 🔗 1. Google Calendar integration
- OAuth login
- Direct event creation without `.ics`
- Multiple calendar selection
- Event update and delete

---

### 🔁 2. Recurring events
- “Every Monday”
- “Daily at 9”
- AI detection of repetition patterns
- Review before recurring event creation

---

### 🧠 3. Smart task understanding
- Priority detection
- Deadline extraction
- Effort estimation
- Multi-step task splitting
- Better handling of vague time expressions

---

### 📨 4. Email → calendar automation
- Parse Gmail messages into events
- Detect meetings, deadlines, and follow-ups
- Convert email requests into calendar-ready tasks

---

### 🎤 5. Voice input
- Speak tasks into the app
- Auto-transcription
- Mobile-first quick capture

---

### 📱 6. Mobile-first interface
- Quick-add task input
- Swipe-to-approve events
- Notification-style review

---

### 🤖 7. Controlled automation mode
- Confidence-based event creation
- Low confidence → manual approval
- High confidence → optional auto-create

---

### 🧩 8. Task routing system
Instead of only calendar:

```txt
Task → decide destination:
→ calendar
→ todo
→ reminder
→ note
```

---

### 📊 9. Analytics and feedback loop
- Track completed events
- Track skipped or rescheduled events
- Improve AI parsing over time

---

### 🔄 10. Learning system
The system learns user preferences:

- preferred meeting length
- working hours
- naming style
- default task categories
""")

st.divider()

st.markdown("""
### Design principle

```txt
AI suggests → human reviews → user approves → system executes
```

This avoids risky blind automation and keeps the user in control.
""")
