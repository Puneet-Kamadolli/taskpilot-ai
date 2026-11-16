import logging

import pytest

from fastapi.testclient import TestClient

from main import app

@pytest.fixture
def client():
    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as test_client:
        yield test_client

def test_successful_request_is_logged(client, caplog):
    with caplog.at_level(logging.INFO,logger="main"):
        response = client.get("/")

    assert response.status_code == 200
    assert "API Request" in caplog.text
    assert "method=GET" in caplog.text
    assert "url=/" in caplog.text
    assert "status_code=200" in caplog.text

def test_not_found_request_is_logged(client, caplog):
    with caplog.at_level(logging.INFO, logger="main"):
        response = client.get("/nonexistent")

    assert response.status_code == 404
    assert "API Request" in caplog.text
    assert "method=GET" in caplog.text
    assert "url=/nonexistent" in caplog.text
    assert "status_code=404" in caplog.text

def test_request_duration_is_logged(client, caplog):
    with caplog.at_level(logging.INFO, logger="main"):
        response = client.get("/")

    assert response.status_code == 200
    assert "duration_ms=" in caplog.text