Klondike Solitaire (FastAPI + Web)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/PabloCannizzaro/TP_FINAL_PROGRAMACION)

Diagnóstico inicial

- Frontend presentaba caracteres corruptos y un bug de sintaxis en `solitaire/frontend/main.js` que rompía el render (línea de stock con comillas inválidas y símbolos rotos). Además, no había manejo de errores ni estados de carga, permitiendo dobles clics y múltiples requests concurrentes.
- UI con textos con encoding corrupto en `solitaire/frontend/index.html` y sin feedback accesible.
- Backend estable, con endpoints claros; faltaba una prueba de error para movimientos inválidos.
 

Arquitectura de estado del juego

- Motor puro en `solitaire/backend/core/`:
  - `KlondikeGame`: estado completo (stock, waste, tableau x7, foundations, scoring, history). Reglas de movimiento puras y serialización.
  - Pilas: `PilaAbstracta` (abstracta) + `PilaFundacion`, `PilaTableau`, `PilaDescarte`, `PilaMazo` (esta última usa `ColaTAD`).
  - Scoring con tiempo/movimientos y modos `standard|vegas`.
  - Historial `HistorialMovimientos` (undo/redo por estados serializados).
- Dominio y persistencia: `Partida` con encapsulamiento de semilla y `RepositorioPartidasJSON` (CRUD en `data/saves.json`).
- API FastAPI (`/api`): crear partida, mover, hint, undo/redo, autoplay, obtener estado y CRUD de saves.

Refactor y UI minimalista

- Reescrito `solitaire/frontend/main.js` para:
  - Arreglar símbolos, stock visual y bug de sintaxis.
  - Envolver acciones con `action()` que aplica loading/disabled y manejo unificado de errores con toast accesible.
  - Mejorar accesibilidad (aria-live, aria-busy) y prevenir dobles envíos.
  - Toggle de tema claro/oscuro via `data-theme`.
- Actualizado `solitaire/frontend/index.html` (textos correctos, botón de tema, toast).
- Estilos modernizados en `solitaire/frontend/styles.css` (tema claro, estado `disabled`, toast, responsive).

Pruebas

- Lógica: ya existente en `tests/test_rules.py` y TADs en `tests/test_tads.py`.
- API: `tests/test_api.py` cubre ciclo básico; se agregó `tests/test_errors.py` para validar 400 ante movimiento inválido.
 

Scripts y tooling

- Makefile: `dev`/`start`, `test`, `lint`, `format`.
- Lint/format: `pyproject.toml` para Black y Ruff; `.editorconfig` para consistencia.

Cómo correr

- Requisitos: Python 3.10+
- Instalar dependencias: `pip install -r requirements.txt`
- Ejecutar app: `python -m solitaire.main` y abrir `http://localhost:8000/`
- Pruebas: `pytest -q`
- Lint: `ruff check .` (opcional si instalado)
- Format: `black .` (opcional si instalado)

Docker

- Local: `docker compose up --build`
- App en `http://localhost:8000/`

Despliegue en Railway

- Usa el botón de este README (Deploy on Railway). No requiere configuración adicional: `Procfile` ya expone el proceso web con Uvicorn y Railway inyecta `PORT`.
- Salud sugerida: `GET /api/game/state`.

 

Variables de entorno

- `PORT`: asignado por Railway (no requerido localmente).

Checklist de aceptación

- `python -m solitaire.main` levanta sin errores y sirve el frontend.
- Los botones ejecutan el flujo correcto con un clic, muestran loading y no permiten dobles envíos; errores visibles vía toast.
- Se puede jugar y ganar; reglas válidas; reinicio estable.
- Pruebas clave en verde; lint/format pasan si las herramientas están instaladas.
- README actualizado con comandos.

Próximos pasos

- Agregar pruebas end-to-end del frontend (Playwright) si se desea validar UI.
- Ampliar accesibilidad con navegación por teclado entre columnas/celdas.

Assets de cartas (frente y dorso)

- Carpeta: `solitaire/frontend/assets/cards/`
- Nombres esperados (minúsculas):
  - Dorso por defecto: `back.png`
  - Frente: `<rank>_of_<suit>.png`
    - `<rank>`: `ace, 2..10, jack, queen, king`
    - `<suit>`: `hearts, diamonds, clubs, spades`
- Ejemplos: `ace_of_hearts.png`, `10_of_spades.png`, `queen_of_diamonds.png`
- Fallback: si falta el archivo, se renderiza un SVG de placeholder (sin necesidad de assets externos).

Notas de accesibilidad (a11y)

- Cada carta face-up se renderiza como imagen con `alt` y `aria-label` (“Siete de Corazones”, etc.).
- Botones muestran estado de carga y evitan doble click; overlay semitransparente anuncia acciones en curso.
- Focus visible en controles y zonas de drop.

Tema claro/oscuro

- Se quitó el botón “Light”. El tema por defecto queda tal como está (oscuro).
- Para reactivar un toggle, se puede volver a agregar un botón que alterne `document.documentElement.dataset.theme` entre `light` y `dark` (ya hay estilos definidos para `:root[data-theme="light"]`).
Klondike Solitaire (FastAPI + SPA)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/PabloCannizzaro/TP_FINAL_PROGRAMACION)

Descripción

Solitario Klondike con backend en FastAPI y frontend web (SPA) estático. Incluye motor de reglas puro (sin I/O), pistas de jugadas sin mutar estado, deshacer/rehacer, guardado en JSON y tablero de puntajes simple.

Estructura

- `solitaire/backend/core/`: motor y utilidades
  - `klondike.py`: reglas, estado y movimientos
  - `models.py`: tipos (Suit, Rank, Card, MoveType)
  - `serializer.py`: snapshots JSON-friendly
  - `scoring.py`: puntaje y tiempo
  - `hints.py`: sugerencias (`hint`/`hints`) sin mutar estado
- `solitaire/backend/api/`: API REST (FastAPI)
- `solitaire/backend/domain/`: entidad `Partida` y repositorio JSON
- `solitaire/backend/services/`: servicios auxiliares (scoreboard)
- `solitaire/frontend/`: SPA estática (HTML/CSS/JS)
- `solitaire/tads/`: TADs educativos (cola, lista, deque, BST)

Ejecutar en local

- Requisitos: Python 3.10+
- Instalar dependencias: `pip install -r requirements.txt`
- Ejecutar la app:
  - Opción simple: `python -m solitaire.main`
  - O con Uvicorn: `uvicorn solitaire.backend.app:create_app --factory --host 0.0.0.0 --port 8000`
- Abrir: `http://localhost:8000/`
- Health check: `GET /health`

Docker

- Levantar: `docker compose up --build`
- App en: `http://localhost:8000/`

Despliegue en Railway

- Botón al inicio del README (Deploy on Railway) o crear un servicio desde este repo.
- Railway detecta Python (Procfile) o usa el Dockerfile.
- Proceso web (Procfile): `web: python -m solitaire.main`
- Variable `PORT` la inyecta Railway automáticamente (la app la usa).
- Health check sugerido: `GET /health` o `GET /api/game/state`

Endpoints principales

- `POST /api/game/new` {mode, draw, seed?, player_name?} -> {id, state}
- `POST /api/game/move` {move} -> {ok, state}
- `POST /api/game/hint` -> {hint}
- `POST /api/game/undo` -> {ok, state}
- `POST /api/game/redo` -> {ok, state}
- `POST /api/game/autoplay` {limit?} -> {moved, state}
- `GET  /api/game/state` -> state
- CRUD saves: `GET/POST /api/saves`, `GET/PUT/DELETE /api/saves/{id}`
- Ranking: `GET /api/leaderboard` y `GET /api/scoreboard`

Formato de movimientos (API/UI)

- `{"type":"draw"}`
- `{"type":"recycle"}`
- `{"type":"w2f"}`
- `{"type":"w2t","to_col":int}`
- `{"type":"t2f","from_col":int}`
- `{"type":"t2t","from_col":int,"start_index":int,"to_col":int}`

Pistas de jugadas (hint/hints)

- Implementadas en `solitaire/backend/core/hints.py` sin mutar el estado.
- Prioriza: `w2f` > `t2f` > `t2t` que revela > `w2t` > `draw` > `recycle`.
- El endpoint `/api/game/hint` usa esta versión pura basada en `serialize_state(...)`.

Variables de entorno

- `PORT`: puerto de escucha (lo asigna Railway en despliegue). Localmente, por defecto 8000.

Notas

- Guardados en `data/saves.json` (se crea automáticamente).
- El frontend se sirve bajo `/static` y la SPA en `/`.
