"""Generate the deterministic I-06 engine/API benchmark evidence."""

from __future__ import annotations

import json
import platform
import statistics
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.data import build_database
from app.engine import DecisionEngine
from app.main import create_app
from app.repository import Repository

ROOT = Path(__file__).parents[1]
SEED = ROOT / "app" / "db" / "seed.synthetic.json"
OUTPUT = ROOT / "evidence" / "benchmark_i06.json"


def percentile_95(values: list[float]) -> float:
    return sorted(values)[94]


with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    database = temporary / "benchmark.sqlite3"
    build_database(SEED, database)
    engine_times = []
    with Repository(database) as repository:
        engine = DecisionEngine(repository)
        for _ in range(100):
            started = time.perf_counter()
            engine.recommend(["goal_alpha", "preference_beta"])
            engine_times.append((time.perf_counter() - started) * 1000)

    api_times = []
    with TestClient(create_app(SEED, temporary / "api.sqlite3")) as client:
        for _ in range(100):
            started = time.perf_counter()
            response = client.post("/api/recommend", json={"text": "goal alpha preference beta"})
            response.raise_for_status()
            api_times.append((time.perf_counter() - started) * 1000)

report = {
    "date": "2026-08-08",
    "runtime": platform.python_version(),
    "platform": platform.platform(),
    "runs": 100,
    "engine_p95_ms": round(percentile_95(engine_times), 3),
    "engine_mean_ms": round(statistics.mean(engine_times), 3),
    "engine_threshold_ms": 100,
    "api_p95_ms": round(percentile_95(api_times), 3),
    "api_mean_ms": round(statistics.mean(api_times), 3),
    "api_threshold_ms": 500,
}
OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
