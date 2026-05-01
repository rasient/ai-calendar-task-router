def route_task(task_text, analysis):
    lowered = task_text.lower()

    if analysis.get("recurrence_detected"):
        destination = "calendar_recurring_review"
    elif any(word in lowered for word in ["holnap", "ma ", "meeting", "találkozó", "10-kor", "9-kor"]):
        destination = "calendar"
    elif any(word in lowered for word in ["jegyzet", "note", "ötlet", "idea"]):
        destination = "note"
    elif any(word in lowered for word in ["emlékeztess", "remind"]):
        destination = "reminder"
    else:
        destination = "todo_or_calendar_review"

    return {
        "recommended_destination": destination,
        "reason": "Destination selected from timing, recurrence, and task language.",
        "human_review_required": True,
        "confidence": analysis.get("confidence", 0.65),
    }
