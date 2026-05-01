# 📅 AI Calendar Task Router Expanded

AI Calendar Task Router converts unstructured tasks into structured, reviewable calendar events and task-routing decisions.

## Core idea

```txt
Messy human intention
→ AI understanding
→ destination decision
→ human review
→ calendar-ready output
```

## What is included

This version does not only list future features. It turns them into app modules and prototypes.

## App modules

### 1. Task Router
Routes tasks to calendar, todo, reminder, note, or recurring calendar review.

### 2. Recurring Tasks
Detects recurrence patterns such as every Monday, daily, minden hétfőn, naponta.

### 3. Smart Understanding
Extracts priority, deadline, effort estimate, subtasks, and confidence.

### 4. Email → Calendar
Paste an email/message and extract a calendar-ready follow-up event.

### 5. Voice Input Prototype
Defines the voice-to-calendar flow and supports pasted dictated text.

### 6. Controlled Automation
Shows confidence-based automation logic.

### 7. Analytics
Tracks basic local analytics.

## Current safe MVP

```txt
Task text
→ AI parse
→ Human review
→ Download .ics file
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

Create `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Recommended next production features

- Google Calendar API OAuth
- Direct `events.insert`
- Event update/delete
- Real voice input
- Gmail integration
- Persistent database
- User preference learning
- Mobile-first UI
- Confidence threshold automation

## Design principle

```txt
AI suggests → human reviews → user approves → system executes
```

## Author

Alexander Berg
