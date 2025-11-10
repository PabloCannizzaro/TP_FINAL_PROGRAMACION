"""Rutas REST para el juego Klondike (FastAPI).

Endpoints principales y contratos:
  - POST /api/game/new {mode, draw, seed?, player_name?} -> {id,state}
  - POST /api/game/move {move} -> {ok,state} (400 si ilegal)
  - POST /api/game/hint -> {hint}
  - POST /api/game/undo -> {ok,state}
  - POST /api/game/redo -> {ok,state}
  - POST /api/game/autoplay {limit?} -> {moved,state}
  - GET  /api/game/state -> state
  - CRUD /api/saves ... (JSON en data/saves.json)

Notas:
- El manejo de errores se unifica en app.py para devolver {"detail": msg}.
- Se guarda en memoria un juego activo (GameHolder) y se persiste tras cada
  acción.
- En victoria se registra una entrada en el scoreboard (si es posible).
"""
from __future__ import annotations

import uuid
from pathlib import Path
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request

from ..core.klondike import KlondikeGame
from ..core.hints import hint as compute_hint, hints as compute_hints
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
    """Mantiene el juego actual en memoria y su ``Partida`` asociada.

    Este holder permite compartir una sesión en memoria entre llamadas HTTP
    dentro del mismo proceso (útil para desarrollo/demo). La persistencia
    duradera se realiza en JSON mediante ``RepositorioPartidasJSON``.
    """

    def __init__(self) -> None:
        self.game: Optional[KlondikeGame] = None
        self.partida: Optional[Partida] = None

    def ensure(self) -> None:
        if not self.game or not self.partida:
            p = Partida.nueva(id=str(uuid.uuid4()))
            self.game = KlondikeGame(mode=p.modo, draw_count=p.draw_count, seed=p.semilla)
            self.partida = p


HOLDERS: Dict[str, GameHolder] = {}


def _get_holder(request: Request) -> GameHolder:
    """Devuelve un `GameHolder` por usuario, usando el header `X-Client-Id`."""
    try:
        cid = request.headers.get("x-client-id") or request.headers.get("X-Client-Id") or "default"
    except Exception:
        cid = "default"
    if cid not in HOLDERS:
        HOLDERS[cid] = GameHolder()
    return HOLDERS[cid]


@router.post("/game/new")
def new_game(payload: Dict[str, Any], request: Request) -> Dict[str, Any]:
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
    h = _get_holder(request)
    h.game, h.partida = g, p
    _repo().crear(p)
    return {"id": p.id, "state": serialize_state(g.to_state())}


@router.post("/game/move")
def post_move(payload: Dict[str, Any], request: Request) -> Dict[str, Any]:
    h = _get_holder(request)
    g, p = h.game, h.partida
    if not g or not p:
        raise HTTPException(status_code=400, detail="No hay partida activa")
    mv = payload.get("move")
    if not isinstance(mv, dict):
        raise HTTPException(status_code=400, detail="move inválido")
    ok = g.apply_move(mv)
    if not ok:
        raise HTTPException(status_code=400, detail="Movimiento ilegal")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    # si ganó, registrar en scoreboard usando el nombre del jugador si existe
    try:
        if g.is_won():
            nombre = p.jugador or payload.get("name") or "Anónimo"
            _scoreboard().add(name=nombre, score=p.puntaje, moves=p.movimientos, seconds=p.tiempo_segundos, draw=p.draw_count)
    except Exception:
        pass
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.post("/game/hint")
def post_hint(request: Request) -> Dict[str, Any]:
    h = _get_holder(request)
    g = h.game
    if not g:
        raise HTTPException(status_code=400, detail="No hay partida activa")
    # Usar versiones puras basadas en el estado serializado
    state = serialize_state(g.to_state())
    h = compute_hint(state)
    return {"hint": h}


@router.post("/game/autoplay")
def post_autoplay(request: Request, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    h = _get_holder(request)
    g, p = h.game, h.partida
    if not g or not p:
        raise HTTPException(status_code=400, detail="No hay partida activa")
    limit = int((payload or {}).get("limit", 200))
    count = g.autoplay(limit=limit)
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    # si al terminar el autoplay se ganó, registrar en el scoreboard
    try:
        if g.is_won():
            nombre = p.jugador or "Anónimo"
            _scoreboard().add(name=nombre, score=p.puntaje, moves=p.movimientos, seconds=p.tiempo_segundos, draw=p.draw_count)
    except Exception:
        pass
    return {"moved": count, "state": serialize_state(g.to_state())}


@router.post("/game/undo")
def post_undo(request: Request) -> Dict[str, Any]:
    h = _get_holder(request)
    g, p = h.game, h.partida
    if not g or not p:
        raise HTTPException(status_code=400, detail="No hay partida activa")
    if not g.undo():
        raise HTTPException(status_code=400, detail="No hay más para deshacer")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.post("/game/redo")
def post_redo(request: Request) -> Dict[str, Any]:
    h = _get_holder(request)
    g, p = h.game, h.partida
    if not g or not p:
        raise HTTPException(status_code=400, detail="No hay partida activa")
    if not g.redo():
        raise HTTPException(status_code=400, detail="No hay más para rehacer")
    p.actualizar_desde_juego(g)
    _repo().actualizar(p)
    return {"ok": True, "state": serialize_state(g.to_state())}


@router.get("/game/state")
def get_state(request: Request) -> Dict[str, Any]:
    h = _get_holder(request)
    # Para compatibilidad con tests/CI y primera carga, auto-crear si no hay
    if not h.game or not h.partida:
        # crea una partida por defecto (modo standard, draw 1)
        pid = str(uuid.uuid4())
        p = Partida.nueva(id=pid)
        g = KlondikeGame(mode=p.modo, draw_count=p.draw_count, seed=p.semilla)
        h.game, h.partida = g, p
        _repo().crear(p)
    return serialize_state(h.game.to_state())


# -------------------- CRUD de Partidas --------------------


@router.get("/saves")
def list_saves() -> Dict[str, Any]:
    items = _repo().listar()
    return {"items": [r.__dict__ | {"semilla": r.semilla} for r in items]}


@router.get("/scoreboard")
def get_scoreboard(request: Request) -> Dict[str, Any]:
    """Ranking con partidas ganadas y, si corresponde, la partida en curso.

    Siempre devuelve las entradas persistidas (victorias). Adems, si el
    cliente actual tiene una partida activa con nombre de jugador, se incluye
    una fila adicional representando sus estadsticas *hasta el momento*,
    aunque no haya finalizado el juego. El orden respeta (-score, seconds,
    moves, ts) como en el servicio de scoreboard.
    """
    items = _scoreboard().sorted_entries()
    try:
        h = _get_holder(request)
        p = h.partida if h else None
        if p and p.jugador:
            # Si la partida ya est ganada, NO agregamos la fila "en curso"
            # para evitar duplicados con la entrada persistida del scoreboard.
            won = False
            try:
                won = bool((p.estado_serializado or {}).get("won", False))
            except Exception:
                won = False
            if won:
                return {"items": items}
            current_row = {
                "name": p.jugador,
                "score": int(p.puntaje),
                "moves": int(p.movimientos),
                "seconds": int(p.tiempo_segundos),
                "draw": int(p.draw_count),
                # ts solo para desempate final; como es en curso, usamos ahora
                "ts": float(time.time()),
                # bandera opcional por si el frontend la quiere distinguir
                "live": True,
            }
            # Evitar duplicar si ya existe una fila exactamente igual
            exists_same = any(
                (r.get("name") == current_row["name"]
                 and int(r.get("score", 0)) == current_row["score"]
                 and int(r.get("moves", 0)) == current_row["moves"]
                 and int(r.get("seconds", 0)) == current_row["seconds"]
                 and int(r.get("draw", 1)) == current_row["draw"]) for r in items
            )
            if exists_same:
                return {"items": items}
            def sort_key(row: Dict[str, Any]):
                return (
                    -int(row.get("score", 0)),
                    int(row.get("seconds", 0)),
                    int(row.get("moves", 0)),
                    float(row.get("ts", 0.0)),
                )
            items = sorted([*items, current_row], key=sort_key)
    except Exception:
        # No interrumpir el endpoint si no hay holder/partida
        pass
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
