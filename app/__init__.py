# app/__init__.py
from flask import Flask
from pathlib import Path
from .api import register_routes

# Basado en la ubicación de este archivo, no en el CWD
BASE_DIR = Path(__file__).resolve().parents[1]

def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    # Log para verificar rutas reales
    app.logger.info(f"TEMPLATES: {app.template_folder}")
    app.logger.info(f"STATIC:    {app.static_folder}")

    register_routes(app)

    # Salud para verificar que levanta
    @app.get("/ping")
    def ping():
        return {"ok": True}, 200

    return app
