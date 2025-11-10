Klondike Solitaire — Slides (Resumen técnico)

1) Arquitectura y Capas
- Backend: FastAPI (API REST JSON), core de reglas puro, dominio y persistencia JSON.
- Frontend: SPA estática (HTML/CSS/JS) que consume la API con `fetch`.
- Servicios: scoreboard y perfiles (JSON), TADs educativos (cola, deque, BST).

2) CRUD Back vs Front (diferencias clave)
- Back: CRUD persistente sobre `Partida` en `data/saves.json` (endpoints `/api/saves`).
- Front: “CRUD de UI” en memoria + preferencias (e.g., `playerName`), comunica cambios vía HTTP.
- Comunicación: `fetch('/api/...', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({...}) })`.

3) Ejecución local (demo)
- `cd <repo>` → `pip install -r requirements.txt` → `python main.py`.
- Abrir `http://localhost:8000/` y mostrar `/health` y `/api/game/state`.

4) Railway (demo)
- Mostrar dashboard (servicio Healthy), variable `PORT`, logs de arranque y URL pública.
- Ver `GET /health` y el tablero cargando.

5) Desafíos → Logros → Aprendizajes
- Desafíos: undo/redo, drag&drop y estado de carga, hints sin mutar estado, compat Windows.
- Logros: API completa tested, scoreboard persistente, SPA accesible y robusta.
- Aprendizajes: modularización por capas, dataclasses/pathlib, CORS y codificaciones.

6) Librerías
- “Amigables”: FastAPI, `dataclasses`, `pathlib`, `pytest`.
- “No tan amigables”: `queue.SimpleQueue`, `uvicorn` en Windows, CORS.

7) Comandos visibles en slide final
- `python main.py` | `uvicorn main:app --reload` | `pytest -q`

