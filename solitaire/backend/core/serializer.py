"""Serialización del estado del juego a JSON y viceversa."""
from __future__ import annotations

from typing import Any, Dict, List

from .models import Card, Suit, Rank


def serialize_pile(cards: List[Card]) -> List[dict]:
    return [c.to_dict() for c in cards]


def deserialize_pile(data: List[dict]) -> List[Card]:
    return [Card.from_dict(d) for d in data]


def serialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize the game state to a JSON-friendly dict."""

    out: Dict[str, Any] = {
        "mode": state["mode"],
        "draw_count": state["draw_count"],
        "stock": serialize_pile(state["stock"]),
        "waste": serialize_pile(state["waste"]),
        "foundations": {s: serialize_pile(v) for s, v in state["foundations"].items()},
        "tableau": [serialize_pile(col) for col in state["tableau"]],
        "score": state["score"],
        "moves": state["moves"],
        "seconds": state["seconds"],
        "won": bool(state.get("won", False)),
    }
    return out


def deserialize_state(data: Dict[str, Any]) -> Dict[str, Any]:
    """Deserialize a state from a JSON-friendly dict."""

    state: Dict[str, Any] = {
        "mode": data["mode"],
        "draw_count": int(data["draw_count"]),
        "stock": deserialize_pile(list(data["stock"])),
        "waste": deserialize_pile(list(data["waste"])),
        "foundations": {k: deserialize_pile(v) for k, v in data["foundations"].items()},
        "tableau": [deserialize_pile(col) for col in data["tableau"]],
        "score": int(data.get("score", 0)),
        "moves": int(data.get("moves", 0)),
        "seconds": int(data.get("seconds", 0)),
        "won": bool(data.get("won", False)),
    }
    return state
