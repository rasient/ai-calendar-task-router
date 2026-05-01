# 📅 AI Calendar Task Router

AI Calendar Task Router converts unstructured tasks into structured, reviewable calendar events.

## Core idea

Most productivity tools store tasks.

This project routes tasks into time.

```txt
Unstructured task
→ AI parsing
→ Human review
→ Calendar-ready event
```

## Current MVP

The current version focuses on safe automation:

```txt
Task text → AI parse → human review → .ics file
```

This avoids incorrect automatic calendar inserts.

## Features

- Natural-language task input
- AI event parsing with OpenAI
- Fallback parser if no API key is available
- Human review step before creation
- Editable title, time, description, and location
- Downloadable `.ics` calendar event
- Works with Google Calendar, Outlook, and Apple Calendar
- Europe/Budapest timezone support

## Example

Input:

```txt
Holnap 10-kor küldjem el Katának a videót és kérjek visszajelzést.
```

Output:

```json
{
  "title": "Videó elküldése Katának",
  "start": "2026-05-02T10:00:00+02:00",
  "end": "2026-05-02T10:30:00+02:00",
  "description": "Elküldeni a kész videót Katának és visszajelzést kérni.",
  "location": ""
}
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m streamlit run app.py
```

## Environment

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Recommended future features

### 1. Google Calendar integration
- OAuth login
- Direct event creation without `.ics`
- Multiple calendar selection
- Event update and delete

### 2. Recurring events
- “Every Monday”
- “Daily at 9”
- AI detection of repetition patterns
- Review before recurring event creation

### 3. Smart task understanding
- Priority detection
- Deadline extraction
- Effort estimation
- Multi-step task splitting
- Better handling of vague time expressions

### 4. Email → calendar automation
- Parse Gmail messages into events
- Detect meetings, deadlines, and follow-ups
- Convert email requests into calendar-ready tasks

### 5. Voice input
- Speak tasks into the app
- Auto-transcription
- Mobile-first quick capture

### 6. Mobile-first interface
- Quick-add task input
- Swipe-to-approve events
- Notification-style review

### 7. Controlled automation mode
- Confidence-based event creation
- Low confidence → manual approval
- High confidence → optional auto-create

### 8. Task routing system

Instead of only calendar:

```txt
Task → decide destination:
→ calendar
→ todo
→ reminder
→ note
```

### 9. Analytics and feedback loop
- Track completed events
- Track skipped or rescheduled events
- Improve AI parsing over time

### 10. Learning system
The system learns user preferences:

- preferred meeting length
- working hours
- naming style
- default task categories

## Design principle

```txt
AI suggests → human reviews → user approves → system executes
```

This avoids risky blind automation and keeps the user in control.

## Positioning

This is not just a reminder app.

It is a small sociotechnical workflow system:

```txt
messy human intention → structured digital time
```

## Author

Alexander Berg
