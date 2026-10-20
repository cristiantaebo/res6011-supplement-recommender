from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

ROOT = Path(__file__).parents[1]
SEED = ROOT / "app" / "db" / "seed.synthetic.json"
STATIC = ROOT / "app" / "static"


@pytest.fixture()
def client(tmp_path: Path):
    app = create_app(SEED, tmp_path / "api.sqlite3")
    with TestClient(app) as test_client:
        yield test_client


def test_entry_and_taxonomy_are_same_origin_and_predefined(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Informational prototype boundary" in response.text
    taxonomy = client.get("/api/taxonomy")
    assert taxonomy.status_code == 200
    assert taxonomy.json()["data_version"] == "synthetic-v1"
    assert len(taxonomy.json()["terms"]) == 8
    assert "set-cookie" not in response.headers
    assert "access-control-allow-origin" not in response.headers


def test_valid_supported_request_returns_stored_ranked_explanations(client):
    response = client.post("/api/recommend", json={"text": "goal alpha preference beta"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["data_version"] == "synthetic-v1"
    assert [item["product_id"] for item in data["recommendations"]] == ["p001", "p002", "p005"]
    assert data["recommendations"][0]["recommendation_text"] == "Option One matches the selected predefined criteria."
    assert data["recommendations"][0]["recipe_text"] == "Follow the predefined directions for Option One."
    assert sum(reason["points"] for reason in data["recommendations"][0]["reasons"]) == data["recommendations"][0]["score"]
    assert "informational and non-medical" in data["disclaimer"]


@pytest.mark.parametrize("payload", [{"text": ""}, {"text": "   "}, {"text": "x" * 501}, {"text": 7}, {"text": "goal alpha", "unexpected": True}])
def test_malformed_requests_receive_controlled_422(client, payload):
    assert client.post("/api/recommend", json=payload).status_code == 422


def test_length_boundaries_are_accepted(client):
    assert client.post("/api/recommend", json={"text": "x"}).status_code == 200
    assert client.post("/api/recommend", json={"text": "x" * 500}).status_code == 200


def test_ambiguity_unsupported_no_match_and_boundary_have_no_invented_results(client):
    cases = {
        "shared choice": "AMBIGUOUS_INPUT",
        "unlisted criterion": "UNSUPPORTED_INPUT",
        "goal gamma": "NO_MATCH",
        "goal alpha diagnose": "BOUNDARY",
    }
    for text, status in cases.items():
        data = client.post("/api/recommend", json={"text": text}).json()
        assert data["status"] == status
        assert data.get("recommendations", []) == []
        assert "informational and non-medical" in data["disclaimer"]


def test_ui_static_accessibility_and_reset_contract():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (STATIC / "styles.css").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    for token in ("<header", "<main", "<footer", "<h1", "<label for=\"request-text\"", "aria-live=\"polite\"", "maxlength=\"500\"", "type=\"submit\""):
        assert token in html
    assert ":focus-visible" in css
    assert "@media (max-width: 42rem)" in css
    assert "prefers-reduced-motion" in css
    assert "function resetInterface()" in javascript
    assert "localStorage" not in javascript and "sessionStorage" not in javascript and "document.cookie" not in javascript


def test_openapi_has_only_intended_api_surface(client):
    schema = client.get("/openapi.json").json()
    assert set(schema["paths"]) == {"/health", "/api/taxonomy", "/api/recommend"}
