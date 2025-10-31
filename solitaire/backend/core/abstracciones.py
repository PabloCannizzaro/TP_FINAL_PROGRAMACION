"""Abstracciones del motor de juego (sin I/O).

Define la clase abstracta ``PilaAbstracta`` para las distintas pilas del
solitario (fundaciÃ³n, tableau, descarte, mazo).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional

from .models import Card


class PilaAbstracta(ABC):
    """Interfaz comÃºn para pilas del juego.

    Cada pila mantiene internamente una lista de ``Card`` y define reglas
    especÃ­ficas para admitir o no la recepciÃ³n de cartas.
    """

    def __init__(self, cartas: Optional[Iterable[Card]] = None) -> None:
        self._cartas: List[Card] = list(cartas) if cartas else []

    def apilar(self, carta: Card) -> None:
        """Coloca una carta en la parte superior, si es vÃ¡lida."""

        if not self.puede_recibir_carta(carta):
            raise ValueError("Movimiento invÃ¡lido para esta pila")
        self._cartas.append(carta)

    def desapilar(self) -> Card:
        """Quita y retorna la carta superior."""

        if not self._cartas:
            raise ValueError("Pila vacÃ­a")
        return self._cartas.pop()

    def ver_tope(self) -> Optional[Card]:
        """Retorna la carta superior o None si estÃ¡ vacÃ­a."""

        return self._cartas[-1] if self._cartas else None

    def puede_recibir_pila(self, cartas: Iterable[Card]) -> bool:
        """Indica si esta pila puede recibir una subpila de cartas.

        Por defecto, se verifica carta por carta, manteniendo el orden.
        """

        for c in cartas:
            if not self.puede_recibir_carta(c):
                return False
        return True

    @abstractmethod
    def puede_recibir_carta(self, carta: Card) -> bool:
        """Regla especÃ­fica para recibir una carta."""

    def cartas(self) -> List[Card]:
        """Retorna una copia superficial de las cartas."""

        return list(self._cartas)


