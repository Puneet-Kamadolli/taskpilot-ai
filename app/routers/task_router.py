from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate

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

@router.get("", response_model=list[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.id.desc()).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code= 404,
            detail=f"Task with ID {task_id} not found"
        )

    return task


@router.put("/{task_id}", response_model = TaskResponse)
def update_task(task_id: int,
                request: TaskUpdate,
                db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found"
        )

    task.original_prompt = request.original_prompt
    task.title = request.title
    task.category = request.category
    task.priority = request.priority
    task.severity = request.severity
    task.status = request.status

    db.commit()
    db.refresh(task)

    return task

@router.delete("/{task_id}")
def delete_task_by_id(task_id : int,
                      db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message":f"Task with ID {task_id} deleted successfully"
    }