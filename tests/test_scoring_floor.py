from solitaire.backend.core.scoring import Scoring
from solitaire.backend.core.klondike import KlondikeGame


def test_scoring_can_be_negative_unit():
    s = Scoring("standard")
    # Penalizaciones pueden llevar el puntaje por debajo de 0
    s.add_points(-5)
    assert s.score == -5
    s.add_points(10)
    assert s.score == 5
    s.add_points(-50)
    assert s.score == -45


def test_scoring_can_be_negative_integration_draw_cycle():
    # Reciclar el mazo aplica penalización (-100 en draw 1)
    g = KlondikeGame(mode="standard", draw_count=1, seed=123)
    # Forzar varios robos y recycles
    for _ in range(100):
        g.draw_from_stock()
    st = g.to_state()
    assert st["score"] <= 0
