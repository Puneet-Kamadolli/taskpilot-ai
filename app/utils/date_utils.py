
import re
from datetime import datetime, time, timedelta

from dateparser.search import search_dates


def extract_due_date(text: str) -> datetime | None:
    if not text or not text.strip():
        return None

    now = datetime.now()
    normalized_text = text.lower()

    # Rule 1: "this weekend" means Sunday at the end of the day.
    if re.search(r"\bthis weekend\b", normalized_text):
        days_until_sunday = (6 - now.weekday()) % 7
        target_date = now.date() + timedelta(days=days_until_sunday)

        return datetime.combine(target_date, time(23, 59, 59))

    # Rule 2: "next weekend" means the following weekend.
    if re.search(r"\bnext weekend\b", normalized_text):
        days_until_saturday = (5 - now.weekday()) % 7

        if days_until_saturday == 0:
            days_until_saturday = 7

        target_date = now.date() + timedelta(days=days_until_saturday + 8)

        return datetime.combine(target_date, time(23, 59, 59))

    # Rule 3: Extract dates from the text.
    matches = search_dates(
        text,
        settings={
            "RELATIVE_BASE": now,
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": False,
        },
    )

    if not matches:
        return None

    # Ignore false date matches that are not actual date expressions.
    date_matches = [
        (matched_text, parsed_date)
        for matched_text, parsed_date in matches
        if re.search(
            r"\b(?:today|tomorrow|yesterday|"
            r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
            r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
            r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
            r"sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|"
            r"\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?|"
            r"next\s+week|in\s+\d+\s+(?:day|week|month)s?)\b",
            matched_text,
            re.IGNORECASE,
        )
    ]

    if not date_matches:
        return None

    matched_text, parsed_date = date_matches[0]

    # If the input doesn't specify a clock time,
    # treat the deadline as the end of the day.
    has_explicit_time = bool(
        re.search(
            r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b"
            r"|\b\d{1,2}:\d{2}\b",
            matched_text,
            re.IGNORECASE,
        )
    )

    if not has_explicit_time:
        parsed_date = datetime.combine(
            parsed_date.date(),
            time(23, 59, 59),
        )

    return parsed_date
