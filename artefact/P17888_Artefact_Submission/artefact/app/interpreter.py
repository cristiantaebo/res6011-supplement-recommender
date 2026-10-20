"""Controlled phrase interpreter; it never returns or stores free-text input."""

from __future__ import annotations

import re
import unicodedata
from typing import Protocol


MAX_INPUT_LENGTH = 500
CATEGORY_ORDER = {"wellness_goal": 0, "preference": 1, "format": 2}


class InterpreterRepository(Protocol):
    def aliases(self) -> list[dict]: ...
    def boundary_patterns(self) -> list[dict]: ...
    def taxonomy_terms(self) -> list[dict]: ...


def normalize_text(value: str) -> str:
    normal = unicodedata.normalize("NFKC", value).lower()
    separated = "".join(character if character.isalnum() or character.isspace() else " " for character in normal)
    return " ".join(separated.split())


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"(?:^|\s){re.escape(phrase)}(?:$|\s)", text) is not None


class ControlledInterpreter:
    def __init__(self, repository: InterpreterRepository):
        self.repository = repository

    def interpret(self, user_input: object) -> dict:
        if not isinstance(user_input, str) or len(user_input) > MAX_INPUT_LENGTH:
            return {"status": "INVALID_INPUT", "message": "Input must be text no longer than 500 characters."}
        normalized = normalize_text(user_input)
        if not normalized:
            return {"status": "EMPTY_INPUT", "message": "Enter a supported predefined goal."}

        for boundary in self.repository.boundary_patterns():
            phrase = normalize_text(boundary["phrase"])
            if _contains_phrase(normalized, phrase):
                return {"status": "BOUNDARY", "pattern_id": boundary["pattern_id"], "boundary_code": boundary["boundary_code"], "message": boundary["response_text"]}

        candidates: dict[str, list[dict]] = {}
        for alias in self.repository.aliases():
            phrase = normalize_text(alias["phrase"])
            if _contains_phrase(normalized, phrase):
                item = dict(alias)
                item["matched_phrase"] = phrase
                candidates.setdefault(item["category"], []).append(item)
        if not candidates:
            terms = self.repository.taxonomy_terms()
            return {
                "status": "UNSUPPORTED_INPUT",
                "message": "No supported predefined criteria were recognised; select from the controlled choices.",
                "choices": [
                    {"term_id": item["term_id"], "category": item["category"], "label": item["label"]}
                    for item in sorted(terms, key=lambda item: (CATEGORY_ORDER.get(item["category"], 99), item["term_id"]))
                ],
            }

        selected: list[dict] = []
        for category in sorted(candidates):
            category_items = candidates[category]
            best_length = max(len(item["matched_phrase"].split()) for item in category_items)
            longest = [item for item in category_items if len(item["matched_phrase"].split()) == best_length]
            best_priority = max(int(item["priority"]) for item in longest)
            best_by_term: dict[str, dict] = {}
            for item in sorted((item for item in longest if int(item["priority"]) == best_priority), key=lambda item: item["term_id"]):
                best_by_term.setdefault(item["term_id"], item)
            if len(best_by_term) > 1:
                return {
                    "status": "AMBIGUOUS_INPUT",
                    "message": "More than one predefined criterion is equally applicable; select one.",
                    "category": category,
                    "choices": [{"term_id": item["term_id"], "label": item["label"]} for item in best_by_term.values()],
                }
            selected.append(next(iter(best_by_term.values())))

        if not any(item["category"] == "wellness_goal" for item in selected):
            goals = [term for term in self.repository.taxonomy_terms() if term["category"] == "wellness_goal"]
            return {
                "status": "AMBIGUOUS_INPUT",
                "message": "Select one predefined wellness goal before requesting options.",
                "category": "wellness_goal",
                "choices": [{"term_id": item["term_id"], "label": item["label"]} for item in sorted(goals, key=lambda item: item["term_id"])],
            }
        controlled = [
            {"term_id": item["term_id"], "category": item["category"], "label": item["label"], "matched_phrase": item["matched_phrase"]}
            for item in sorted(selected, key=lambda item: (CATEGORY_ORDER[item["category"]], item["term_id"]))
        ]
        return {"status": "OK", "matched_terms": controlled, "message": "Supported predefined criteria recognised."}
