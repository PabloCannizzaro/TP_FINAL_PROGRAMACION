Klondike Solitaire (FastAPI + Web)

Diagnóstico inicial

- Frontend presentaba caracteres corruptos y un bug de sintaxis en `solitaire/frontend/main.js` que rompía el render (línea de stock con comillas inválidas y símbolos rotos). Además, no había manejo de errores ni estados de carga, permitiendo dobles clics y múltiples requests concurrentes.
- UI con textos con encoding corrupto en `solitaire/frontend/index.html` y sin feedback accesible.
- Backend estable, con endpoints claros; faltaba una prueba de error para movimientos inválidos.
- Render (despliegue) correcto vía `render.yaml`, pero sin documentación unificada en la raíz ni scripts de lint/format.

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
- Botón Render: se interpreta el requisito como “un solo clic → acción esperada con loading/disabled y errores manejados” aplicado a botones principales (Nuevo, Robar, Undo/Redo, Pista, Autoplay). La lógica se valida indirectamente por pruebas de API y manualmente en UI.

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

Despliegue en Render

- Botón en `docs/README.md` o usando `render.yaml` del repo (uvicorn con `--factory`).

Variables de entorno

- `PORT`: asignado por Render (no requerido localmente).

Checklist de aceptación

- `python -m solitaire.main` levanta sin errores y sirve el frontend.
- Los botones ejecutan el flujo correcto con un clic, muestran loading y no permiten dobles envíos; errores visibles vía toast.
- Se puede jugar y ganar; reglas válidas; reinicio estable.
- Pruebas clave en verde; lint/format pasan si las herramientas están instaladas.
- README actualizado con comandos.

Próximos pasos

- Agregar pruebas end-to-end del frontend (Playwright) si se desea validar UI.
- Ampliar accesibilidad con navegación por teclado entre columnas/celdas.

