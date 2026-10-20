"""Read-only, parameterised access to the predefined product database."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import quote


class Repository:
    def __init__(self, database_path: Path):
        uri = f"file:{quote(str(database_path.resolve()).replace('\\', '/'), safe='/:')}?mode=ro"
        self.connection = sqlite3.connect(uri, uri=True)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def __enter__(self) -> "Repository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    def active_version(self) -> str:
        row = self.connection.execute("SELECT version_id FROM dataset_version WHERE status = ?", ("active",)).fetchone()
        if row is None:
            raise LookupError("no active dataset")
        return str(row["version_id"])

    def active_products(self) -> list[dict]:
        rows = self.connection.execute(
            "SELECT p.product_id, p.display_name AS name, p.predefined_summary AS summary, p.predefined_recommendation_text AS recommendation_text, r.predefined_recipe_text AS recipe_text FROM product p JOIN recipe r ON r.product_id=p.product_id AND r.active=1 WHERE p.version_id = ? AND p.active = 1 ORDER BY p.product_id",
            (self.active_version(),),
        ).fetchall()
        return [dict(row) for row in rows]

    def taxonomy_terms(self) -> list[dict]:
        rows = self.connection.execute("SELECT term_id, category, display_label AS label FROM taxonomy_term WHERE version_id = ? AND active=1 ORDER BY category, term_id", (self.active_version(),)).fetchall()
        return [dict(row) for row in rows]

    def aliases(self) -> list[dict]:
        rows = self.connection.execute(
            "SELECT a.alias_id, a.term_id, a.normalised_phrase AS phrase, a.priority, t.category, t.display_label AS label FROM term_alias a JOIN taxonomy_term t ON t.term_id=a.term_id WHERE t.version_id=? AND t.active=1 ORDER BY LENGTH(a.normalised_phrase) DESC, a.priority DESC, a.term_id",
            (self.active_version(),),
        ).fetchall()
        return [dict(row) for row in rows]

    def boundary_patterns(self) -> list[dict]:
        rows = self.connection.execute("SELECT boundary_id AS pattern_id, normalised_phrase AS phrase, boundary_code, predefined_response AS response_text FROM boundary_pattern WHERE active=1 ORDER BY LENGTH(normalised_phrase) DESC, boundary_id").fetchall()
        return [dict(row) for row in rows]

    def active_rules(self, term_ids: list[str]) -> list[dict]:
        if not term_ids:
            return []
        placeholders = ",".join("?" for _ in term_ids)
        rows = self.connection.execute(
            f"SELECT rule_id, term_id, relationship, weight, predefined_reason_template, version_id FROM scoring_rule WHERE active=1 AND version_id=? AND term_id IN ({placeholders}) ORDER BY rule_id",
            (self.active_version(), *term_ids),
        ).fetchall()
        return [dict(row) for row in rows]

    def product_relations(self, term_ids: list[str]) -> list[dict]:
        if not term_ids:
            return []
        placeholders = ",".join("?" for _ in term_ids)
        rows = self.connection.execute(
            f"SELECT pt.product_id, pt.term_id, pt.relationship AS relation, t.category FROM product_term pt JOIN taxonomy_term t ON t.term_id=pt.term_id JOIN product p ON p.product_id=pt.product_id WHERE p.version_id=? AND pt.term_id IN ({placeholders}) ORDER BY pt.product_id, pt.term_id, pt.relationship",
            (self.active_version(), *term_ids),
        ).fetchall()
        return [dict(row) for row in rows]
