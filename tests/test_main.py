import os
from datetime import datetime
from typing import Any, Generator, Literal

import pytest
from app import models
from app.main import app as test_app
from app.main import get_db
from app.schemas import BaseLine, ErrorType
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import Engine, create_engine, Table, insert, Insert
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer


class FixedPostgresContainer(PostgresContainer):
    """
    This wrapper type was the only way to fix testcontainers indefinitely loading on Windows...
    """

    def get_connection_url(self, host: Any = None) -> str:
        if os.name == "nt":
            return super().get_connection_url().replace("localnpipe", "localhost")
        return super().get_connection_url()


@pytest.fixture(scope="module")
def postgres_version() -> str:
    return "postgres:15.0"


@pytest.fixture(scope="module")
def postgres_test_container(postgres_version: str) -> PostgresContainer:
    container: PostgresContainer = FixedPostgresContainer(postgres_version)
    try:
        container.start()
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="module")
def postgres_test_engine(postgres_test_container: PostgresContainer) -> Engine:
    return create_engine(postgres_test_container.get_connection_url())


@pytest.fixture(scope="module")
def postgres_test_session(postgres_test_engine: Engine) -> sessionmaker[Session]:
    pg_session_local: sessionmaker[Session] = sessionmaker(
        autocommit=False, autoflush=False, bind=postgres_test_engine
    )
    return pg_session_local


@pytest.fixture(scope="module")
def postgres_test_app(postgres_test_session: sessionmaker[Session]) -> FastAPI:
    def get_db_test_override() -> Generator[Session, Any, None]:
        db = postgres_test_session()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides = {get_db: get_db_test_override}
    return test_app


@pytest.fixture()
def _setup_postgres_data(postgres_test_engine: Engine) -> None:
    models.Base.metadata.drop_all(bind=postgres_test_engine)
    models.Base.metadata.create_all(bind=postgres_test_engine)

    table: Table = Table("messages", models.Base.metadata)
    messages: list[dict[str, str | datetime]] = [
        {
            "input_text": "ДЗ не стоит сдавать в последний день",
            "result_prediction": "clean",
            "baseline_used": "first_hypothesis",
            "execution_date": datetime(year=2023, month=11, day=25, hour=8),
        },
        {
            "input_text": "телеграм",
            "result_prediction": "fraud",
            "baseline_used": "first_hypothesis",
            "execution_date": datetime(year=2023, month=11, day=25, hour=10),
        },
        {
            "input_text": "Мороз и солнце",
            "result_prediction": "clean",
            "baseline_used": "constant_clean",
            "execution_date": datetime(year=2023, month=11, day=24, hour=8),
        }
    ]

    with postgres_test_engine.connect() as connection:
        insertion: Insert = insert(table).values(messages)
        connection.execute(insertion)
        connection.commit()


@pytest.fixture(scope="module")
def client_for_tests(postgres_test_app: FastAPI) -> TestClient:
    with TestClient(postgres_test_app) as test_client:
        return test_client


HttpMethod = Literal["POST", "GET", "PUT", "PATCH"]


def test_root_message_ok(client_for_tests: TestClient) -> None:
    response: Response = run_base_response_checks("GET", "/", 200, client_for_tests)
    assert response.json()["message"] == "Hello! This is the fraud detector."


@pytest.mark.usefixtures("_setup_postgres_data")
@pytest.mark.parametrize(
    ("http_method", "method_url", "expected_status"),
    [
        ("GET", "/number_of_entries", 200),
        ("POST", "/number_of_entries", 405),
    ],
)
def test_simple_api_structure(
    http_method: HttpMethod,
    method_url: str,
    expected_status: int,
    client_for_tests: TestClient,
) -> None:
    run_base_response_checks(http_method, method_url, expected_status, client_for_tests)


@pytest.mark.parametrize(
    ("input_error_type", "expected_error_cost"),
    [
        ("false-positive", 10_000),
        ("false-negative", 75_000),
    ],
)
def test_get_cost_by_error_type(
    input_error_type: ErrorType, expected_error_cost: int, client_for_tests: TestClient
) -> None:
    response: Response = run_base_response_checks(
        "GET", f"/cost/{input_error_type}", 200, client_for_tests
    )
    assert response.json()["errorCost"] == expected_error_cost


@pytest.mark.parametrize(
    ("input_baseline", "expected_baseline_loss"),
    [
        ("constant_fraud", 1_900_000_000.0),
        ("constant_clean", 750_000_000.0),
        ("first_hypothesis", 644_850_000.0),
    ],
)
def test_get_loss_by_baseline(
    input_baseline: BaseLine, expected_baseline_loss: int, client_for_tests: TestClient
) -> None:
    response: Response = run_base_response_checks(
        "GET", f"/loss/{input_baseline}", 200, client_for_tests
    )
    assert response.json()["baseDailyLineLoss"] == expected_baseline_loss


@pytest.mark.usefixtures("_setup_postgres_data")
@pytest.mark.parametrize(
    ("input_baseline", "expected_message"),
    [
        (
                "first_hypothesis",
                {
                    "input_text": "телеграм",
                    "prediction_result": "fraud",
                    "baseline_used": "first_hypothesis",
                    "execution_date": "2023-11-25T10:00:00",
                },
        ),
        (
                "constant_clean",
                {
                    "input_text": "Мороз и солнце",
                    "prediction_result": "clean",
                    "baseline_used": "constant_clean",
                    "execution_date": "2023-11-24T08:00:00",
                },
        ),
    ],
)
def test_get_latest_entry_200(
        input_baseline: BaseLine,
        expected_message: dict[str, str],
        client_for_tests: TestClient
) -> None:
    response: Response = run_base_response_checks(
        "GET", f"/latest_entry/{input_baseline}", 200, client_for_tests
    )

    assert response.json()["baseline_used"] == expected_message["baseline_used"]
    assert response.json()["prediction_result"] == expected_message["prediction_result"]
    assert response.json()["baseline_used"] == expected_message["baseline_used"]
    assert response.json()["execution_date"] == expected_message["execution_date"]


@pytest.mark.usefixtures("_setup_postgres_data")
def test_get_latest_entry_404(client_for_tests: TestClient) -> None:
    run_base_response_checks(
        "GET", "/latest_entry/constant_fraud", 404, client_for_tests
    )


@pytest.mark.usefixtures("_setup_postgres_data")
def test_get_number_of_entries(client_for_tests: TestClient) -> None:
    response: Response = run_base_response_checks(
        "GET", "/number_of_entries", 200, client_for_tests
    )

    assert response.json()["constant_clean"] == 1
    assert response.json()["first_hypothesis"] == 2

    assert "constant_fraud" not in response.json()


def run_base_response_checks(
    http_method: HttpMethod, method_url: str, expected_status: int, client: TestClient
) -> Response:
    response: Response = client.request(method=http_method, url=method_url)
    assert response.status_code == expected_status
    assert "application/json" in response.headers["content-type"]

    return response
