"""HistorialMovimientos: historial de deshacer/rehacer usando collections.deque.

Proporciona operaciones push/pop en O(1) para un historial ilimitado.
"""
from __future__ import annotations

from collections import deque
from typing import Deque, Generic, Optional, TypeVar

T = TypeVar("T")


class HistorialMovimientos(Generic[T]):
    """Sistema de deshacer/rehacer con dos pilas (deques): ``_undos`` y ``_redos``.

    El elemento almacenado ``T`` puede ser un movimiento o un estado completo serializado.
    En este proyecto almacenamos estados serializados por simplicidad y robustez.
    """

    def __init__(self) -> None:
        self._undos: Deque[T] = deque()
        self._redos: Deque[T] = deque()

    def push_undo(self, item: T) -> None:
        """Agrega un elemento a la pila de deshacer y limpia el historial de rehacer."""

        self._undos.append(item)
        self._redos.clear()

    def push_undo_preserve_redo(self, item: T) -> None:
        """Agrega un elemento a la pila de deshacer sin limpiar la de rehacer.

        Útil para operaciones de "rehacer" donde no queremos descartar
        el resto del historial de redo.
        """

        self._undos.append(item)

    def can_undo(self) -> bool:
        """Indica si hay acciones que se pueden deshacer."""
        return len(self._undos) > 0

    def can_redo(self) -> bool:
        """Indica si hay acciones que se pueden rehacer."""
        return len(self._redos) > 0

    def pop_undo(self) -> Optional[T]:
        """Extrae el último elemento de la pila de deshacer (si existe)."""
        return self._undos.pop() if self._undos else None

    def push_redo(self, item: T) -> None:
        """Agrega un elemento a la pila de rehacer."""
        self._redos.append(item)

    def pop_redo(self) -> Optional[T]:
        """Extrae el último elemento de la pila de rehacer (si existe)."""
        return self._redos.pop() if self._redos else None

    def clear(self) -> None:
        """Limpia por completo ambos historiales (deshacer y rehacer)."""
        self._undos.clear()
        self._redos.clear()
