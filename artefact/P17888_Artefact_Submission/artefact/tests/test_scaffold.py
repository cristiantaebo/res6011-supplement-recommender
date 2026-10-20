"""I-01 scaffold verification."""

from fastapi.testclient import TestClient

from app.main import app
from app.settings import DEFAULT_HOST, PROJECT_ID


client = TestClient(app)


def test_health_smoke() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "project_id": PROJECT_ID,
        "stage": "I-05",
    }


def test_scaffold_has_no_session_or_permissive_cors_headers() -> None:
    response = client.get("/health")

    assert "set-cookie" not in response.headers
    assert "access-control-allow-origin" not in response.headers
    assert DEFAULT_HOST == "127.0.0.1"
