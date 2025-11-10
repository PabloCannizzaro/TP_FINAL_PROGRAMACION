Este addendum complementa el README con los puntos solicitados por cátedra.

Ejecución rápida (consola)

- `cd <ruta-del-repo>` (ej.: `cd solitarie/`)
- Requisitos: Python 3.10+
- Dependencias: `pip install -r requirements.txt`
- Ejecutar (elige una):
  - `python main.py`
  - `python -m solitaire.main`
  - `uvicorn main:app --reload`
- Abrir `http://localhost:8000/`
- Pruebas: `pytest -q` | Lint: `ruff check .` | Formato: `black .`

Ejecutar en Thonny (Windows)

- Abrir Thonny (Python 3.10+).
- Archivo → Abrir… y seleccionar `main.py` (raíz del repo).
- Verificar “Directorio de trabajo” = carpeta del repo (Ajustes → Intérprete).
- Ejecutar (F5). Ir a `http://localhost:8000/`.
- Alternativa: abrir y ejecutar `solitaire/main.py`.

Front vs Back: CRUD y comunicación

- Backend (API FastAPI): CRUD persistente de `Partida` y ranking en archivos JSON.
  - Endpoints: `GET/POST /api/saves`, `GET/PUT/DELETE /api/saves/{id}`, `GET /api/scoreboard`, `GET /api/leaderboard`.
- Frontend (SPA): mantiene estado de tablero en memoria y preferencias (
  `localStorage`), y usa `fetch` para operar sobre la API.
  - Ejemplo: `fetch('/api/game/move', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ move }) })`.

Despliegue: evidencias a incluir

- Local: captura del navegador en `http://localhost:8000/` y consola ejecutando `python main.py`.
- Railway: URL pública funcionando, dashboard “Healthy”, `GET /health` OK.

Desafíos, Logros y Aprendizajes

- Desafíos
  - Undo/Redo con historial consistente.
  - Sincronización SPA (drag&drop, toasts, loading, a11y).
  - Hints sin mutar estado; scoring con penalizaciones.
  - Compat Windows (host/bind, encoding, CORS).
- Logros
  - API completa testable; scoreboard persistente ordenado.
  - SPA accesible y robusta.
  - Persistencia JSON simple y reproducible.
- Aprendizajes
  - Modularización por capas (core/domain/api/services/frontend).
  - Uso de `dataclasses`, `pathlib`, `pytest`.
- Librerías
  - Amigables: FastAPI, `dataclasses`, `pathlib`.
  - No tan amigables: `queue.SimpleQueue`, `uvicorn` en Windows, CORS.

