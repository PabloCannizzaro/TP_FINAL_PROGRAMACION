"""Ãrbol binario de bÃºsqueda simple (BST) para puntajes.

Provee inserciÃ³n y recorrido en-orden. Usado para ordenar una tabla
de puntuaciones por puntaje (y desempate por menor tiempo/movimientos).

Nota: ImplementaciÃ³n mÃ­nima para el TP; no estÃ¡ balanceado.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar


K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _Node(Generic[K, V]):
    key: K
    value: V
    left: Optional["_Node[K, V]"] = None
    right: Optional["_Node[K, V]"] = None


class ArbolBST(Generic[K, V]):
    """BST genÃ©rico clave/valor con recorrido en-orden."""

    def __init__(self) -> None:
        self._root: Optional[_Node[K, V]] = None

    def insert(self, key: K, value: V) -> None:
        def _ins(node: Optional[_Node[K, V]], key: K, value: V) -> _Node[K, V]:
            if node is None:
                return _Node(key, value)
            if key < node.key:  # type: ignore[operator]
                node.left = _ins(node.left, key, value)
            else:
                node.right = _ins(node.right, key, value)
            return node

        self._root = _ins(self._root, key, value)

    def inorder(self) -> Iterator[Tuple[K, V]]:
        def _in(node: Optional[_Node[K, V]]):
            if not node:
                return
            yield from _in(node.left)
            yield node.key, node.value
            yield from _in(node.right)

        return _in(self._root)

    def to_list(self) -> List[Tuple[K, V]]:
        return list(self.inorder())


