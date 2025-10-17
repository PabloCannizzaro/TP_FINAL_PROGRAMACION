# Klondike Solitaire (Web + FastAPI)

Proyecto académico: Solitario Klondike con frontend web (SPA) y backend en Python (FastAPI). Cumple con modularización, TADs, herencia (clase abstracta), CRUD con persistencia JSON, docstrings, pruebas y CI.

## Requisitos

- Python 3.10+
- Node opcional (no requerido para correr; el frontend ya está en JS)

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar local

```bash
python -m solitaire.main
# o
python solitaire/main.py
```

Luego abrir http://localhost:8000/

## Librerías

- fastapi, uvicorn (backend ASGI)
- pydantic (dependencia de fastapi)
- pytest (tests)

## Estructura

Ver árbol propuesto en el enunciado (carpeta `solitaire/`).

## API principal

- POST `/api/game/new` {mode, draw, seed?}
- POST `/api/game/move` {move}
- POST `/api/game/hint`
- POST `/api/game/undo` / `/api/game/redo`
- POST `/api/game/autoplay` {limit?}
- GET `/api/game/state`
- CRUD partidas: `/api/saves` (GET, POST), `/api/saves/{id}` (GET, PUT, DELETE)

## Persistencia

Repositorio JSON en `data/saves.json` (se crea automáticamente).

## Pruebas

```bash
pytest -q
```

## Checklist de consignas

- [x] Docstrings + type hints en clases/métodos principales.
- [x] Modularización (motor, API, GUI, TADs, dominio) + `main.py`.
- [x] Clases: `Partida` (principal, ≥5 atributos, 1 encapsulado `__semilla`), `PilaAbstracta` (abstracta) + derivadas.
- [x] Herencia y polimorfismo implementados (`PilaFundacion`, `PilaTableau`, `PilaDescarte`, `PilaMazo`).
- [x] Módulos usados: `collections.deque` (historial), `queue` (ColaTAD), `json` (persistencia). Opcional `re` en perfiles.
- [x] CRUD completo de Partida con persistencia JSON.
- [x] Interfaz web funcional (drag básico, HUD, controles).
- [x] Tests unitarios (TADs, reglas, CRUD, API) + CI.
- [x] README con instalación y librerías.

## Notas de diseño

- El historial de deshacer/rehacer guarda el estado serializado completo (simple/robusto).
- La pila `PilaMazo` usa `ColaTAD` y mantiene snapshot para serialización.
- El frontend usa JS vanilla (accesible, ARIA básico) para minimizar dependencias.

