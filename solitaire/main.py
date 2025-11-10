"""Punto de entrada para ejecutar la aplicación web de Klondike.

Inicia el backend FastAPI y sirve el frontend (SPA). Lee el puerto de la
variable de entorno ``PORT`` (usada por Railway/Heroku-like) y por defecto
usa 8000 en local. No contiene lógica de dominio.
"""
from __future__ import annotations

import os
import uvicorn


def main() -> None:
    """Start the ASGI server for the FastAPI app.

    This imports the FastAPI app lazily to keep import side effects minimal
    and allow other tooling (e.g., pytest) to import modules without starting
    the server.
    """
    from .backend.app import create_app

    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except Exception:
        port = 8000
    # En Windows, ligar por defecto a localhost para evitar problemas
    # con firewalls/redes; en otros SO, 0.0.0.0 habilita acceder desde LAN/contener.
    default_host = "127.0.0.1" if os.name == "nt" else "0.0.0.0"
    host = os.environ.get("HOST", default_host)
    uvicorn.run(create_app(), host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
