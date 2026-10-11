from datetime import datetime

from app.utils.date_utils import extract_due_date

def test_extract_tomorrow():
    result = extract_due_date("Complete the project by tomorrow at 6 PM")

    assert result is not None
    assert result.hour == 18
    assert result.minute == 0 

def test_extract_weekend():
    result = extract_due_date("Complete the project by this weekend")

    assert result is not None
    assert result.weekday() == 6
    assert result.hour == 23

def test_no_deadline():
    result = extract_due_date("Review the project requirements")

    assert result is None