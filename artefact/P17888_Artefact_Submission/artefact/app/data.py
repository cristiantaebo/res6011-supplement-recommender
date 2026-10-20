"""Deterministic validation and SQLite construction for approved data."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ALLOWED_SOURCE_TYPES = {"academic", "industry", "product_page", "synthetic"}
ALLOWED_CATEGORIES = {"wellness_goal", "preference", "format", "dietary_label", "boundary"}
PROHIBITED_LOCATORS = ("kaggle", "opendata")
MEDICAL_CLAIMS = ("cures ", "treats ", "diagnoses ", "prevents disease")


class DataValidationError(ValueError):
    """Raised when seed input does not satisfy the controlled schema policy."""


def load_seed(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _unique_ids(records: list[dict], field: str, label: str) -> set[str]:
    values = [record.get(field) for record in records]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise DataValidationError(f"invalid or duplicate {label}")
    return set(values)


def validate_seed(data: dict) -> None:
    required = {"dataset", "sources", "terms", "aliases", "products", "recipes", "product_terms", "scoring_rules", "boundary_patterns"}
    if not isinstance(data, dict) or not required.issubset(data):
        raise DataValidationError("seed structure is incomplete")
    dataset = data["dataset"]
    if not all(dataset.get(key) for key in ("version_id", "created_date", "source_inventory_hash", "notes")) or dataset.get("status") not in {"draft", "validated", "active", "retired"}:
        raise DataValidationError("invalid dataset metadata")

    source_ids = _unique_ids(data["sources"], "source_id", "source")
    for source in data["sources"]:
        if source.get("source_type") not in ALLOWED_SOURCE_TYPES:
            raise DataValidationError("invalid source type")
        if bool(source.get("synthetic")) != (source["source_type"] == "synthetic"):
            raise DataValidationError("synthetic flag conflicts with source type")
        if not all(source.get(key) for key in ("title", "publisher", "public_url", "accessed_date", "licence_or_use_note", "evidence_path")):
            raise DataValidationError("source metadata is incomplete")
        locator = f"{source['public_url']} {source['evidence_path']}".lower()
        if any(term in locator for term in PROHIBITED_LOCATORS):
            raise DataValidationError("prohibited source locator")

    term_ids = _unique_ids(data["terms"], "term_id", "taxonomy term")
    for term in data["terms"]:
        if term.get("category") not in ALLOWED_CATEGORIES or not term.get("display_label") or type(term.get("active")) is not bool:
            raise DataValidationError("invalid taxonomy term")

    _unique_ids(data["aliases"], "alias_id", "alias")
    for alias in data["aliases"]:
        if alias.get("term_id") not in term_ids or not alias.get("normalised_phrase") or not isinstance(alias.get("priority"), int):
            raise DataValidationError("invalid alias")

    product_ids = _unique_ids(data["products"], "product_id", "product")
    for product in data["products"]:
        controlled_text = " ".join(str(product.get(key, "")).lower() for key in ("display_name", "predefined_summary", "predefined_recommendation_text"))
        if product.get("source_id") not in source_ids or not all(product.get(key) for key in ("display_name", "predefined_summary", "predefined_recommendation_text")):
            raise DataValidationError("invalid or untraceable product")
        if product.get("format_id") is not None and product.get("format_id") not in term_ids:
            raise DataValidationError("invalid product format")
        if type(product.get("active")) is not bool or any(claim in controlled_text for claim in MEDICAL_CLAIMS):
            raise DataValidationError("invalid product content")

    _unique_ids(data["recipes"], "recipe_id", "recipe")
    active_recipe_products: set[str] = set()
    for recipe in data["recipes"]:
        if recipe.get("product_id") not in product_ids or recipe.get("source_id") not in source_ids or not recipe.get("predefined_recipe_text") or type(recipe.get("active")) is not bool:
            raise DataValidationError("invalid recipe")
        if recipe["active"]:
            if recipe["product_id"] in active_recipe_products:
                raise DataValidationError("duplicate active product recipe")
            active_recipe_products.add(recipe["product_id"])
    active_products = {product["product_id"] for product in data["products"] if product["active"]}
    if active_recipe_products != active_products:
        raise DataValidationError("every active product requires one active recipe")

    for relation in data["product_terms"]:
        if relation.get("product_id") not in product_ids or relation.get("term_id") not in term_ids or relation.get("source_id") not in source_ids:
            raise DataValidationError("invalid product relationship")
        if relation.get("relationship") not in {"matches", "excludes", "eligible"}:
            raise DataValidationError("invalid relationship type")

    _unique_ids(data["scoring_rules"], "rule_id", "scoring rule")
    for rule in data["scoring_rules"]:
        if rule.get("term_id") not in term_ids or rule.get("source_id") not in source_ids or rule.get("relationship") not in {"matches", "eligible"}:
            raise DataValidationError("invalid scoring rule reference")
        if type(rule.get("weight")) is not int or not 0 <= rule["weight"] <= 10 or not rule.get("predefined_reason_template") or type(rule.get("active")) is not bool:
            raise DataValidationError("invalid scoring rule")

    _unique_ids(data["boundary_patterns"], "boundary_id", "boundary pattern")
    for boundary in data["boundary_patterns"]:
        if not all(boundary.get(key) for key in ("normalised_phrase", "boundary_code", "predefined_response")) or type(boundary.get("active")) is not bool:
            raise DataValidationError("invalid boundary pattern")


def build_database(seed_path: Path, database_path: Path, schema_path: Path | None = None) -> None:
    data = load_seed(seed_path)
    validate_seed(data)
    schema_path = schema_path or Path(__file__).with_name("db") / "schema.sql"
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        dataset = data["dataset"]
        version_id = dataset["version_id"]
        with connection:
            connection.execute("INSERT INTO dataset_version VALUES (?, ?, ?, ?, ?)", (version_id, dataset["created_date"], dataset["status"], dataset["source_inventory_hash"], dataset["notes"]))
            connection.executemany("INSERT INTO source_record VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [(x["source_id"], x["source_type"], x["title"], x["publisher"], x["public_url"], x["accessed_date"], int(x["synthetic"]), x["licence_or_use_note"], x["evidence_path"]) for x in data["sources"]])
            connection.executemany("INSERT INTO taxonomy_term VALUES (?, ?, ?, ?, ?)", [(x["term_id"], version_id, x["category"], x["display_label"], int(x["active"])) for x in data["terms"]])
            connection.executemany("INSERT INTO term_alias VALUES (?, ?, ?, ?)", [(x["alias_id"], x["term_id"], x["normalised_phrase"], x["priority"]) for x in data["aliases"]])
            connection.executemany("INSERT INTO product VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [(x["product_id"], version_id, x["display_name"], x["predefined_summary"], x["predefined_recommendation_text"], x["format_id"], int(x["active"]), x["source_id"]) for x in data["products"]])
            connection.executemany("INSERT INTO recipe VALUES (?, ?, ?, ?, ?)", [(x["recipe_id"], x["product_id"], x["predefined_recipe_text"], x["source_id"], int(x["active"])) for x in data["recipes"]])
            connection.executemany("INSERT INTO product_term VALUES (?, ?, ?, ?)", [(x["product_id"], x["term_id"], x["relationship"], x["source_id"]) for x in data["product_terms"]])
            connection.executemany("INSERT INTO scoring_rule VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [(x["rule_id"], version_id, x["term_id"], x["relationship"], x["weight"], x["predefined_reason_template"], int(x["active"]), x["source_id"]) for x in data["scoring_rules"]])
            connection.executemany("INSERT INTO boundary_pattern VALUES (?, ?, ?, ?, ?)", [(x["boundary_id"], x["normalised_phrase"], x["boundary_code"], x["predefined_response"], int(x["active"])) for x in data["boundary_patterns"]])
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise DataValidationError("foreign-key verification failed")
        if connection.execute("SELECT COUNT(*) FROM dataset_version WHERE status='active'").fetchone()[0] != 1:
            raise DataValidationError("exactly one active dataset is required")
    except Exception:
        connection.close()
        database_path.unlink(missing_ok=True)
        raise
    finally:
        connection.close()
