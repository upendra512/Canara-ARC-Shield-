"""FastAPI application scaffold."""

from __future__ import annotations

from fastapi import FastAPI

from api.routes import router


def create_app() -> FastAPI:
    """Create the API application without starting a server."""

    app = FastAPI(title="Offline Regulatory Intelligence Platform")
    app.include_router(router)
    return app
