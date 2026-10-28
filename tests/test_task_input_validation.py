import pytest
from pydantic import ValidationError
from app.schemas.task_schema import TaskCreate, TaskPromptCreate

@pytest.mark.parametrize(
    "priority",
    ["Low","Medium","High","Urgent"],
)
def test_valid_priorities_are_accepted(priority):
    task = TaskCreate(
        original_prompt="Prepare report",
        title="Prepare report",
        category="Work",
        priority=priority,
        severity='High',
    )
    assert task.priority == priority

def test_invalid_priority_is_rejected():
    with pytest.raises(ValidationError):
        TaskCreate(
            original_prompt="Prepare report",
            title="Prepare report",
            category="Work",
            priority="Super High",
            severity="Medium"
        )

def test_blank_title_is_rejected():

    with pytest.raises(ValidationError):
        TaskCreate(
            original_prompt="Prepare report",
            title="  ",
            category="Work",
            priority="High",
            severity="Medium"
        )

def test_blank_task_prompt_is_rejected():
    with pytest.raises(ValidationError):
        TaskPromptCreate(prompt=" ")