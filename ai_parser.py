import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def fallback_parse(task_text, timezone="Europe/Budapest", default_duration=30):
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    start = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=default_duration)

    return {
        "title": "Teendő naptárba tétele",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "description": task_text,
        "location": "",
    }


def parse_task_to_event(task_text, client=None, timezone="Europe/Budapest", default_duration=30):
    if not client:
        return fallback_parse(task_text, timezone, default_duration)

    prompt = f'''
You convert user tasks into calendar events.

Return ONLY valid JSON:
{{
  "title": "short event title",
  "start": "ISO datetime with timezone offset",
  "end": "ISO datetime with timezone offset",
  "description": "clear event description",
  "location": ""
}}

Timezone: {timezone}
Default duration: {default_duration} minutes.
If no time is provided, choose 09:00.
Keep title short.

Task:
{task_text}
'''

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        text = response.output_text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(text)

        for key in ["title", "start", "end", "description", "location"]:
            if key not in parsed:
                raise ValueError(f"Missing key: {key}")

        return parsed

    except Exception:
        return fallback_parse(task_text, timezone, default_duration)


def fallback_analysis(task_text, default_duration=30):
    lowered = task_text.lower()

    recurrence_detected = any(word in lowered for word in ["minden", "every", "hetente", "naponta", "weekly", "daily"])
    deadline = "detected" if any(word in lowered for word in ["péntek", "holnap", "deadline", "ig", "by"]) else ""
    priority = "high" if any(word in lowered for word in ["fontos", "urgent", "sürgős", "deadline"]) else "medium"

    return {
        "priority": priority,
        "deadline": deadline,
        "estimated_effort_minutes": default_duration,
        "suggested_subtasks": ["Clarify task goal", "Schedule focused time", "Review outcome"],
        "recurrence_detected": recurrence_detected,
        "recurrence_rule_suggestion": "RRULE:FREQ=WEEKLY" if recurrence_detected else "",
        "confidence": 0.65,
    }


def analyze_task_system(task_text, client=None, timezone="Europe/Budapest", default_duration=30):
    if not client:
        return fallback_analysis(task_text, default_duration)

    prompt = f'''
Analyze this task as a productivity routing system.

Return ONLY valid JSON:
{{
  "priority": "low|medium|high",
  "deadline": "deadline text or empty string",
  "estimated_effort_minutes": 30,
  "suggested_subtasks": ["subtask 1", "subtask 2"],
  "recurrence_detected": false,
  "recurrence_rule_suggestion": "",
  "confidence": 0.75
}}

Timezone: {timezone}
Default duration: {default_duration}

Task:
{task_text}
'''

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        text = response.output_text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception:
        return fallback_analysis(task_text, default_duration)
