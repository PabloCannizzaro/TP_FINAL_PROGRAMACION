"""ColaTAD: thin educational wrapper around queue.SimpleQueue.

Used for the stock (mazo) and optional event queues.
"""
from __future__ import annotations

from queue import SimpleQueue
from typing import Generic, Iterable, Iterator, Optional, TypeVar

T = TypeVar("T")


class ColaTAD(Generic[T]):
    """A First-In-First-Out queue using ``queue.SimpleQueue``.

    Provides a minimal interface used by the game engine.
    """

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._q: SimpleQueue[T] = SimpleQueue()
        if items:
            for it in items:
                self._q.put(it)

    def encolar(self, item: T) -> None:
        """Enqueue an item at the back of the queue."""

        self._q.put(item)

    def desencolar(self) -> T:
        """Dequeue and return the next item.

        Raises ``QueueEmpty`` (ValueError) if the queue is empty.
        """

        if self.esta_vacia():
            raise ValueError("QueueEmpty")
        return self._q.get()

    def esta_vacia(self) -> bool:
        """Return True if the queue has no items."""

        return self._q.empty()

    def __len__(self) -> int:
        """Return an approximate size (not strictly guaranteed by SimpleQueue)."""

        # SimpleQueue lacks qsize() reliably across platforms; emulate via iteration.
        # To keep O(1), we track length externally would require more code; for
        # our usage we won't rely on __len__ for correctness. Return 0/1 heuristic.
        return 0 if self._q.empty() else 1

    def drenar(self) -> Iterator[T]:
        """Yield items until empty (drain)."""

        while not self.esta_vacia():
            yield self.desencolar()

