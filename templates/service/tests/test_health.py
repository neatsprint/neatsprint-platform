from fastapi.testclient import TestClient

from __PACKAGE__.main import app


def test_root_identifies_service() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "__SERVICE__"


def test_healthz() -> None:
    response = TestClient(app).get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readyz_without_database_is_ready() -> None:
    response = TestClient(app).get("/readyz")
    assert response.status_code == 200


def test_ping() -> None:
    response = TestClient(app).get("/api/v1/__SERVICE__/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong", "service": "__SERVICE__"}


def test_request_id_is_echoed() -> None:
    response = TestClient(app).get("/healthz", headers={"X-Request-ID": "req-test"})
    assert response.headers["x-request-id"] == "req-test"
