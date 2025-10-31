import pytest

from solitaire.backend.core.klondike import KlondikeGame
from solitaire.backend.core.models import Card, Rank, Suit


def empty_foundations():
    return {s.value: [] for s in Suit}


def empty_tableau():
    return [[] for _ in range(7)]


def base_state():
    return {
        "mode": "standard",
        "draw_count": 1,
        "stock": [],
        "waste": [],
        "foundations": empty_foundations(),
        "tableau": empty_tableau(),
        "score": 0,
        "moves": 0,
        "seconds": 0,
        "won": False,
    }


def test_waste_to_foundation_scores_10():
    g = KlondikeGame()
    st = base_state()
    st["waste"] = [Card(Rank.AS, Suit.CORAZONES, True)]
    g.from_state(st)
    assert g.move_waste_to_foundation() is True
    assert g.scoring.score == 10
    assert g.scoring.moves == 1


def test_tableau_to_foundation_penalty_minus_15():
    g = KlondikeGame()
    st = base_state()
    st["tableau"][0] = [Card(Rank.AS, Suit.PICAS, True)]
    g.from_state(st)
    assert g.move_tableau_to_foundation(0) is True
    assert g.scoring.score == -15
    assert g.scoring.moves == 1


def test_waste_to_tableau_adds_5():
    g = KlondikeGame()
    st = base_state()
    # Destino: 8♥ (red)
    st["tableau"][0] = [Card(Rank.OCHO, Suit.CORAZONES, True)]
    # Waste: 7♣ (black) -> válido sobre 8♥
    st["waste"] = [Card(Rank.SIETE, Suit.TREBOLES, True)]
    g.from_state(st)
    assert g.move_waste_to_tableau(0) is True
    assert g.scoring.score == 5
    assert g.scoring.moves == 1


def test_tableau_to_tableau_adds_3():
    g = KlondikeGame()
    st = base_state()
    # Destino: 8♥ (red)
    st["tableau"][1] = [Card(Rank.OCHO, Suit.CORAZONES, True)]
    # Origen: 7♣ (black)
    st["tableau"][0] = [Card(Rank.SIETE, Suit.TREBOLES, True)]
    g.from_state(st)
    assert g.move_tableau_to_tableau(0, 0, 1) is True
    assert g.scoring.score == 3
    assert g.scoring.moves == 1


def test_draw_increments_moves_no_points():
    g = KlondikeGame()
    st = base_state()
    # Stock con una carta boca abajo
    st["stock"] = [Card(Rank.CINCO, Suit.DIAMANTES, False)]
    g.from_state(st)
    assert g.draw_from_stock() is True
    assert g.scoring.score == 0
    assert g.scoring.moves == 1
    assert len(g.waste.cartas()) == 1
    assert g.waste.cartas()[0].face_up is True


def test_recycle_penalty_draw1_minus_100():
    g = KlondikeGame()
    st = base_state()
    # Stock vacío, waste con dos cartas
    st["waste"] = [
        Card(Rank.DOS, Suit.DIAMANTES, True),
        Card(Rank.TRES, Suit.PICAS, True),
    ]
    g.from_state(st)
    assert g.draw_from_stock() is True  # recicla
    assert g.scoring.score == -100
    assert g.scoring.moves == 1
    # Ahora stock debería tener 2 cartas boca abajo
    assert len(g.stock.cartas()) == 2
    assert all(not c.face_up for c in g.stock.cartas())


def test_recycle_penalty_draw3_minus_20():
    g = KlondikeGame(mode="standard", draw_count=3)
    st = base_state()
    st["draw_count"] = 3
    st["waste"] = [Card(Rank.DOS, Suit.DIAMANTES, True)]
    g.from_state(st)
    assert g.draw_from_stock() is True  # recicla
    assert g.scoring.score == -20
    assert g.scoring.moves == 1


def test_undo_applies_minus_5_points():
    g = KlondikeGame()
    st = base_state()
    st["waste"] = [Card(Rank.AS, Suit.CORAZONES, True)]
    g.from_state(st)
    # Hacer un movimiento válido
    assert g.move_waste_to_foundation() is True
    assert g.scoring.score == 10
    assert g.scoring.moves == 1
    # Deshacer
    assert g.undo() is True
    # Vuelve al estado previo (0 moves) y aplica penalización -5
    assert g.scoring.moves == 0
    assert g.scoring.score == -5

