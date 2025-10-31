"""ListaTAD: contenedor educativo sobre ``list`` de Python.

Se utiliza para columnas del tableau y para listas auxiliares del motor.
Hace explícitas operaciones comunes (insertar, agregar, quitar, sublista).
"""
from __future__ import annotations

from typing import Generic, Iterable, Iterator, List, Optional, Sequence, TypeVar

T = TypeVar("T")


class ListaTAD(Generic[T]):
    """Contenedor simple que expone operaciones habituales explícitamente."""

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._data: List[T] = list(items) if items is not None else []

    def insertar(self, idx: int, item: T) -> None:
        """Inserta un elemento en ``idx`` desplazando a la derecha."""

        self._data.insert(idx, item)

    def agregar(self, item: T) -> None:
        """Agrega un elemento al final de la lista."""

        self._data.append(item)

    def quitar(self, idx: int) -> T:
        """Quita y retorna el elemento en ``idx``."""

        return self._data.pop(idx)

    def concatenar(self, otra: "ListaTAD[T]") -> None:
        """Extiende esta lista con los elementos de ``otra``."""

        self._data.extend(otra._data)

    def sublista(self, inicio: int, fin: Optional[int] = None) -> "ListaTAD[T]":
        """Retorna una nueva ``ListaTAD`` como corte [inicio:fin]."""

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
        """Elimina todos los elementos de la lista."""

        self._data.clear()

    def to_list(self) -> List[T]:
        """Retorna una copia superficial como lista nativa."""

        return list(self._data)
