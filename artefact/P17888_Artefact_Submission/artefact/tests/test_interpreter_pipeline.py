import hashlib
import json
from pathlib import Path

import pytest

from app.data import build_database
from app.interpreter import ControlledInterpreter, normalize_text
from app.pipeline import CorePipeline
from app.repository import Repository

ROOT = Path(__file__).parents[1]
SEED = ROOT / "app" / "db" / "seed.synthetic.json"


@pytest.fixture()
def database(tmp_path: Path) -> Path:
    path = tmp_path / "pipeline.sqlite3"
    build_database(SEED, path)
    return path


@pytest.fixture()
def repository(database: Path):
    with Repository(database) as repo:
        yield repo


def test_unicode_case_punctuation_and_whitespace_normalisation(repository):
    result = ControlledInterpreter(repository).interpret("  ＧＯＡＬ—ＡＬＰＨＡ,   preference BETA! ")
    assert result["status"] == "OK"
    assert [(item["term_id"], item["matched_phrase"]) for item in result["matched_terms"]] == [("goal_alpha", "goal alpha"), ("preference_beta", "preference beta")]


def test_supported_synonym_maps_to_controlled_term(repository):
    result = ControlledInterpreter(repository).interpret("alpha objective")
    assert result["status"] == "OK"
    assert result["matched_terms"][0]["term_id"] == "goal_alpha"


def test_equal_alias_collision_is_ambiguous_and_stable(repository):
    result = ControlledInterpreter(repository).interpret("shared choice")
    assert result == {
        "status": "AMBIGUOUS_INPUT",
        "message": "More than one predefined criterion is equally applicable; select one.",
        "category": "wellness_goal",
        "choices": [{"term_id": "goal_beta", "label": "Goal Beta"}, {"term_id": "goal_gamma", "label": "Goal Gamma"}],
    }


def test_missing_goal_returns_controlled_goal_choices(repository):
    result = ControlledInterpreter(repository).interpret("preference alpha, format beta")
    assert result["status"] == "AMBIGUOUS_INPUT"
    assert result["category"] == "wellness_goal"
    assert [item["term_id"] for item in result["choices"]] == ["goal_alpha", "goal_beta", "goal_gamma"]


def test_unsupported_empty_and_malformed_inputs(repository):
    interpreter = ControlledInterpreter(repository)
    unsupported = interpreter.interpret("unlisted criterion")
    assert unsupported["status"] == "UNSUPPORTED_INPUT"
    assert [item["term_id"] for item in unsupported["choices"]] == ["goal_alpha", "goal_beta", "goal_gamma", "preference_alpha", "preference_beta", "preference_gamma", "format_alpha", "format_beta"]
    assert interpreter.interpret("  ...  ")["status"] == "EMPTY_INPUT"
    assert interpreter.interpret(None)["status"] == "INVALID_INPUT"
    assert interpreter.interpret("x" * 501)["status"] == "INVALID_INPUT"


@pytest.mark.parametrize("text,pattern", [("Can you diagnose this?", "b001"), ("please TREAT this", "b002"), ("an emergency", "b003"), ("medical advice", "b004")])
def test_boundary_precedes_supported_aliases(repository, text, pattern):
    result = ControlledInterpreter(repository).interpret(f"goal alpha {text}")
    assert result["status"] == "BOUNDARY"
    assert result["pattern_id"] == pattern
    assert result["boundary_code"].endswith("REQUEST")
    assert "matched_terms" not in result


def test_boundary_matching_uses_whole_phrases(repository):
    result = ControlledInterpreter(repository).interpret("goal alpha treatment")
    assert result["status"] == "OK"


def test_core_pipeline_is_exact_and_contains_no_raw_input(repository):
    user_text = "GOAL ALPHA and preference beta"
    result = CorePipeline(repository).process(user_text)
    assert result["status"] == "OK"
    assert [item["product_id"] for item in result["recommendations"]] == ["p001", "p002", "p005"]
    assert user_text not in json.dumps(result)
    assert "normalized_input" not in result and "raw_input" not in result


def test_pipeline_repeatability_and_no_database_persistence(database: Path):
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    with Repository(database) as repository:
        pipeline = CorePipeline(repository)
        baseline = json.dumps(pipeline.process("goal alpha preference beta"), sort_keys=True)
        assert all(json.dumps(pipeline.process("goal alpha preference beta"), sort_keys=True) == baseline for _ in range(100))
    after = hashlib.sha256(database.read_bytes()).hexdigest()
    assert before == after


def test_normalizer_is_deterministic():
    assert normalize_text(" A—B\tC ") == "a b c"
