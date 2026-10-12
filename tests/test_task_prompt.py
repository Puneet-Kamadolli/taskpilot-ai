from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

    with TestClient(app) as testclient:
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