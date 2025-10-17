"""HistorialMovimientos: undo/redo history using collections.deque.

Provides O(1) push/pop operations for unlimited history.
"""
from __future__ import annotations

from collections import deque
from typing import Deque, Generic, Optional, TypeVar

T = TypeVar("T")


class HistorialMovimientos(Generic[T]):
    """Two-stack undo/redo using two deques: ``_undos`` and ``_redos``.

    The stored element ``T`` can be a move or a full serialized state.
    In this project we store serialized states for simplicity and robustness.
    """

    def __init__(self) -> None:
        self._undos: Deque[T] = deque()
        self._redos: Deque[T] = deque()

    def push_undo(self, item: T) -> None:
        """Push an item onto the undo stack and clear redo history."""

        self._undos.append(item)
        self._redos.clear()

    def can_undo(self) -> bool:
        return len(self._undos) > 0

    def can_redo(self) -> bool:
        return len(self._redos) > 0

    def pop_undo(self) -> Optional[T]:
        return self._undos.pop() if self._undos else None

    def push_redo(self, item: T) -> None:
        self._redos.append(item)

    def pop_redo(self) -> Optional[T]:
        return self._redos.pop() if self._redos else None

    def clear(self) -> None:
        self._undos.clear()
        self._redos.clear()

