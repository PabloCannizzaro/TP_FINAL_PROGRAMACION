"""Entry point to run the Klondike Solitaire web app.

Runs the FastAPI backend and serves the SPA frontend.
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
    uvicorn.run(create_app(), host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
