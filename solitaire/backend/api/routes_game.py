"""Rutas REST para el juego Klondike.

Endpoints principales:
  - POST /api/game/new {mode, seed?, draw}
  - POST /api/game/move {move}
  - POST /api/game/hint
  - POST /api/game/undo
  - POST /api/game/redo
  - POST /api/game/autoplay
  - GET  /api/game/state
  - CRUD /api/saves ...
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException

from ..core.klondike import KlondikeGame
from ..core.serializer import serialize_state
from ..domain.partida import Partida
from ..domain.repositorio import RepositorioPartidasJSON
from ..services.scoreboard import ScoreboardService


router = APIRouter(prefix="/api")


def _repo() -> RepositorioPartidasJSON:
    data_path = Path(__file__).resolve().parents[2] / "data" / "saves.json"
    return RepositorioPartidasJSON(data_path)


def _scoreboard() -> ScoreboardService:
    data_path = Path(__file__).resolve().parents[2] / "data" / "scoreboard.json"
    return ScoreboardService(data_path)


class GameHolder:
    """Mantiene el juego actual en memoria y su Partida asociada."""

    def __init__(self) -> None:
        self.game: Optional[KlondikeGame] = None
        self.partida: Optional[Partida] = None

    def ensure(self) -> None:
        if not self.game or not self.partida:
            p = Partida.nueva(id=str(uuid.uuid4()))
            self.game = KlondikeGame(mode=p.modo, draw_count=p.draw_count, seed=p.semilla)
            self.partida = p


holder = GameHolder()


@router.post("/game/new")
def new_game(payload: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(payload.get("mode", "standard"))
    draw = int(payload.get("draw", 1))
    seed = payload.get("seed")
    player_name = payload.get("player_name")
    pid = str(uuid.uuid4())
    p = Partida.nueva(
        id=pid,
        modo=mode,
        draw_count=draw,
        seed=int(seed) if seed is not None else None,
        jugador=str(player_name) if player_name else None,
    )
    g = KlondikeGame(mode=mode, draw_count=draw, seed=p.semilla)
    holder.game, holder.partida = g, p
    _repo().crear(p)
    return {"id": p.id, "state": serialize_state(g.to_state())}


@router.post("/game/move")
def post_move(payload: Dict[str, Any]) -> Dict[str, Any]:
    holder.ensure()
    g, p = holder.game, holder.partida
    assert g and p
    mv = payload.get("move")
    if not isinstance(mv, dict):
        raise HTTPException(status_code=400, detail="move inválido")
    ok = g.apply_move(mv)
    if not ok:
        raise HTTPException(status_code=400, detail="Movimiento ilegal")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    # si ganó, registrar en scoreboard con nombre anónimo (placeholder)
    try:
        if g.is_won():
            _scoreboard().add(name=payload.get("name") or "Anónimo", score=p.puntaje, moves=p.movimientos, seconds=p.tiempo_segundos, draw=p.draw_count)
    except Exception:
        pass
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.post("/game/hint")
def post_hint() -> Dict[str, Any]:
    holder.ensure()
    g = holder.game
    assert g
    h = g.hint()
    return {"hint": h}


@router.post("/game/autoplay")
def post_autoplay(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    holder.ensure()
    g, p = holder.game, holder.partida
    assert g and p
    limit = int((payload or {}).get("limit", 200))
    count = g.autoplay(limit=limit)
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"moved": count, "state": serialize_state(g.to_state())}


@router.post("/game/undo")
def post_undo() -> Dict[str, Any]:
    holder.ensure()
    g, p = holder.game, holder.partida
    assert g and p
    if not g.undo():
        raise HTTPException(status_code=400, detail="No hay más para deshacer")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.post("/game/redo")
def post_redo() -> Dict[str, Any]:
    holder.ensure()
    g, p = holder.game, holder.partida
    assert g and p
    if not g.redo():
        raise HTTPException(status_code=400, detail="No hay más para rehacer")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.get("/game/state")
def get_state() -> Dict[str, Any]:
    holder.ensure()
    g = holder.game
    assert g
    return serialize_state(g.to_state())


# -------------------- CRUD de Partidas --------------------


@router.get("/saves")
def list_saves() -> Dict[str, Any]:
    items = _repo().listar()
    return {"items": [r.__dict__ | {"semilla": r.semilla} for r in items]}


@router.get("/scoreboard")
def get_scoreboard() -> Dict[str, Any]:
    items = _scoreboard().sorted_entries()
    return {"items": items}


@router.get("/saves/{pid}")
def get_save(pid: str) -> Dict[str, Any]:
    p = _repo().obtener(pid)
    if not p:
        raise HTTPException(status_code=404, detail="No encontrado")
    return p.__dict__ | {"semilla": p.semilla}


@router.post("/saves")
def create_save(payload: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(payload.get("mode", "standard"))
    draw = int(payload.get("draw", 1))
    seed = payload.get("seed")
    pid = str(uuid.uuid4())
    p = Partida.nueva(id=pid, modo=mode, draw_count=draw, seed=int(seed) if seed is not None else None)
    _repo().crear(p)
    return {"id": p.id}


@router.put("/saves/{pid}")
def update_save(pid: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    p = _repo().obtener(pid)
    if not p:
        raise HTTPException(status_code=404, detail="No encontrado")
    # permitir actualizar el estado serializado completo
    state = payload.get("state")
    if state:
        p.estado_serializado = state
        p.puntaje = int(state.get("score", 0))
        p.movimientos = int(state.get("moves", 0))
        p.tiempo_segundos = int(state.get("seconds", 0))
    _repo().actualizar(p)
    return {"ok": True}


@router.delete("/saves/{pid}")
def delete_save(pid: str) -> Dict[str, Any]:
    _repo().eliminar(pid)
    return {"ok": True}


@router.get("/leaderboard")
def get_leaderboard(limit: int = 50) -> Dict[str, Any]:
    """Retorna jugadores anteriores con su mejor puntuación.

    Se calcula a partir de partidas persistidas en ``data/saves.json``.
    """

    items = _repo().listar()
    best: Dict[str, Dict[str, Any]] = {}
    for p in items:
        if not p.jugador:
            continue
        prev = best.get(p.jugador)
        cand = {"jugador": p.jugador, "max_score": int(p.puntaje), "partidas": 1}
        if prev is None or cand["max_score"] > prev["max_score"]:
            best[p.jugador] = cand
        else:
            # actualizar contador de partidas
            prev["partidas"] += 1
    ordered = sorted(best.values(), key=lambda x: (-x["max_score"], x["jugador"]))[:limit]
    return {"items": ordered}
