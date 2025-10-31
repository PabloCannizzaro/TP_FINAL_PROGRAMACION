"""Núcleo del motor de Klondike (reglas, modelos, serialización y ayudas).

Este paquete agrupa:
- ``models``: tipos base (Suit, Rank, Card, Move).
- ``abstracciones``: interfaz común de pilas.
- ``klondike``: implementación de reglas y estado.
- ``serializer``: helpers para snapshots JSON-friendly.
- ``scoring``: puntaje y temporizador.
- ``hints``: heurística para sugerencias (sin mutar estado).
"""

from .hints import hint, hints  # re-export helpers

__all__ = ["hint", "hints"]
