"""Thin same-origin API and static UI composition."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.data import build_database
from app.models import RecommendationRequest
from app.pipeline import CorePipeline
from app.repository import Repository
from app.settings import APP_NAME, DEFAULT_DATABASE_PATH, DEFAULT_SEED_PATH, DISCLAIMER, PROJECT_ID, STATIC_PATH

LOGGER = logging.getLogger("artefact.events")


def create_app(seed_path: Path = DEFAULT_SEED_PATH, database_path: Path = DEFAULT_DATABASE_PATH) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        build_database(seed_path, database_path)
        yield

    application = FastAPI(title=APP_NAME, version="0.2.0", lifespan=lifespan)
    application.state.database_path = database_path
    application.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_PATH / "index.html")

    @application.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "project_id": PROJECT_ID, "stage": "I-05"}

    @application.get("/api/taxonomy", tags=["prototype"])
    def taxonomy() -> dict:
        with Repository(application.state.database_path) as repository:
            return {"data_version": repository.active_version(), "terms": repository.taxonomy_terms(), "disclaimer": DISCLAIMER}

    @application.post("/api/recommend", tags=["prototype"])
    def recommend(payload: RecommendationRequest) -> dict:
        started = perf_counter()
        try:
            with Repository(application.state.database_path) as repository:
                result = CorePipeline(repository).process(payload.text)
            result["disclaimer"] = DISCLAIMER
            LOGGER.info(
                "event=RECOMMENDATION_RESULT duration_ms=%d data_version=%s outcome=%s",
                round((perf_counter() - started) * 1000),
                result.get("data_version", "none"),
                result["status"],
            )
            return result
        except (LookupError, ValueError):
            LOGGER.error("event=INVALID_DATA_VERSION outcome=ERROR")
            return JSONResponse(
                status_code=503,
                content={"status": "INVALID_DATA_VERSION", "event_code": "DATA-001", "message": "The controlled dataset is unavailable.", "disclaimer": DISCLAIMER},
            )

    @application.exception_handler(Exception)
    async def unexpected_error(_: Request, error: Exception) -> JSONResponse:
        LOGGER.error("event=UNEXPECTED_ERROR outcome=ERROR type=%s", type(error).__name__)
        return JSONResponse(status_code=500, content={"status": "ERROR", "event_code": "APP-001", "message": "The local prototype could not process this request.", "disclaimer": DISCLAIMER})

    return application


app = create_app()
