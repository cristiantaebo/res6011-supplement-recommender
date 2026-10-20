import copy
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from app.data import DataValidationError, build_database, load_seed, validate_seed
from app.repository import Repository

ROOT = Path(__file__).parents[1]
SEED = ROOT / "app" / "db" / "seed.synthetic.json"
SCHEMA = ROOT / "app" / "db" / "schema.sql"
EXPECTED_SEED_SHA256 = "906549b7a9b27c3de27bfd8c94435c42f538ac2e2f6521d8b1ce85a6a486c40d"


@pytest.fixture()
def database(tmp_path: Path) -> Path:
    path = tmp_path / "fixture.sqlite3"
    build_database(SEED, path, SCHEMA)
    return path


def test_schema_and_deterministic_seed(database: Path):
    with sqlite3.connect(database) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert tables == {"dataset_version", "source_record", "taxonomy_term", "term_alias", "product", "recipe", "product_term", "scoring_rule", "boundary_pattern"}
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute("SELECT COUNT(*) FROM dataset_version WHERE status='active'").fetchone()[0] == 1


def test_repository_filters_and_orders_products(database: Path):
    with Repository(database) as repository:
        assert [item["product_id"] for item in repository.active_products()] == ["p001", "p002", "p003", "p004", "p005"]
        assert repository.active_version() == "synthetic-v1"
        assert [(rule["rule_id"], rule["weight"]) for rule in repository.active_rules(["goal_alpha", "preference_beta", "format_beta"])] == [("rule_format_beta", 2), ("rule_goal_alpha", 5), ("rule_preference_beta", 3)]


def test_constraints_reject_bad_weights_foreign_keys_and_second_active(database: Path):
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO scoring_rule VALUES ('bad','synthetic-v1','goal_alpha','matches',11,'x',1,'synthetic_001')")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO term_alias VALUES ('bad', 'missing', 'x', 0)")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO dataset_version VALUES ('v2','2026-08-08','active','hash','x')")


def test_seed_provenance_and_content_policy():
    data = load_seed(SEED)
    validate_seed(data)
    assert {source["source_type"] for source in data["sources"]} == {"synthetic"}
    assert all(source["synthetic"] is True for source in data["sources"])
    assert all("kaggle" not in (source["public_url"] + source["evidence_path"]).lower() and "opendata" not in (source["public_url"] + source["evidence_path"]).lower() for source in data["sources"])
    controlled = json.dumps(data["products"]).lower()
    assert not any(claim in controlled for claim in ("cures ", "treats ", "diagnoses ", "prevents disease"))


def test_seed_hash_is_reviewed_and_stable():
    assert hashlib.sha256(SEED.read_bytes()).hexdigest() == EXPECTED_SEED_SHA256


def test_parameterised_input_cannot_mutate_database(database: Path):
    attack = "goal_alpha'); DROP TABLE product;--"
    with Repository(database) as repository:
        assert repository.product_relations([attack]) == []
        assert len(repository.active_products()) == 5


def test_invalid_seed_fails_closed_without_database(tmp_path: Path):
    data = copy.deepcopy(load_seed(SEED))
    data["sources"][0]["public_url"] = "https://kaggle.example/test"
    invalid_seed = tmp_path / "invalid.json"
    invalid_seed.write_text(json.dumps(data), encoding="utf-8")
    database = tmp_path / "must-not-exist.sqlite3"
    with pytest.raises(DataValidationError):
        build_database(invalid_seed, database, SCHEMA)
    assert not database.exists()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data["products"][0].update({"predefined_summary": ""}),
        lambda data: data["terms"].append(copy.deepcopy(data["terms"][0])),
        lambda data: data["product_terms"][0].update({"term_id": "missing"}),
        lambda data: data["scoring_rules"][0].update({"weight": -1}),
    ],
)
def test_invalid_record_fixtures_are_rejected(mutate):
    data = copy.deepcopy(load_seed(SEED))
    mutate(data)
    with pytest.raises(DataValidationError):
        validate_seed(data)
