"""Repositorio JSON para Partidas (CRUD) sobre archivo local.

Características:
- Estructura de almacenamiento: diccionario ``id -> partida`` en un JSON.
- Operaciones atómicas a nivel de archivo (lectura y escritura completa).
- Crea el archivo y directorios si no existen.

Notas:
- Este repositorio está pensado para un entorno académico/simple; no maneja
  concurrencia entre procesos ni bloqueos de archivo.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .partida import Partida


class RepositorioPartidasJSON:
    """Repositorio en JSON con operaciones CRUD para ``Partida``."""

    def __init__(self, ruta_archivo: Path) -> None:
        self.ruta = ruta_archivo
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta.exists():
            self._guardar_todo({})

    def _leer_todo(self) -> Dict[str, dict]:
        with self.ruta.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        if not isinstance(data, dict):
            data = {}
        return data

    def _guardar_todo(self, data: Dict[str, dict]) -> None:
        with self.ruta.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def crear(self, p: Partida) -> None:
        data = self._leer_todo()
        if p.id in data:
            raise ValueError("Partida ya existe")
        data[p.id] = self._to_dict(p)
        self._guardar_todo(data)

    def listar(self) -> List[Partida]:
        data = self._leer_todo()
        return [self._from_dict(v) for v in data.values()]

    def obtener(self, id_: str) -> Optional[Partida]:
        data = self._leer_todo()
        raw = data.get(id_)
        return self._from_dict(raw) if raw else None

    def actualizar(self, p: Partida) -> None:
        data = self._leer_todo()
        if p.id not in data:
            raise ValueError("Partida inexistente")
        data[p.id] = self._to_dict(p)
        self._guardar_todo(data)

    def eliminar(self, id_: str) -> None:
        data = self._leer_todo()
        if id_ in data:
            del data[id_]
            self._guardar_todo(data)

    @staticmethod
    def _to_dict(p: Partida) -> dict:
        return {
            "id": p.id,
            "modo": p.modo,
            "puntaje": p.puntaje,
            "movimientos": p.movimientos,
            "tiempo_segundos": p.tiempo_segundos,
            "estado_serializado": p.estado_serializado,
            "draw_count": p.draw_count,
            "semilla": p.semilla,
            "jugador": p.jugador,
        }

    @staticmethod
    def _from_dict(d: Optional[dict]) -> Optional[Partida]:
        if not d:
            return None
        p = Partida(
            id=d["id"],
            modo=d.get("modo", "standard"),
            puntaje=int(d.get("puntaje", 0)),
            movimientos=int(d.get("movimientos", 0)),
            tiempo_segundos=int(d.get("tiempo_segundos", 0)),
            estado_serializado=d.get("estado_serializado", {}),
            draw_count=int(d.get("draw_count", 1)),
            jugador=d.get("jugador"),
        )
        setattr(p, "_Partida__semilla", int(d.get("semilla", 0)))
        return p
