# 📅 AI Calendar Task Router — Real Google Calendar

This version implements real Google Calendar OAuth and `events.insert`.

## Features

- AI task parsing
- Human review step
- Download `.ics`
- Real Google Calendar OAuth
- Real Google Calendar event insertion
- Calendar selection
- Local event database
- Analytics

## Google Calendar setup

1. Go to Google Cloud Console
2. Create a project
3. Enable Google Calendar API
4. Configure OAuth consent screen
5. Create OAuth Client ID
6. Choose Desktop app
7. Download the file as `credentials.json`
8. Put `credentials.json` in the project folder

## Run

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## OAuth flow

1. Open the app
2. Go to Google OAuth tab
3. Click Start Google OAuth
4. Open the authorization URL
5. Approve calendar access
6. Copy the redirected URL from browser
7. Paste it back into the app
8. Click Complete OAuth

This creates `token.json`.

## Safety principle

```txt
AI suggests → human reviews → user approves → event is created
```

## Important

Do not commit:

```txt
credentials.json
token.json
.env
```

They are already in `.gitignore`.

## Author

Alexander Berg
