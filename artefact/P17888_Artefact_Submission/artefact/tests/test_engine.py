import copy
import json
import time
from pathlib import Path

import pytest

from app.data import build_database
from app.engine import DecisionEngine, EngineDataError
from app.repository import Repository

ROOT = Path(__file__).parents[1]
SEED = ROOT / "app" / "db" / "seed.synthetic.json"


@pytest.fixture()
def repository(tmp_path: Path):
    database = tmp_path / "engine.sqlite3"
    build_database(SEED, database)
    with Repository(database) as repo:
        yield repo


def test_normal_scoring_and_stored_explanations(repository):
    result = DecisionEngine(repository).recommend(["goal_alpha", "preference_beta"])
    assert result == {
        "status": "OK",
        "applied_exclusions": [],
        "recommendations": [
            {"product_id": "p001", "name": "Option One", "summary": "Neutral predefined option one.", "recommendation_text": "Option One matches the selected predefined criteria.", "recipe_text": "Follow the predefined directions for Option One.", "score": 8, "reasons": [{"rule_id": "rule_goal_alpha", "label": "Goal Alpha", "text": "Matches Goal Alpha.", "points": 5}, {"rule_id": "rule_preference_beta", "label": "Preference Beta", "text": "Matches Preference Beta.", "points": 3}]},
            {"product_id": "p002", "name": "Option Two", "summary": "Neutral predefined option two.", "recommendation_text": "Option Two matches the selected predefined criteria.", "recipe_text": "Follow the predefined directions for Option Two.", "score": 8, "reasons": [{"rule_id": "rule_goal_alpha", "label": "Goal Alpha", "text": "Matches Goal Alpha.", "points": 5}, {"rule_id": "rule_preference_beta", "label": "Preference Beta", "text": "Matches Preference Beta.", "points": 3}]},
            {"product_id": "p005", "name": "Option Five", "summary": "Neutral predefined option five.", "recommendation_text": "Option Five matches the selected predefined criteria.", "recipe_text": "Follow the predefined directions for Option Five.", "score": 5, "reasons": [{"rule_id": "rule_goal_alpha", "label": "Goal Alpha", "text": "Matches Goal Alpha.", "points": 5}]},
        ],
        "data_version": "synthetic-v1",
        "message": "Predefined options ranked by the selected criteria.",
    }


def test_tie_breaks_by_matched_count_then_product_id(repository):
    result = DecisionEngine(repository).recommend(["goal_beta", "preference_alpha", "format_beta"])
    assert [(item["product_id"], item["score"], len(item["reasons"])) for item in result["recommendations"]] == [
        ("p004", 5, 2),
        ("p003", 5, 1),
    ]
    tied = DecisionEngine(repository).recommend(["goal_alpha", "preference_beta"])
    assert [item["product_id"] for item in tied["recommendations"][:2]] == ["p001", "p002"]


def test_exclusion_is_applied_before_ranking(repository):
    result = DecisionEngine(repository).recommend(["goal_alpha", "preference_gamma"])
    assert "p005" not in [item["product_id"] for item in result["recommendations"]]
    assert result["applied_exclusions"] == [{"product_id": "p005", "term_id": "preference_gamma", "relationship": "excludes"}]


@pytest.mark.parametrize("terms", [[], ["unknown"], ["goal_gamma"]])
def test_no_match_is_controlled(repository, terms):
    assert DecisionEngine(repository).recommend(terms) == {"status": "NO_MATCH", "data_version": "synthetic-v1", "applied_exclusions": [], "recommendations": [], "message": "No predefined option matches the selected criteria."}


def test_repeatability_is_byte_equivalent(repository):
    engine = DecisionEngine(repository)
    baseline = json.dumps(engine.recommend(["preference_beta", "goal_alpha"]), sort_keys=True)
    assert all(json.dumps(engine.recommend(["goal_alpha", "preference_beta"]), sort_keys=True) == baseline for _ in range(100))


class MemoryRepository:
    def __init__(self, count=100, bad_rules=False):
        self.count = count
        self.bad_rules = bad_rules
    def taxonomy_terms(self):
        return [{"term_id": "goal_alpha", "category": "wellness_goal", "label": "Goal Alpha"}]
    def active_version(self):
        return "memory-v1"
    def active_rules(self, term_ids):
        return [{"rule_id": "rule_goal_alpha", "term_id": "goal_alpha", "relationship": "matches", "weight": 99 if self.bad_rules else 5, "predefined_reason_template": "Stored reason.", "version_id": "memory-v1"}]
    def active_products(self):
        return [{"product_id": f"p{i:03}", "name": f"Option {i}", "summary": "Stored summary.", "recommendation_text": "Stored neutral explanation.", "recipe_text": "Stored directions."} for i in range(self.count)]
    def product_relations(self, term_ids):
        return [{"product_id": f"p{i:03}", "term_id": "goal_alpha", "relation": "matches", "category": "wellness_goal"} for i in range(self.count)]


def test_hundred_product_decision_under_100ms():
    engine = DecisionEngine(MemoryRepository())
    timings = []
    for _ in range(100):
        started = time.perf_counter()
        result = engine.recommend(["goal_alpha"])
        timings.append((time.perf_counter() - started) * 1000)
    p95_ms = sorted(timings)[94]
    assert p95_ms < 100
    assert [item["product_id"] for item in result["recommendations"]] == ["p000", "p001", "p002"]


def test_invalid_stored_rules_fail_closed():
    with pytest.raises(EngineDataError):
        DecisionEngine(MemoryRepository(bad_rules=True)).recommend(["goal_alpha"])
