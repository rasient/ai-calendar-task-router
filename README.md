# 📅 AI Calendar Task Router — Production Prototype

This version turns the “Recommended next production features” into real app modules and working prototypes.

## Included production-feature prototypes

### Google Calendar API scaffold
- OAuth status panel
- `events.insert` payload preview
- update/delete stubs
- clear next step for OAuth

### Persistent local database
- saves created/reviewed events into local JSON storage
- lists events
- update/delete local event records

### User preferences
- timezone
- default duration
- confidence threshold
- working hours

### Gmail / Email intake
- paste an email/message
- extract a calendar-ready follow-up event

### Voice input prototype
- supports dictated text
- documents future voice-to-calendar flow

### Controlled automation
- confidence threshold
- low confidence → manual review
- high confidence → eligible for auto-create
- still review-first for safety

### Analytics
- event creation count
- suggestion count
- route distribution
- last created event

## Safe architecture

```txt
AI suggests → human reviews → user approves → system executes
```

## Install

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

## Future real production step

To activate direct Google Calendar creation:

1. Create Google Cloud project
2. Enable Google Calendar API
3. Configure OAuth consent screen
4. Download `credentials.json`
5. Implement `google-auth-oauthlib`
6. Replace stubs with real `events.insert`, `events.update`, `events.delete`

## Author

Alexander Berg
