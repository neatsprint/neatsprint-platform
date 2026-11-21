"""Entry point for the NeatSprint __TITLE__.

The service owns its logical database and exposes only its public API. Cross-service
access happens over HTTP or events, never through a shared database (ADR-002).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from neatsprint_lib.api import create_health_router, install_platform_middleware
from neatsprint_lib.db import check_database, create_engine, create_session_factory
from neatsprint_lib.errors import install_error_handlers
from neatsprint_lib.logging import configure_logging

from __PACKAGE__.api.router import api_router
from __PACKAGE__.settings import settings

configure_logging(settings.service_name, settings.log_level, settings.version)


def _database_check() -> Any:
    """Readiness check bound to the engine created in the lifespan."""
    engine = getattr(app.state, "engine", None)
    if engine is None:
        return True
    return check_database(engine)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    engine = None
    if settings.database_url:
        engine = create_engine(settings.database_url)
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
    try:
        yield
    finally:
        if engine is not None:
            await engine.dispose()


app = FastAPI(
    title="NeatSprint __TITLE__",
    version=settings.version,
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

install_error_handlers(app)
install_platform_middleware(
    app, settings.service_name, metrics_enabled=settings.metrics_enabled
)
app.include_router(
    create_health_router(
        settings.service_name,
        {"database": _database_check},
        version=settings.version,
    )
)
app.include_router(api_router, prefix=f"/api/v1/{settings.api_prefix}")


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "version": settings.version,
        "docs": "/docs",
    }
