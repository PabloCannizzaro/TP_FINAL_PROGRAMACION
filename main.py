"""Entrypoint simple para ejecutar y servir la app.

Permite:
- `python main.py` (Windows-friendly: liga en 127.0.0.1).
- `uvicorn main:app --reload` (para desarrollo con autoreload).
"""
from __future__ import annotations

import os
import uvicorn

from solitaire.backend.app import create_app


# Objeto ASGI para `uvicorn main:app`
app = create_app()


if __name__ == "__main__":
    # Ejecutar con Python estándar: `python main.py`
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except Exception:
        port = 8000
    default_host = "127.0.0.1" if os.name == "nt" else "0.0.0.0"
    host = os.environ.get("HOST", default_host)
    # Usar referencia de string para habilitar `--reload` si se desea
    uvicorn.run("main:app", host=host, port=port, reload=True)

