"""Submódulo de API (FastAPI) para el juego.

Contiene routers y endpoints REST que exponen las operaciones del motor
de Klondike (crear partida, mover, pista, undo/redo, estado, etc.).

Este paquete no contiene lógica de juego: delega en ``solitaire.backend.core``
para mantener una separación clara de responsabilidades (API vs. dominio).
"""

__all__ = []
