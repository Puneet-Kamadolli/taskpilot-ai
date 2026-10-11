import re
from datetime import date, datetime, time, timedelta

from dateparser.search import search_dates

def extract_due_date(text: str) -> datetime | None:
    if not text or not text.strip():
        return None

    now = datetime.now()
    normalized_text = text.lower()

    # Rule 1: "this weekend" means Sunday at the end of the day
    if re.search(r"\bthis weekend\b", normalized_text):
        days_until_sunday = (6 - now.weekday()) % 7
        target_date = now.date() + timedelta(days=days_until_sunday)

        return datetime.combine(target_date, time(23, 59, 59))

    # Rule 2: "next weekend" means the following weekend
    if re.search(r"\bnext weekend\b",normalized_text):
        days_until_saturday = (5 - now.weekday()) % 7

        if days_until_saturday == 0:
            days_until_saturday = 7

        target_date = now.date() + timedelta(days= days_until_saturday + 8)

        return datetime.combine(target_date, time(23, 59, 59))

    # Rule 3: Extract other dates from the text
    matches = search_dates(
        text,
        settings={
            "RELATIVE_BASE": now,
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": False
        }
    )

    if not matches:
        return None

    matched_text, parsed_date = matches[0]

    # If the input doesn't specify a clock time
    # treat the deadline as the end of the day

    has_explicit_time = bool(
        re.search(
            r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b"
            r"|\b\d{1,2}:\d{2}\b",
            matched_text,
            re.IGNORECASE
        )
    )

    if not has_explicit_time:
        parsed_date = datetime.combine(
            parsed_date.date(),
            time(23, 59, 59)
        )

    return parsed_date