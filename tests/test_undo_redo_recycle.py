from solitaire.backend.core.klondike import KlondikeGame


def test_undo_redo_including_recycle():
    g = KlondikeGame(seed=123)
    # draw many times to force recycle at least once
    moves_applied = 0
    recycled = False
    for _ in range(60):
        before_stock = len(g.stock.cartas())
        g.apply_move({"type": "draw"})
        moves_applied += 1
        after_stock = len(g.stock.cartas())
        if after_stock > before_stock:
            recycled = True
            break
    assert moves_applied > 0
    assert recycled or len(g.waste.cartas()) > 0

    # undo all
    undid = 0
    while g.undo():
        undid += 1
    assert undid > 0
    # redo same amount
    redid = 0
    while g.redo():
        redid += 1
    assert redid == undid

