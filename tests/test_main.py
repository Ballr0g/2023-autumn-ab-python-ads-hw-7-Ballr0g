from typing import Literal

import pytest
from httpx import Response

from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


HttpMethod = Literal["POST", "GET", "PUT", "PATCH"]


def test_root_message_ok(test_client: TestClient) -> None:
    response: Response = run_base_response_checks("GET", "/", 200, test_client)
    assert response.json()["message"] == "Hello! This is the fraud detector."


@pytest.mark.parametrize(
    ("http_method", "method_url", "expected_status"),
    [
        ("GET", "/number_of_entries", 200),
        ("POST", "/number_of_entries", 405),
    ]
)
def test_simple_api_structure(
        http_method: HttpMethod,
        method_url: str,
        expected_status: int,
        test_client: TestClient
) -> None:
    run_base_response_checks(http_method, method_url, expected_status, test_client)


def run_base_response_checks(
        http_method: HttpMethod,
        method_url: str,
        expected_status: int,
        test_client: TestClient
) -> Response:
    response: Response = test_client.request(method=http_method, url=method_url)
    assert response.status_code == expected_status
    assert "application/json" in response.headers["content-type"]

    return response
