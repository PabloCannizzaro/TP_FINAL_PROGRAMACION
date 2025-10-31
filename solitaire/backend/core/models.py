"""Modelos base para el solitario Klondike.

Contiene definiciones de palos, rangos, cartas y movimientos.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Literal, Optional, Tuple


class Suit(str, Enum):
    CORAZONES = "hearts"
    DIAMANTES = "diamonds"
    TREBOLES = "clubs"
    PICAS = "spades"

    @property
    def color(self) -> Literal["red", "black"]:
        return "red" if self in {Suit.CORAZONES, Suit.DIAMANTES} else "black"


class Rank(int, Enum):
    AS = 1
    DOS = 2
    TRES = 3
    CUATRO = 4
    CINCO = 5
    SEIS = 6
    SIETE = 7
    OCHO = 8
    NUEVE = 9
    DIEZ = 10
    JOTA = 11
    REINA = 12
    REY = 13


@dataclass(frozen=True)
class Card:
    """Una carta de la baraja inglesa (inmutable).

    Atributos: ``rank``, ``suit`` y ``face_up`` (boca arriba/abajo).
    """

    rank: Rank
    suit: Suit
    face_up: bool = False

    def flips(self) -> "Card":
        """Retorna una copia con el estado de ``face_up`` invertido."""

        return Card(self.rank, self.suit, not self.face_up)

    def to_dict(self) -> Dict:
        return {"rank": int(self.rank), "suit": self.suit.value, "face_up": self.face_up}

    @staticmethod
    def from_dict(d: Dict) -> "Card":
        return Card(Rank(d["rank"]), Suit(d["suit"]), bool(d.get("face_up", False)))


class MoveType(str, Enum):
    DRAW = "draw"
    TABLEAU_TO_TABLEAU = "t2t"
    TABLEAU_TO_FOUNDATION = "t2f"
    WASTE_TO_TABLEAU = "w2t"
    WASTE_TO_FOUNDATION = "w2f"
    RECYCLE_STOCK = "recycle"


@dataclass
class Move:
    """Representa un movimiento atÃ³mico en el juego."""

    type: MoveType
    source: Optional[Tuple[str, int]] = None
    target: Optional[Tuple[str, int]] = None
    count: int = 1


