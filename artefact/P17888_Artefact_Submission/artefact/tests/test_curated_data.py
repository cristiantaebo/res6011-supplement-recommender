import hashlib
import json
from pathlib import Path

from app.data import build_database, load_seed, validate_seed
from app.pipeline import CorePipeline
from app.repository import Repository

ROOT = Path(__file__).parents[1]
CURATED = ROOT / "app" / "db" / "seed.curated.json"
SYNTHETIC = ROOT / "app" / "db" / "seed.synthetic.json"
INVENTORY = ROOT / "app" / "db" / "source_inventory.curated.json"
CURATED_SHA256 = "62b6ab3c6af27f1e57dd865d3a04dcc0f6d54d7f87a176b7edbb3722e33cb16a"
SYNTHETIC_SHA256 = "906549b7a9b27c3de27bfd8c94435c42f538ac2e2f6521d8b1ce85a6a486c40d"
INVENTORY_SHA256 = "1cd009f4faaa67efbe1841fa3b41e3fac374130eaac471d7afcbd02605e6c81b"


def test_curated_seed_and_inventory_hashes_are_frozen():
    assert hashlib.sha256(CURATED.read_bytes()).hexdigest() == CURATED_SHA256
    assert hashlib.sha256(SYNTHETIC.read_bytes()).hexdigest() == SYNTHETIC_SHA256
    assert hashlib.sha256(INVENTORY.read_bytes()).hexdigest() == INVENTORY_SHA256
    assert load_seed(CURATED)["dataset"]["source_inventory_hash"] == INVENTORY_SHA256


def test_curated_sources_are_allowed_public_pages_with_explicit_project_method():
    data = load_seed(CURATED)
    validate_seed(data)
    product_sources = {product["source_id"] for product in data["products"]}
    source_map = {source["source_id"]: source for source in data["sources"]}
    assert all(source_map[source_id]["source_type"] == "product_page" and not source_map[source_id]["synthetic"] for source_id in product_sources)
    assert source_map["source_project_method"]["source_type"] == "synthetic"
    assert all(source_map[source_id]["public_url"].startswith("https://") for source_id in product_sources)
    inventory_text = INVENTORY.read_text(encoding="utf-8").lower()
    assert "kaggle" not in inventory_text and "opendata" not in inventory_text


def test_curated_content_contains_only_reviewed_non_medical_wording():
    data = load_seed(CURATED)
    product_text = json.dumps(data["products"] + data["recipes"]).lower()
    for prohibited in ("cures ", "treats ", "diagnoses ", "prevents disease", "best treatment", "safe for you", "effective for you"):
        assert prohibited not in product_text
    assert all("check the current label" in recipe["predefined_recipe_text"].lower() for recipe in data["recipes"])


def test_curated_database_and_controlled_scenarios(tmp_path: Path):
    database = tmp_path / "curated.sqlite3"
    build_database(CURATED, database)
    with Repository(database) as repository:
        assert repository.active_version() == "curated-v1"
        assert [product["product_id"] for product in repository.active_products()] == [
            "real_centrum_multigummies_antioxidants",
            "real_myprotein_whey_powder",
            "real_solgar_gelatin_capsules",
        ]
        pipeline = CorePipeline(repository)
        cases = {
            "mixable option vegetarian powder": "real_myprotein_whey_powder",
            "capsule option gluten free capsule": "real_solgar_gelatin_capsules",
            "chewable option gluten free gummy": "real_centrum_multigummies_antioxidants",
        }
        for text, expected in cases.items():
            result = pipeline.process(text)
            assert result["status"] == "OK"
            assert result["data_version"] == "curated-v1"
            assert result["recommendations"][0]["product_id"] == expected
            assert result["recommendations"][0]["score"] == 10
            assert result["recommendations"][0]["recipe_text"]
        assert pipeline.process("tablet option")["status"] == "NO_MATCH"
        assert pipeline.process("portable option")["status"] == "AMBIGUOUS_INPUT"
