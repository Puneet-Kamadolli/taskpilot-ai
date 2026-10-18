from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):

    original_prompt: str
    title: str
    category: str
    priority: str
    severity: str
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):

    id: int
    original_prompt: str
    title: str
    category: str
    priority: str
    severity: str
    status: str
    due_date: Optional[datetime] = None

    class Config:
         from_attributes = True

class TaskUpdate(BaseModel):
    
    original_prompt: str
    title: str
    category: str
    priority: str
    severity: str
    status: str
    due_date: Optional[datetime] = None 

class TaskPromptCreate(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=1000,
        description="Natural-language description of the task"
    )