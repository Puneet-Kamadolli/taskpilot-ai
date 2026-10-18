
import logging
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models.task import Task
from app.services import remainder_scheduler


@pytest.fixture
def test_session_factory(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    monkeypatch.setattr(
        remainder_scheduler,
        "SessionLocal",
        TestSessionLocal,
    )

    yield TestSessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_task(
    db,
    title,
    due_date,
    status="Pending",
    reminder_sent=False,
):
    task = Task(
        original_prompt=title,
        title=title,
        category="Work",
        priority="High",
        severity="High",
        status=status,
        due_date=due_date,
        reminder_sent=reminder_sent,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task.id


def test_due_task_is_reminded_once(
    test_session_factory,
    caplog,
):
    caplog.set_level(logging.INFO)

    db = test_session_factory()
    task_id = create_task(
        db,
        title="Push code changes",
        due_date=datetime.now() + timedelta(minutes=5),
    )
    db.close()

    remainder_scheduler.check_due_tasks()

    db = test_session_factory()
    task = db.get(Task, task_id)

    assert task.reminder_sent is True
    assert "UPCOMING TASK REMAINDERS" in caplog.text

    db.close()

    caplog.clear()
    remainder_scheduler.check_due_tasks()

    assert "UPCOMING TASK REMAINDERS" not in caplog.text


def test_ineligible_tasks_are_not_reminded(
    test_session_factory,
    caplog,
):
    caplog.set_level(logging.INFO)

    db = test_session_factory()

    overdue_id = create_task(
        db,
        "Overdue task",
        datetime.now() - timedelta(minutes=5),
    )

    completed_id = create_task(
        db,
        "Completed task",
        datetime.now() + timedelta(minutes=5),
        status="Completed",
    )

    already_reminded_id = create_task(
        db,
        "Already reminded task",
        datetime.now() + timedelta(minutes=5),
        reminder_sent=True,
    )

    db.close()

    remainder_scheduler.check_due_tasks()

    db = test_session_factory()

    assert db.get(Task, overdue_id).reminder_sent is False
    assert db.get(Task, completed_id).reminder_sent is False
    assert db.get(Task, already_reminded_id).reminder_sent is True

    assert "UPCOMING TASK REMAINDERS" not in caplog.text

    db.close()
