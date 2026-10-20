import ast
import sqlite3
from pathlib import Path

from app.data import build_database
from app.main import app
from app.pipeline import CorePipeline
from app.repository import Repository

ROOT = Path(__file__).parents[1]
SEED = ROOT / "app" / "db" / "seed.synthetic.json"


def test_i05_has_only_approved_route_and_ui_surface():
    routes = {route.path for route in app.routes}
    assert routes == {"/", "/api/recommend", "/api/taxonomy", "/docs", "/docs/oauth2-redirect", "/health", "/openapi.json", "/redoc", "/static"}
    assert (ROOT / "app" / "static").is_dir()
    assert not (ROOT / "app" / "templates").exists()


def test_checkpoint_has_no_identity_session_or_history_schema(tmp_path: Path):
    database = tmp_path / "surface.sqlite3"
    build_database(SEED, database)
    with sqlite3.connect(database) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert not tables.intersection({"account", "user", "profile", "session", "conversation", "history", "cookie"})


def test_route_layer_contains_no_sql_or_scoring_logic():
    route_source = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "sqlite" not in route_source.lower()
    assert "score" not in route_source.lower()
    assert "DecisionEngine" not in route_source


def test_result_exposes_version_and_exact_rule_contributions(tmp_path: Path):
    database = tmp_path / "explanation.sqlite3"
    build_database(SEED, database)
    with Repository(database) as repository:
        result = CorePipeline(repository).process("goal alpha preference beta")
    assert result["data_version"] == "synthetic-v1"
    for recommendation in result["recommendations"]:
        assert recommendation["score"] == sum(reason["points"] for reason in recommendation["reasons"])
        assert all(set(reason) == {"rule_id", "label", "text", "points"} for reason in recommendation["reasons"])


def test_core_modules_import_no_network_clock_or_randomness():
    forbidden = {"requests", "httpx", "random", "secrets", "time", "socket", "openai"}
    found = set()
    for module in ("engine.py", "interpreter.py", "pipeline.py"):
        path = ROOT / "app" / module
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module.split(".")[0])
    assert found.isdisjoint(forbidden)
