"""Rutas REST para el juego Klondike (por sesión).

Endpoints principales:
  - POST /api/game/new {mode, seed?, draw, player_name?}
  - POST /api/game/move {move}
  - POST /api/game/hint
  - POST /api/game/undo
  - POST /api/game/redo
  - POST /api/game/autoplay
  - POST /api/game/player {player_name}
  - GET  /api/game/state
  - GET  /api/leaderboard (mejor puntaje por jugador)
  - GET  /api/scoreboard (tabla histórica)
  - CRUD /api/saves ...
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, HTTPException, Request, Response

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
    """Mantiene juegos por sesión usando una cookie ``sid``."""

    def __init__(self) -> None:
        self.sessions: Dict[str, Tuple[KlondikeGame, Partida]] = {}

    def get(self, sid: str) -> Optional[Tuple[KlondikeGame, Partida]]:
        return self.sessions.get(sid)

    def set(self, sid: str, game: KlondikeGame, partida: Partida) -> None:
        self.sessions[sid] = (game, partida)

    def ensure(self, sid: str) -> Tuple[KlondikeGame, Partida]:
        got = self.sessions.get(sid)
        if got is None:
            p = Partida.nueva(id=str(uuid.uuid4()))
            g = KlondikeGame(mode=p.modo, draw_count=p.draw_count, seed=p.semilla)
            self.sessions[sid] = (g, p)
            return g, p
        return got


holder = GameHolder()


def _sid(request: Request, response: Response) -> str:
    sid = request.cookies.get("sid")
    if not sid:
        sid = str(uuid.uuid4())
        response.set_cookie("sid", sid, httponly=False, samesite="lax")
    return sid


@router.post("/game/new")
def new_game(payload: Dict[str, Any], request: Request, response: Response) -> Dict[str, Any]:
    mode = str(payload.get("mode", "standard"))
    draw = int(payload.get("draw", 1))
    seed = payload.get("seed")
    player_name = payload.get("player_name")
    sid = _sid(request, response)
    pid = str(uuid.uuid4())
    p = Partida.nueva(
        id=pid,
        modo=mode,
        draw_count=draw,
        seed=int(seed) if seed is not None else None,
        jugador=str(player_name) if player_name else None,
    )
    g = KlondikeGame(mode=mode, draw_count=draw, seed=p.semilla)
    holder.set(sid, g, p)
    _repo().crear(p)
    return {"id": p.id, "state": serialize_state(g.to_state())}


@router.post("/game/move")
def post_move(payload: Dict[str, Any], request: Request, response: Response) -> Dict[str, Any]:
    sid = _sid(request, response)
    g, p = holder.ensure(sid)
    mv = payload.get("move")
    if not isinstance(mv, dict):
        raise HTTPException(status_code=400, detail="move inválido")
    ok = g.apply_move(mv)
    if not ok:
        raise HTTPException(status_code=400, detail="Movimiento ilegal")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    try:
        if g.is_won():
            _scoreboard().add(name=p.jugador or "Anónimo", score=p.puntaje, moves=p.movimientos, seconds=p.tiempo_segundos, draw=p.draw_count)
    except Exception:
        pass
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.post("/game/hint")
def post_hint(request: Request, response: Response) -> Dict[str, Any]:
    sid = _sid(request, response)
    g, _ = holder.ensure(sid)
    h = g.hint()
    return {"hint": h}


@router.post("/game/autoplay")
def post_autoplay(payload: Dict[str, Any] | None = None, request: Request = None, response: Response = None) -> Dict[str, Any]:
    assert request is not None and response is not None
    sid = _sid(request, response)
    g, p = holder.ensure(sid)
    limit = int((payload or {}).get("limit", 200))
    count = g.autoplay(limit=limit)
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"moved": count, "state": serialize_state(g.to_state())}


@router.post("/game/undo")
def post_undo(request: Request, response: Response) -> Dict[str, Any]:
    sid = _sid(request, response)
    g, p = holder.ensure(sid)
    if not g.undo():
        raise HTTPException(status_code=400, detail="No hay más para deshacer")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.post("/game/redo")
def post_redo(request: Request, response: Response) -> Dict[str, Any]:
    sid = _sid(request, response)
    g, p = holder.ensure(sid)
    if not g.redo():
        raise HTTPException(status_code=400, detail="No hay más para rehacer")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.get("/game/state")
def get_state(request: Request, response: Response) -> Dict[str, Any]:
    sid = _sid(request, response)
    g, _ = holder.ensure(sid)
    return serialize_state(g.to_state())


@router.post("/game/player")
def set_player(payload: Dict[str, Any], request: Request, response: Response) -> Dict[str, Any]:
    sid = _sid(request, response)
    _, p = holder.ensure(sid)
    p.jugador = str(payload.get("player_name")) if payload.get("player_name") else None
    _repo().actualizar(p)
    return {"ok": True}


# -------------------- CRUD / Leaderboards --------------------


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
    """Retorna jugadores anteriores con su mejor puntuación a partir de saves."""

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
            prev["partidas"] += 1
    ordered = sorted(best.values(), key=lambda x: (-x["max_score"], x["jugador"]))[:limit]
    return {"items": ordered}
