"""ListaTAD: educational wrapper around Python list.

Used for tableau columns and stacks of moves.
"""
from __future__ import annotations

from typing import Generic, Iterable, Iterator, List, Optional, Sequence, TypeVar

T = TypeVar("T")


class ListaTAD(Generic[T]):
    """A simple list wrapper exposing common operations explicitly."""

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._data: List[T] = list(items) if items is not None else []

    def insertar(self, idx: int, item: T) -> None:
        """Insert an item at ``idx`` shifting to the right."""

        self._data.insert(idx, item)

    def agregar(self, item: T) -> None:
        """Append an item to the end of the list."""

        self._data.append(item)

    def quitar(self, idx: int) -> T:
        """Remove and return the item at ``idx``."""

        return self._data.pop(idx)

    def concatenar(self, otra: "ListaTAD[T]") -> None:
        """Extend this list with items from ``otra``."""

        self._data.extend(otra._data)

    def sublista(self, inicio: int, fin: Optional[int] = None) -> "ListaTAD[T]":
        """Return a new ``ListaTAD`` as a slice [inicio:fin]."""

        return ListaTAD(self._data[inicio:fin])

    def __getitem__(self, idx: int) -> T:
        return self._data[idx]

    def __setitem__(self, idx: int, value: T) -> None:
        self._data[idx] = value

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def vaciar(self) -> None:
        """Remove all items from the list."""

        self._data.clear()

    def to_list(self) -> List[T]:
        """Return a shallow copy as a plain list."""

        return list(self._data)

