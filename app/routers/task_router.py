from datetime import date, datetime, time, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

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
        severity = request.severity,
        due_date = request.due_date
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@router.get("", response_model=list[TaskResponse])
def get_all_tasks(
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    due_today: bool = False,
    overdue: bool = False,
    due_before: Optional[date] = Query(None),
    db: Session = Depends(get_db)):

    query = db.query(Task)

    # Filter based on fields

    if category:
        query = query.filter(Task.category == category)
    if priority:
        query = query.filter(Task.priority == priority)
    if severity: 
        query = query.filter(Task.severity == severity)
    if status: 
        query = query.filter(Task.status == status)

    # due date filters

    # Tasks with due today
    if due_today:

        today = date.today()
        start_of_day = datetime.combine(today, time.min)
        start_of_tomorrow = start_of_day + timedelta(days=1)

        query = query.filter(
            Task.due_date >= start_of_day,
            Task.due_date < start_of_tomorrow
        )

    # Overdue Tasks
    if overdue:
        current_time = datetime.now()

        query = query.filter(
            Task.due_date > current_time
        )

    # Tasks due before the specified date
    if due_before:

        cut_off = datetime.combine(due_before, time.min)

        query = query.filter(Task.due_date < cut_off)

    tasks = query.order_by(Task.id.desc()).all()
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
    task.due_date = request.due_date

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