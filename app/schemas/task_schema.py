from datetime import datetime
from typing import Optional, Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict, StringConstraints

# Allowed Task values
TaskCategory = Literal[
    "Work",
    "Personal",
    "Learning",
    "Health",
    "Other",
]

TaskPriority = Literal[
    "Low",
    "Medium",
    "High",
    "Urgent",
]

TaskSeverity = Literal[
    "Low",
    "Medium",
    "High",
    "Critical",
]

TaskStatus = Literal[
    "Pending",
    "In Progress",
    "Completed",
]

# Non-empty string with surrounding whitespace removed
NonEmptyText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
] 

class TaskCreate(BaseModel):

    original_prompt: NonEmptyText
    title: Annotated[NonEmptyText, StringConstraints(max_length=200)]
    category: TaskCategory
    priority: TaskPriority
    severity: TaskSeverity
    due_date: datetime | None = None

class TaskResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_prompt: str
    title: str
    category: TaskCategory
    priority: TaskPriority
    severity: TaskSeverity
    status: TaskStatus
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    
    original_prompt: NonEmptyText
    title: Annotated[NonEmptyText, StringConstraints(max_length=200)]
    category: TaskCategory
    priority: TaskPriority
    severity: TaskSeverity
    status: TaskStatus
    due_date: datetime | None = None 

class TaskPromptCreate(BaseModel):
    prompt: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=1000
        ),
    ] = Field(description="Natural-language description of the task")