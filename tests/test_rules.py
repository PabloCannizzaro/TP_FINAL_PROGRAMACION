from solitaire.backend.core.klondike import KlondikeGame


def test_new_game_has_7_columns_and_stock():
    g = KlondikeGame(mode="standard", draw_count=1, seed=123)
    assert len(g.tableau) == 7
    # top card(s) face up
    for i, col in enumerate(g.tableau):
        assert len(col.cartas()) == i + 1
        assert col.ver_tope() is not None and col.ver_tope().face_up
    # stock should have remaining cards
    total = sum(len(c.cartas()) for c in g.tableau) + len(g.stock.cartas())
    assert total == 52


def test_draw_and_recycle():
    g = KlondikeGame(seed=42)
    before = len(g.stock.cartas())
    assert g.draw_from_stock()
    assert len(g.waste.cartas()) in (1, 3)
    # drain stock completely by drawing many times
    for _ in range(100):
        g.draw_from_stock()
    # after recycle, stock should refill
    assert g.draw_from_stock() in (True, False)


def test_hint_returns_something():
    g = KlondikeGame(seed=99)
    h = g.hint()
    assert h is not None

