"""Dominio: Clase principal Partida con CRUD y encapsulado.

Expone la entidad de negocio que persiste el estado del juego
serializado (JSON) y metadatos como puntaje y tiempo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..core.klondike import KlondikeGame
from ..core.serializer import serialize_state


@dataclass
class Partida:
    """Representa una partida de Klondike persistible.

    Atributos:
    - ``id``: identificador único (str)
    - ``modo``: "standard" o "vegas"
    - ``puntaje``: puntos actuales
    - ``movimientos``: cantidad de movimientos realizados
    - ``tiempo_segundos``: tiempo transcurrido
    - ``estado_serializado``: dict JSON-friendly con todo el estado del juego
    - ``__semilla``: semilla privada de barajado (encapsulada)
    - ``draw_count``: 1 o 3
    """

    id: str
    modo: str
    puntaje: int
    movimientos: int
    tiempo_segundos: int
    estado_serializado: Dict[str, Any] = field(default_factory=dict)
    draw_count: int = 1
    __semilla: int = field(default=0, repr=False, init=False)

    @property
    def semilla(self) -> int:
        """Acceso de solo lectura a la semilla encapsulada."""

        return self.__semilla

    @classmethod
    def nueva(cls, id: str, modo: str = "standard", draw_count: int = 1, seed: Optional[int] = None) -> "Partida":
        juego = KlondikeGame(mode=modo, draw_count=draw_count, seed=seed)
        estado = serialize_state(juego.to_state())
        p = cls(
            id=id,
            modo=modo,
            puntaje=estado.get("score", 0),
            movimientos=estado.get("moves", 0),
            tiempo_segundos=estado.get("seconds", 0),
            estado_serializado=estado,
            draw_count=draw_count,
        )
        # set private seed after init
        setattr(p, "_Partida__semilla", juego.seed)
        return p

    def actualizar_desde_juego(self, juego: KlondikeGame) -> None:
        """Sincroniza atributos desde el estado actual del juego."""

        est = serialize_state(juego.to_state())
        self.estado_serializado = est
        self.puntaje = est["score"]
        self.movimientos = est["moves"]
        self.tiempo_segundos = est["seconds"]
