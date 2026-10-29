from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
from sqlalchemy.pool import StaticPool

from main import app
from app.database.database import Base, get_db
from app.models.task import Task
from app.services.gemini_service import ExtractedTask

@pytest.fixture
def client():
    # Create an isolated in-memory database for each test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread":False},
        poolclass=StaticPool
    )

    TestingSessionlocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db= TestingSessionlocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(
        app, 
        raise_server_exceptions=False,
        ) as testclient:
        yield testclient

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

def mock_gemini(prompt):
    return ExtractedTask(
        title= "Prepare for FastAPI interview",
        category="Learning",
        priority="High",
        severity="High" 
    )

def test_create_task_from_prompt(client, monkeypatch):
    # Mock Gemini so the test does not call the real API.
    monkeypatch.setattr(
        "app.routers.task_router.extract_task_details",
        mock_gemini,
    )

    # Return a predictable deadline.
    expected_deadline = datetime(2026, 10, 16, 18, 0)

    monkeypatch.setattr(
        "app.routers.task_router.extract_due_date",
        lambda prompt: expected_deadline,
    )

    response = client.post(
        "/tasks/from-prompt",
        json={
            "prompt": "Prepare for my FastAPI interview by Friday"
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Prepare for FastAPI interview"
    assert data["category"] == "Learning"
    assert data["priority"] == "High"
    assert data["severity"] == "High"
    assert data["due_date"].startswith("2026-10-16T18:00:00")

    # Verify that the saved task can be retrieved.
    task_id = data["id"]

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == task_id


def test_create_task_without_deadline(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.task_router.extract_task_details",
        mock_gemini,
    )

    monkeypatch.setattr(
        "app.routers.task_router.extract_due_date",
        lambda prompt: None,
    )

    response = client.post(
        "/tasks/from-prompt",
        json={"prompt": "Review the project requirements"},
    )

    assert response.status_code == 201
    assert response.json()["due_date"] is None


def test_gemini_failure_returns_502(client, monkeypatch):
    def failing_gemini(prompt):
        raise RuntimeError("Simulated Gemini failure")

    monkeypatch.setattr(
        "app.routers.task_router.extract_task_details",
        failing_gemini,
    )

    response = client.post(
        "/tasks/from-prompt",
        json={"prompt": "Prepare for a Python interview"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Could not extract task details. Please try again."
    )


def test_blank_prompt_returns_422(client):
    response = client.post(
        "/tasks/from-prompt",
        json={"prompt": "   "},
    )

    assert response.status_code == 422

def test_oversized_prompt_returns_422(client):
    response = client.post(
        "/tasks/from-prompt",
        json={"prompt": "A" * 1001},
    )
    assert response.status_code == 422

def test_due_before_includes_tasks_selected_through_specified_date(client):
    """Include tasks due on or before the specified date."""

    def create_task(title, due_date=None):

        response = client.post(
            "/tasks",
            json={
                "original_prompt":title,
                "title": title,
                "category": "Work",
                "priority": "Medium",
                "severity": "Low",
                "due_date": due_date
            }
        )

        assert response.status_code == 200, response.text
        return response.json()

    # 1. Previous day task: should be included
    create_task(
        "Previous Day task",
        "2026-10-24T15:00:00"
    )

    # 2. Selected date at midnight: Should be included
    create_task(
        "Midnight task",
        "2026-10-25T00:00:00"
    )

    # 3. Selected date at 3Pm: should be included
    create_task(
        "Afternoon task",
        "2026-10-25T15:00:00"
    )

    # 4. Next day task: should be excluded
    create_task(
        "Next day task",
        "2026-10-26T00:00:00"
    )

    # 5. No deadline task: should be excluded
    create_task("No deadline task")

    response = client.get(
        "/tasks",
        params={ "due_before": "2026-10-25"}
    )

    assert response.status_code == 200

    returned_titles = {
        task["title"] for task in response.json()
    }

    assert "Previous Day task" in returned_titles
    assert "Midnight task" in returned_titles
    assert "Afternoon task" in returned_titles

    assert "Next day task" not in returned_titles
    assert "No deadline task" not in returned_titles

def test_missing_task_returns_404(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == ("Task with ID 9999 not found")

def test_invalid_task_priority_returns_422(client):
    response = client.post(
        "/tasks",
        json={
            "original_prompt":"Prepare a report",
            "title":"Prepare a report",
            "category":"Work",
            "priority":"Super High",
            "severity":"Medium",
        },
    )

    assert response.status_code == 422

def test_unexpected_server_error_return_safe_500(
        client,
        monkeypatch
):
    def failing_extraction_date(prompt):
        raise RuntimeError("Internal database details")

    monkeypatch.setattr(
        "app.routers.task_router.extract_due_date",
        failing_extraction_date,
    )

    response = client.post(
        "/tasks",
        json = {
            "original_prompt":"Prepare a document",
            "title": "Prepare a document",
            "category": "Work",
            "priority": "Medium",
            "severity": "Medium",
        }
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "An unhandled server error occurred."
    }
    assert "Internal database details" not in response.text

def test_database_commit_failure_triggers_rollback(
        client,
        monkeypatch
):
    rollback_called = False
    original_rollback = SQLAlchemySession.rollback

    def failing_commit(self):
        raise RuntimeError("Simulate database failure")

    def tracking_rollback(self):
        nonlocal rollback_called
        rollback_called = True
        original_rollback(self)

    monkeypatch.setattr(
        SQLAlchemySession,
        "commit",
        failing_commit,
    )

    monkeypatch.setattr(
        SQLAlchemySession,
        "rollback",
        tracking_rollback
    )

    response = client.post(
        "/tasks",
        json = {
            "original_prompt":"Prepare a document",
            "title": "Prepare a document",
            "category": "Work",
            "priority": "High",
            "severity": "Medium",
        }
    )

    assert response.status_code == 500
    assert rollback_called is True