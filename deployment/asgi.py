"""Hosting-only entrypoint for the unchanged P17888 software snapshot."""

from pathlib import Path
import sys
import tempfile

SOURCE = Path(__file__).resolve().parents[1] / "artefact" / "P17888_Artefact_Submission" / "artefact"
sys.path.insert(0, str(SOURCE))

from app.main import create_app  # noqa: E402
from app.settings import DEFAULT_SEED_PATH  # noqa: E402

DEMO_DATABASE = Path(tempfile.gettempdir()) / "p17888-demo" / "artefact.sqlite3"
app = create_app(seed_path=DEFAULT_SEED_PATH, database_path=DEMO_DATABASE)
