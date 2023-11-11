from app.main import app
from fastapi.testclient import TestClient

test_client: TestClient = TestClient(app)


def test_root_message_ok() -> None:
    response = test_client.get("/")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert response.json()["message"] == "Hello! This is the fraud detector."


def test_number_of_entries_ok() -> None:
    response = test_client.get("/number_of_entries")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


def test_number_of_entries_not_allowed() -> None:
    response = test_client.post("/number_of_entries")
    assert response.status_code == 405
    assert "application/json" in response.headers["content-type"]
