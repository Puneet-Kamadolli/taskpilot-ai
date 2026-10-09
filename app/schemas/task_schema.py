from pydantic import BaseModel

class TaskCreate(BaseModel):

    original_prompt: str
    title: str
    category: str
    priority: str
    severity: str

class TaskResponse(BaseModel):

    id: int
    original_prompt: str
    title: str
    category: str
    priority: str
    severity: str
    status: str

    class Config:
         from_attributes = True

class TaskUpdate(BaseModel):
    
    original_prompt: str
    title: str
    category: str
    priority: str
    severity: str
    status: str