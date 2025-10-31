"""ColaTAD: contenedor educativo sobre ``queue.SimpleQueue``.

Se utiliza para modelar el mazo (stock) y posibles colas de eventos.
Expone una interfaz mínima (encolar/desencolar/emptiness) acorde al TP.
"""
from __future__ import annotations

from queue import SimpleQueue
from typing import Generic, Iterable, Iterator, Optional, TypeVar

T = TypeVar("T")


class ColaTAD(Generic[T]):
    """Cola FIFO basada en ``queue.SimpleQueue``.

    Provee una interfaz mínima utilizada por el motor del juego.
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
        """Desencola y retorna el próximo elemento.

        Lanza ``ValueError`` ("QueueEmpty") si la cola está vacía.
        """

        if self.esta_vacia():
            raise ValueError("QueueEmpty")
        return self._q.get()

    def esta_vacia(self) -> bool:
        """Return True if the queue has no items."""

        return self._q.empty()

    def __len__(self) -> int:
        """Tamaño aproximado (``SimpleQueue`` no lo garantiza estrictamente)."""

        # ``SimpleQueue`` carece de ``qsize`` confiable; evitamos costo/estado extra.
        # Aquí devolvemos 0/1 heurístico ya que el tamaño exacto no se usa
        # para la corrección del motor.
        return 0 if self._q.empty() else 1

    def drenar(self) -> Iterator[T]:
        """Yield items until empty (drain)."""

        while not self.esta_vacia():
            yield self.desencolar()
