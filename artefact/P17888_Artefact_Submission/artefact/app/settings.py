"""Non-secret local prototype settings."""

from pathlib import Path

PROJECT_ID = "P17888"
APP_NAME = "Controlled Non-Medical Recommendation Prototype"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
ARTEFACT_ROOT = Path(__file__).parents[1]
DEFAULT_SEED_PATH = ARTEFACT_ROOT / "app" / "db" / "seed.curated.json"
DEFAULT_DATABASE_PATH = ARTEFACT_ROOT / "runtime" / "artefact.sqlite3"
STATIC_PATH = ARTEFACT_ROOT / "app" / "static"
DISCLAIMER = (
    "This local prototype is informational and non-medical. It uses only predefined data and rules, "
    "does not diagnose or treat, and does not replace advice from a qualified healthcare professional."
)
