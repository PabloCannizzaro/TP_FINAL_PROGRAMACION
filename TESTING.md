Cómo correr pruebas y reproducir partidas

Requisitos

- Python 3.10+
- Instalar dependencias: `pip install -r requirements.txt`

Pruebas unitarias y de propiedades

- Ejecutar: `python -m pytest -q` (usa Hypothesis para generar semillas aleatorias)
- Reporte de cobertura: `python -m pytest --cov=solitaire.backend.core -q`

Semillas reproducibles

- El backend acepta `seed` en `POST /api/game/new`.
- El frontend lee `?seed=NNN` en la URL y lo pasa al crear “Nuevo”.
- Ejemplo: `http://localhost:8000/?seed=123&player=Pablo`.

End-to-End (opcional)

- Se sugiere Playwright (Python). Instalar: `pip install playwright` y `playwright install`.
- Correr un servidor local: `python -m solitaire.main`.
- E2E (sugeridos):
  - Cargar app y abrir “Reglas”.
  - Draw 1 hasta reciclar; verificar que el descarte vuelve a mazo.
  - Drag&drop válido/ inválido (usar selectores `.col` y `.card`).
  - Undo/Redo de 5 movimientos.
  - Autoplay en tablero simple (semilla fija) y verificar fundaciones.

Notas

- Si no existen imágenes PNG de cartas, la UI usa fallback SVG; los 404 no impiden jugar.
- Nombre del jugador: se almacena en `localStorage` y se envía a `/api/game/new`.

