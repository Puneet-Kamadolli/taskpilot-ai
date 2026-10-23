import logging

from datetime import date, datetime, time, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate, TaskPromptCreate
from app.utils.date_utils import extract_due_date
from app.services.gemini_service import extract_task_details

logger = logging.getLogger(__name__)

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

    # Use the explicitly supplied deadline when available
    # Otherwise, try to extract it from the original prompt

    due_date = request.due_date

    if due_date is None:
        due_date = extract_due_date(request.original_prompt)

    task = Task(
        original_prompt = request.original_prompt,
        title = request.title,
        category = request.category,
        priority = request.priority,
        severity = request.severity,
        due_date = due_date
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@router.post("/from-prompt", response_model=TaskResponse, status_code=201)
def create_task_from_prompt(
    request: TaskPromptCreate,
    db: Session = Depends(get_db)
):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=422,
            detail="Task prompt cannot be empty"
        )

    # Step 1: Extract task details from gemini
    try:
        details = extract_task_details(prompt)
    except Exception:
        logger.exception("Gemini task extraction failed")
        raise HTTPException(
            status_code=502,
            detail="Could not extract task details. Please try again."
        )

    # Step 2: Extract task deadline using date utility
    due_date = extract_due_date(prompt)

    # Step 3: Build database model
    task = Task(
        original_prompt=prompt,
        title=details.title,
        category=details.category,
        priority=details.priority,
        severity=details.severity,
        due_date=due_date 
    )

    # Step 4: save the task
    db.add(task)
    db.commit()
    db.refresh(task)

    # Step 5: return task
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
            Task.due_date.isnot(None),
            Task.due_date < current_time,
            Task.status == 'Pending'
        )

    # Tasks due before the specified date
    if due_before:

        cut_off = datetime.combine(due_before + timedelta(days=1), time.min)

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