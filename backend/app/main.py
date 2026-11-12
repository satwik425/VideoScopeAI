from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db import models  # noqa: F401
from app.db.session import Base, engine
from app.services.storage_service import init_storage


def _migrate() -> None:
    """Tiny additive migration for SQLite DBs created before Phase 6."""
    with engine.begin() as conn:
        cols = {r[1] for r in conn.execute(text("PRAGMA table_info(videos)"))}
        if "visual_status" not in cols:
            conn.execute(text("ALTER TABLE videos ADD COLUMN visual_status VARCHAR DEFAULT 'pending'"))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_storage()
    Base.metadata.create_all(engine)
    _migrate()
    yield


app = FastAPI(title="VidScope AI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)
