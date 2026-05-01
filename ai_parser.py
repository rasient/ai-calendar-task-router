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

    prompt = f"""
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
"""

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
