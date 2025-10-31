"""Fábrica de aplicación FastAPI y montaje del frontend (SPA).

Descripción general:
- Expone la API REST bajo el prefijo ``/api`` (ver ``routes_game.py``).
- Monta el frontend estático bajo ``/static`` y sirve ``/`` con ``index.html``.
- Habilita CORS amplio para facilitar ejecución local y despliegue simple.
- Normaliza errores HTTP y ``ValueError`` devolviendo JSON ``{"detail": str}``.

Este módulo no contiene lógica de juego; solo integra FastAPI y el SPA.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.requests import Request
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

    # Unified error handling to ensure consistent JSON errors
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):  # type: ignore[override]
        # Use 'detail' so frontend displays messages in toast
        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):  # type: ignore[override]
        # Map ValueError to 400 with human-readable detail
        return JSONResponse(status_code=400, content={"detail": str(exc) or "Bad Request"})

    app.include_router(game_router)

    @app.get("/health")
    def health():  # type: ignore[unused-ignore]
        return {"ok": True}

    # mount frontend under /static and serve SPA at /
    # El frontend está dentro del paquete `solitaire/frontend`
    root = Path(__file__).resolve().parents[1]  # .../solitaire
    static_dir = root / "frontend"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir), html=False), name="frontend")

        index_path = static_dir / "index.html"

        @app.get("/")
        def spa_index():  # type: ignore[unused-ignore]
            return FileResponse(str(index_path))

    return app
