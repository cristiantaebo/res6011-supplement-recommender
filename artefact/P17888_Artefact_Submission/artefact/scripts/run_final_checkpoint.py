"""Run and persist the final predefined end-to-end checkpoint scenarios."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.data import load_seed
from app.main import create_app
from app.settings import DEFAULT_SEED_PATH

ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / "evidence" / "final_checkpoint_run.json"
SCENARIOS = [
    ("supported", "mixable option vegetarian labelled powder", "OK"),
    ("alternative_phrasing", "mixable vegetarian powder", "OK"),
    ("no_match", "tablet option", "NO_MATCH"),
    ("ambiguous", "portable option", "AMBIGUOUS_INPUT"),
    ("unsupported", "unlisted criterion", "UNSUPPORTED_INPUT"),
    ("medical_boundary", "mixable option diagnose", "BOUNDARY"),
]

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / "checkpoint.sqlite3"
    with TestClient(create_app(DEFAULT_SEED_PATH, database)) as client:
        before_hash = hashlib.sha256(database.read_bytes()).hexdigest()
        results = []
        for name, text, expected in SCENARIOS:
            response = client.post("/api/recommend", json={"text": text})
            payload = response.json()
            actual = payload["status"]
            if response.status_code != 200 or actual != expected:
                raise RuntimeError(f"scenario failed: {name}")
            results.append(
                {
                    "scenario": name,
                    "predefined_input": text,
                    "http_status": response.status_code,
                    "status": actual,
                    "product_ids": [item["product_id"] for item in payload.get("recommendations", [])],
                    "data_version": payload.get("data_version"),
                }
            )
        malformed = client.post("/api/recommend", json={"text": ""})
        if malformed.status_code != 422:
            raise RuntimeError("malformed input did not fail validation")
        canonical_payloads = [client.post("/api/recommend", json={"text": "mixable option vegetarian labelled powder"}).json() for _ in range(100)]
        hashes = {hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest() for payload in canonical_payloads}
        after_hash = hashlib.sha256(database.read_bytes()).hexdigest()

seed = load_seed(DEFAULT_SEED_PATH)
stored_products = {item["product_id"]: item for item in seed["products"]}
for payload in canonical_payloads:
    for recommendation in payload["recommendations"]:
        stored = stored_products[recommendation["product_id"]]
        if recommendation["name"] != stored["display_name"] or recommendation["summary"] != stored["predefined_summary"] or recommendation["recommendation_text"] != stored["predefined_recommendation_text"]:
            raise RuntimeError("output differs from predefined product fields")

report = {
    "date": "2026-08-20",
    "data_version": "curated-v1",
    "scenarios": results,
    "malformed_empty_http_status": malformed.status_code,
    "repeat_runs": 100,
    "unique_canonical_hashes": len(hashes),
    "database_hash_unchanged": before_hash == after_hash,
    "all_output_products_predefined": True,
    "result": "PASS",
}
if len(hashes) != 1 or before_hash != after_hash:
    raise RuntimeError("determinism or database immutability failed")
OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
