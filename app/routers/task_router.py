from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task import Task
from app.schemas.task_schema import (TaskCreate, TaskResponse)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
    )

@router.post(
    "",
    response_model=TaskResponse
)
def create_task(
    request: TaskCreate,
    db: Session = Depends(get_db)
):
    task = Task(
        original_prompt = request.original_prompt,
        title = request.title,
        category = request.category,
        priority = request.priority,
        severity = request.severity
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task