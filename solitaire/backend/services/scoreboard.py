"""Servicio de tabla de puntuaciones con soporte de Ãrbol BST.

Persiste un JSON y, para ordenar, usa un Ãrbol Binario de BÃºsqueda
con la clave de orden (-score, seconds, moves, timestamp).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

from ...tads.arbol import ArbolBST

# Detalles de implementación:
# - Los datos se almacenan como lista de dicts en un JSON legible.
# - Para ordenar, se inserta cada fila en un BST usando la clave
#   (-score, seconds, moves, ts), de modo que el recorrido en-orden
#   devuelva primero mejores puntajes (descendentes) y desempates por
#   menor tiempo y movimientos.


@dataclass
class ScoreEntry:
    name: str
    score: int
    moves: int
    seconds: int
    draw: int
    ts: float


class ScoreboardService:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save([])

    def _load(self) -> List[Dict]:
        try:
            return json.loads(self.path.read_text("utf-8"))
        except Exception:
            return []

    def _save(self, data: List[Dict]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, name: str, score: int, moves: int, seconds: int, draw: int) -> None:
        data = self._load()
        entry = ScoreEntry(name=name or "AnÃ³nimo", score=int(score), moves=int(moves), seconds=int(seconds), draw=int(draw), ts=time.time())
        data.append(asdict(entry))
        self._save(data)

    def sorted_entries(self) -> List[Dict]:
        """Retorna entradas ordenadas por (-score, seconds, moves, ts)."""
        data = self._load()
        tree: ArbolBST[Tuple[int, int, int, float], Dict] = ArbolBST()
        for row in data:
            key = (-int(row.get("score", 0)), int(row.get("seconds", 0)), int(row.get("moves", 0)), float(row.get("ts", 0.0)))
            tree.insert(key, row)
        # inorder da ascendente por clave; ya que usamos -score, es score descendente
        return [v for _, v in tree.inorder()]


