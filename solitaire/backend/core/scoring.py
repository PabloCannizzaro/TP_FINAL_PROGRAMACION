"""Puntajes y temporizador para Klondike.

Implementa un sistema simple de puntuaciÃ³n Standard y Vegas.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal


Mode = Literal["standard", "vegas"]


@dataclass
class Scoring:
    """GestiÃ³n de puntaje y tiempo.

    - ``mode``: "standard" o "vegas"
    - ``score``: puntaje acumulado
    - ``moves``: contador de movimientos
    - ``start_ts``: inicio del temporizador (epoch seconds)
    """

    mode: Mode = "standard"
    score: int = 0
    moves: int = 0
    start_ts: float = 0.0

    def start(self) -> None:
        if self.start_ts == 0:
            self.start_ts = time.time()

    def seconds(self) -> int:
        return int(time.time() - self.start_ts) if self.start_ts else 0

    def add_move(self) -> None:
        self.moves += 1

    def add_points(self, pts: int) -> None:
        if self.mode == "vegas":
            # Vegas usually uses money; we approximate with points.
            self.score += pts
        else:
            self.score += pts


