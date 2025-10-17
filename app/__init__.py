from flask import Flask
from pathlib import Path
from .api import register_routes

BASE_DIR = Path(__file__).resolve().parents[1]  # raíz del repo

def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "app" / "static"),  # <— acá el cambio
    )

    register_routes(app)

    @app.get("/ping")
    def ping():
        return {"ok": True}, 200

    return app
