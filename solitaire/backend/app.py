"""FastAPI app factory and static mount for the SPA."""
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
        return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):  # type: ignore[override]
        return JSONResponse(status_code=400, content={"error": str(exc) or "Bad Request"})

    app.include_router(game_router)

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
