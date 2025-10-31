"""Sugerencias de jugadas para Klondike sin mutar el estado.

Expone dos funciones puras:
  - hints(state, limit=20) -> list[MoveDict]
  - hint(state) -> MoveDict | None

Trabaja sobre el estado serializado JSON-friendly tal como lo devuelve
``serialize_state(game.to_state())``. No realiza I/O ni modifica ``state``.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


Move = Dict[str, Any]


RED = {"hearts", "diamonds"}
BLACK = {"clubs", "spades"}


def _color(suit: str) -> str:
    return "red" if suit in RED else "black"


def _foundation_top(foundations: Dict[str, List[Dict[str, Any]]], suit: str) -> Optional[Dict[str, Any]]:
    pile = list(foundations.get(suit, []))
    return pile[-1] if pile else None


def _can_place_on_foundation(card: Dict[str, Any], ftop: Optional[Dict[str, Any]]) -> bool:
    if not card:
        return False
    rank = int(card.get("rank", 0))
    suit = str(card.get("suit", ""))
    if ftop is None:
        return rank == 1  # As inicia fundación
    return suit == ftop.get("suit") and rank == int(ftop.get("rank", 0)) + 1


def _tableau_top(col: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return col[-1] if col else None


def _can_place_on_tableau(head: Dict[str, Any], dest: List[Dict[str, Any]]) -> bool:
    if not head:
        return False
    hr = int(head.get("rank", 0))
    hs = str(head.get("suit", ""))
    dtop = _tableau_top(dest)
    if dtop is None:
        return hr == 13  # Rey en columna vacía
    dr = int(dtop.get("rank", 0))
    ds = str(dtop.get("suit", ""))
    return dr == hr + 1 and _color(ds) != _color(hs)


def _first_face_up_index(col: List[Dict[str, Any]]) -> int:
    for i, c in enumerate(col):
        if bool(c.get("face_up", False)):
            return i
    return -1


def _is_faceup_chain(col: List[Dict[str, Any]], start: int) -> bool:
    if start < 0 or start >= len(col):
        return False
    # Todas boca arriba desde start hasta fin y cadena descendente alternando color
    for i in range(start, len(col)):
        if not bool(col[i].get("face_up", False)):
            return False
    for i in range(start, len(col) - 1):
        a, b = col[i], col[i + 1]
        ar, br = int(a.get("rank", 0)), int(b.get("rank", 0))
        asu, bsu = str(a.get("suit", "")), str(b.get("suit", ""))
        if not (ar == br + 1 and _color(asu) != _color(bsu)):
            return False
    return True


def _score_move(m: Move) -> int:
    t = m.get("type")
    if t == "w2f":
        return 100
    if t == "t2f":
        return 90
    if t == "t2t":
        return int(m.get("score", 0)) or 40
    if t == "w2t":
        return 70
    if t == "draw":
        return 10
    if t == "recycle":
        return 5
    return 0


def hints(state: Dict[str, Any], limit: int = 20) -> List[Move]:
    """Genera hasta ``limit`` jugadas legales ordenadas por prioridad.

    No muta ``state``. Trabaja con estructuras del estado serializado.
    """

    try:
        stock: List[Dict[str, Any]] = list(state.get("stock") or [])
        waste: List[Dict[str, Any]] = list(state.get("waste") or [])
        foundations: Dict[str, List[Dict[str, Any]]] = {
            str(k): list(v) for k, v in (state.get("foundations") or {}).items()
        }
        tableau: List[List[Dict[str, Any]]] = [list(col) for col in (state.get("tableau") or [])]
    except Exception:
        return []

    out: List[Move] = []

    # Precalcular tope de fundación por palo
    ftop: Dict[str, Optional[Dict[str, Any]]] = {s: _foundation_top(foundations, s) for s in ("hearts", "diamonds", "clubs", "spades")}

    # 1) waste -> foundation
    if waste:
        wtop = waste[-1]
        if _can_place_on_foundation(wtop, ftop.get(str(wtop.get("suit")) )):
            out.append({"type": "w2f", "score": 100, "explain": "Descarte a fundación"})

    # 2) tableau -> foundation (tope)
    for i, col in enumerate(tableau):
        if not col:
            continue
        top = col[-1]
        if not bool(top.get("face_up", False)):
            continue
        if _can_place_on_foundation(top, ftop.get(str(top.get("suit")) )):
            out.append({"type": "t2f", "from_col": i, "score": 90, "explain": "Superior a fundación"})

    # 3) waste -> tableau
    if waste:
        wtop = waste[-1]
        for j, dest in enumerate(tableau):
            if _can_place_on_tableau(wtop, dest):
                out.append({"type": "w2t", "to_col": j, "score": 70, "explain": "Descarte a columna"})

    # 4) tableau -> tableau (subpilas)
    for i, col in enumerate(tableau):
        if not col:
            continue
        first_up = _first_face_up_index(col)
        if first_up < 0:
            continue
        for start in range(first_up, len(col)):
            if not _is_faceup_chain(col, start):
                continue
            head = col[start]
            for j, dest in enumerate(tableau):
                if j == i:
                    continue
                if _can_place_on_tableau(head, dest):
                    reveals = start == first_up and first_up > 0
                    base = 80 if reveals else 40
                    score = base + min(5, len(col) - start)  # leve premio por longitud
                    out.append({
                        "type": "t2t",
                        "from_col": i,
                        "start_index": start,
                        "to_col": j,
                        "score": score,
                        "explain": "Mueve cadena{}".format(" y revela" if reveals else ""),
                    })

    if not out:
        # 5) draw / recycle según corresponda
        if len(stock) > 0:
            out.append({"type": "draw", "score": 10, "explain": "Robar del mazo"})
        elif len(waste) > 0:
            out.append({"type": "recycle", "score": 5, "explain": "Reciclar descarte al mazo"})

    # Enriquecer metadatos para resaltar origen y destino en la UI
    enriched: List[Move] = []
    for m in out:
        t = m.get("type")
        if t == "w2f":
            m.setdefault("from_zone", "waste")
            wtop = waste[-1] if waste else None
            suit = str((wtop or {}).get("suit", ""))
            if suit:
                m.setdefault("to_foundation", suit)
            m.setdefault("explain", "Del descarte a la fundación")
        elif t == "t2f":
            m.setdefault("explain", "Superior a la fundación")
            try:
                fc = int(m.get("from_col", -1))
            except Exception:
                fc = -1
            if 0 <= fc < len(tableau) and tableau[fc]:
                suit = str(tableau[fc][-1].get("suit", ""))
                if suit:
                    m.setdefault("to_foundation", suit)
        elif t == "w2t":
            m.setdefault("from_zone", "waste")
            m.setdefault("explain", "Del descarte a una columna")
        elif t == "t2t":
            m.setdefault("explain", m.get("explain") or "Mueve cadena")
        elif t == "draw":
            m.setdefault("from_zone", "stock")
            m.setdefault("explain", "Robar del mazo")
        elif t == "recycle":
            m.setdefault("from_zone", "waste")
            m.setdefault("to_zone", "stock")
            m.setdefault("explain", "Reciclar descarte al mazo")
        enriched.append(m)
    out = enriched

    # Ordenar por score descendente con desempates menores (tipo estable)
    out.sort(key=lambda m: (int(m.get("score", 0)), m.get("type", "")), reverse=True)
    if limit is not None and limit > 0:
        return out[:limit]
    return out


def hint(state: Dict[str, Any]) -> Optional[Move]:
    """Primera sugerencia disponible o ``None`` si no hay jugadas."""
    lst = hints(state, limit=1)
    return lst[0] if lst else None
