"""FastAPI app factory and static mount for the SPA."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes_game import router as game_router


def create_app() -> FastAPI:
    app = FastAPI(title="Klondike Solitaire")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(game_router)

    # mount frontend
    root = Path(__file__).resolve().parents[2]
    static_dir = root / "frontend"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")

    return app

