import pytest
from fastapi.testclient import TestClient
from observability.server import app, init_db
import sqlite3
import json
import os

@pytest.fixture(autouse=True)
def clean_db():
    if os.path.exists("telemetry.db"):
        os.remove("telemetry.db")
    init_db()

def test_get_sessions_empty():
    client = TestClient(app)
    response = client.get("/sessions")
    assert response.status_code == 200
    assert response.json() == []

def test_save_session_and_fetch():
    client = TestClient(app)
    session_data = {
        "type": "init_session",
        "data": {
            "session_id": "test_id",
            "url": "http://test.com",
            "bdd_goal": "Test Goal"
        }
    }
    # Simulando o WS salvando diretamente via função auxiliar para teste unitário
    from observability.server import save_session
    save_session(session_data["data"])

    response = client.get("/sessions")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "test_id"

def test_save_step_and_fetch():
    client = TestClient(app)
    from observability.server import save_session, save_step

    save_session({"session_id": "s1", "url": "url", "bdd_goal": "goal"})

    step_data = {
        "session_id": "s1",
        "step_number": 1,
        "state_hash": "hash123",
        "screenshot_base64": "img_data",
        "action": {"type": "CLICK", "element_id": 5},
        "observation": {"top_candidates": []}
    }
    save_step(step_data)

    response = client.get("/sessions/s1/steps")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["step_number"] == 1
    assert response.json()[0]["state_hash"] == "hash123"
