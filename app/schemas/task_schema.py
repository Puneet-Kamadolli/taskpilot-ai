from datetime import datetime
from typing import Optional
from pydantic import BaseModel

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