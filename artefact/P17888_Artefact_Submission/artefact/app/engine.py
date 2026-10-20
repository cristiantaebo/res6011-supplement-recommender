"""Pure deterministic scoring over predefined repository records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class EngineDataError(ValueError):
    """Raised when stored engine data violates the decision specification."""


class EngineRepository(Protocol):
    def active_version(self) -> str: ...
    def active_products(self) -> list[dict]: ...
    def taxonomy_terms(self) -> list[dict]: ...
    def active_rules(self, term_ids: list[str]) -> list[dict]: ...
    def product_relations(self, term_ids: list[str]) -> list[dict]: ...


@dataclass(frozen=True)
class Candidate:
    product_id: str
    name: str
    summary: str
    recommendation_text: str
    recipe_text: str
    score: int
    reasons: tuple[tuple[str, str, str, int], ...]


class DecisionEngine:
    def __init__(self, repository: EngineRepository, limit: int = 3):
        if not 1 <= limit <= 3:
            raise ValueError("recommendation limit must be between one and three")
        self.repository = repository
        self.limit = limit

    def recommend(self, term_ids: list[str]) -> dict:
        version = self.repository.active_version()
        requested = sorted(set(term_ids))
        known = {term["term_id"]: term for term in self.repository.taxonomy_terms()}
        selected = [term_id for term_id in requested if term_id in known]
        if not selected:
            return self._no_match(version)

        rules = self.repository.active_rules(selected)
        rules_by_term: dict[str, dict] = {}
        for rule in rules:
            if rule["term_id"] in rules_by_term or type(rule["weight"]) is not int or not 0 <= rule["weight"] <= 10:
                raise EngineDataError("invalid or duplicate active scoring rule")
            if rule["version_id"] != version or rule["relationship"] not in {"matches", "eligible"} or not rule["predefined_reason_template"]:
                raise EngineDataError("invalid scoring rule metadata")
            rules_by_term[rule["term_id"]] = rule

        products = {item["product_id"]: item for item in self.repository.active_products()}
        matched_terms: dict[str, set[str]] = {product_id: set() for product_id in products}
        excluded: set[str] = set()
        exclusion_trace: list[dict] = []
        for relation in self.repository.product_relations(selected):
            product_id = relation["product_id"]
            if product_id not in products:
                continue
            if relation["relation"] == "excludes":
                excluded.add(product_id)
                exclusion_trace.append({"product_id": product_id, "term_id": relation["term_id"], "relationship": "excludes"})
            elif relation["relation"] in {"matches", "eligible"} and relation["term_id"] in rules_by_term:
                rule = rules_by_term[relation["term_id"]]
                if rule["relationship"] == relation["relation"]:
                    matched_terms[product_id].add(relation["term_id"])

        candidates: list[Candidate] = []
        for product_id, matched in matched_terms.items():
            if product_id in excluded or not matched:
                continue
            reason_rows = tuple(
                (
                    rules_by_term[term_id]["rule_id"],
                    known[term_id]["label"],
                    rules_by_term[term_id]["predefined_reason_template"],
                    rules_by_term[term_id]["weight"],
                )
                for term_id in sorted(matched)
            )
            product = products[product_id]
            candidates.append(Candidate(product_id, product["name"], product["summary"], product["recommendation_text"], product["recipe_text"], sum(row[3] for row in reason_rows), reason_rows))
        candidates.sort(key=lambda item: (-item.score, -len(item.reasons), item.product_id))
        if not candidates:
            return self._no_match(version, exclusion_trace)
        return {
            "status": "OK",
            "data_version": version,
            "applied_exclusions": sorted(exclusion_trace, key=lambda item: (item["product_id"], item["term_id"])),
            "recommendations": [
                {
                    "product_id": item.product_id,
                    "name": item.name,
                    "summary": item.summary,
                    "recommendation_text": item.recommendation_text,
                    "recipe_text": item.recipe_text,
                    "score": item.score,
                    "reasons": [
                        {"rule_id": rule_id, "label": label, "text": text, "points": points}
                        for rule_id, label, text, points in item.reasons
                    ],
                }
                for item in candidates[: self.limit]
            ],
            "message": "Predefined options ranked by the selected criteria.",
        }

    @staticmethod
    def _no_match(version: str, exclusions: list[dict] | None = None) -> dict:
        return {"status": "NO_MATCH", "data_version": version, "applied_exclusions": exclusions or [], "recommendations": [], "message": "No predefined option matches the selected criteria."}
