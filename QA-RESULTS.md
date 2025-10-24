Resumen ejecutivo

El motor de Klondike en Python cumple las reglas básicas: reparto 1..7, alternancia de color y descenso en tableau, fundaciones A→K por palo, robo Draw 1 con reciclado, undo/redo y pistas/autoplay. Se detectaron problemas de UI (modal de nombre, textos con encoding y 404 de assets), que fueron corregidos y/o documentados. Se añadieron pruebas de propiedades con Hypothesis y tests de undo/redo con reciclado.

Mapa de código (breve)

- Backend: FastAPI (`solitaire/backend/app.py`), API (`api/routes_game.py`), motor (`core/`), dominio/persistencia (`domain/`).
- Frontend: HTML/CSS/JS en `solitaire/frontend/` con drag&drop, HUD y modales.

Diagrama ASCII

Frontend(main.js) → /api (routes_game)
  └─ KlondikeGame (core/klondike)
       ├─ Pila* (abstracciones)
       ├─ Models/Card/Suit/Rank
       ├─ Scoring, Serializer
  └─ Repositorio JSON (domain/repositorio) ← Partida

Issues principales (resumen)

- UI: Modal “Nombre” no cerraba ni guardaba en algunos navegadores → se reemplazó submit por botón y se añadió delegación de clic + cierre por Escape/overlay. (FIX: index.html, main.js)
- i18n/encoding: Textos corruptos “fundaci��n”, etc. → Se reescribió `index.html` UTF‑8. (FIX)
- 404 de assets de cartas → Documentado fallback SVG (no bloqueante). (DOC)

Cobertura y pruebas

- Pytest + Hypothesis: invariantes de cartas, fundaciones ascendentes, alternancia en tableau, undo/redo con reciclado.
- E2E (propuesto): Playwright; ver TESTING.md.

Checklist reglas

✅ Reparto inicial 1..7 con tope visible
✅ Alternancia de color y descenso
✅ Solo Rey en vacante
✅ Fundaciones A→K por palo
✅ Draw 1 + reciclado
✅ Doble clic/autoplay a fundación válidos
✅ Contadores/score se actualizan
✅ Undo/redo consistente
❌ Victoria rápida reproducible (no incluida)

