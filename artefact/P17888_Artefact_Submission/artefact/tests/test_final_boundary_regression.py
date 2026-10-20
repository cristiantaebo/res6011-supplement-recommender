"""Late FR-011 request-policy regressions; all original tests remain unchanged."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.data import build_database
from app.main import create_app
from app.pipeline import CorePipeline
from app.repository import Repository

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize("seed,goal", [("curated", "mixable option"), ("synthetic", "goal alpha")])
@pytest.mark.parametrize("noun,code", [("diagnosis", "DIAGNOSTIC_REQUEST"), ("treatment", "TREATMENT_REQUEST")])
def test_request_boundary_rejects_demonstrated_noun_forms(tmp_path, seed, goal, noun, code):
    database = tmp_path / "boundary.sqlite3"
    build_database(ROOT / f"app/db/seed.{seed}.json", database)
    with Repository(database) as repository:
        result = CorePipeline(repository).process(f"{goal} {noun}")
    assert result["status"] == "BOUNDARY"
    assert result["boundary_code"] == code
    assert result.get("recommendations", []) == []
    assert "matched_terms" not in result
    assert "cannot diagnose or provide medical advice" in result["message"]


@pytest.mark.parametrize("noun,code", [("diagnosis", "DIAGNOSTIC_REQUEST"), ("treatment", "TREATMENT_REQUEST")])
def test_api_rejects_demonstrated_noun_forms(tmp_path, noun, code):
    with TestClient(create_app(ROOT / "app/db/seed.curated.json", tmp_path / "api.sqlite3")) as client:
        response = client.post("/api/recommend", json={"text": f"mixable option {noun}"})
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "BOUNDARY"
    assert result["boundary_code"] == code
    assert result.get("recommendations", []) == []
    assert "disclaimer" in result


def test_alias_extraction_does_not_claim_rejection_of_every_unknown_token(tmp_path):
    with TestClient(create_app(ROOT / "app/db/seed.curated.json", tmp_path / "unknown.sqlite3")) as client:
        result = client.post("/api/recommend", json={"text": "mixable option unlisted criterion"}).json()
    assert result["status"] == "OK"
    assert result["recommendations"][0]["product_id"] == "real_myprotein_whey_powder"
