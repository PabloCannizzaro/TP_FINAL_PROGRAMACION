from solitaire.backend.core.klondike import KlondikeGame


def _base_state():
    return {
        "mode": "standard",
        "draw_count": 1,
        "stock": [],
        "waste": [],
        "foundations": {"hearts": [], "diamonds": [], "clubs": [], "spades": []},
        "tableau": [[], [], [], [], [], [], []],
        "score": 0,
        "moves": 0,
        "seconds": 0,
        "won": False,
    }


def test_tableau_to_foundation_scores_plus_ten():
    # Setup: Ace of hearts face up on tableau col 0, empty foundations
    st = _base_state()
    st["tableau"][0] = [{"rank": 1, "suit": "hearts", "face_up": True}]
    # Ensure enough initial score so the -15 penalty is observable despite floor to 0
    st["score"] = 20

    g = KlondikeGame()
    g.from_state(st)
    before = g.scoring.score
    ok = g.apply_move({"type": "t2f", "from_col": 0})
    assert ok
    # +10 for moving to foundation (no flip here)
    assert g.scoring.score == before + 10


def test_recycle_penalty_draw1_is_100():
    # Setup: empty stock triggers recycle from waste; draw_count=1 applies -100
    st = _base_state()
    st["draw_count"] = 1
    st["waste"] = [
        {"rank": 5, "suit": "spades", "face_up": True},
        {"rank": 7, "suit": "hearts", "face_up": True},
    ]
    st["score"] = 200

    g = KlondikeGame()
    g.from_state(st)
    before = g.scoring.score
    ok = g.apply_move({"type": "draw"})
    assert ok
    assert g.scoring.score == before - 100


def test_recycle_penalty_draw3_is_20():
    # Setup: empty stock triggers recycle from waste; draw_count=3 applies -20
    st = _base_state()
    st["draw_count"] = 3
    st["waste"] = [
        {"rank": 2, "suit": "clubs", "face_up": True},
    ]
    st["score"] = 200

    g = KlondikeGame()
    g.from_state(st)
    before = g.scoring.score
    ok = g.apply_move({"type": "draw"})
    assert ok
    assert g.scoring.score == before - 20


def test_flip_on_tableau_awards_plus_five_on_t2t():
    # Setup: origin has hidden top below a movable head; moving reveals and flips
    st = _base_state()
    # Column 0: 9♠ face down, 8♥ face up
    st["tableau"][0] = [
        {"rank": 9, "suit": "spades", "face_up": False},
        {"rank": 8, "suit": "hearts", "face_up": True},
    ]
    # Column 1 top 9♣ accepts 8♥
    st["tableau"][1] = [
        {"rank": 9, "suit": "clubs", "face_up": True},
    ]
    g = KlondikeGame()
    g.from_state(st)
    before = g.scoring.score
    ok = g.apply_move({"type": "t2t", "from_col": 0, "start_index": 1, "to_col": 1})
    assert ok
    # +3 (t2t) +5 (flip) = +8
    assert g.scoring.score == before + 8


def test_flip_on_tableau_awards_plus_five_on_t2f_totals_plus_fifteen():
    # Setup: origin has hidden card under an Ace ready for foundation
    st = _base_state()
    st["tableau"][0] = [
        {"rank": 9, "suit": "spades", "face_up": False},
        {"rank": 1, "suit": "hearts", "face_up": True},  # Ace
    ]
    st["foundations"]["hearts"] = []
    st["score"] = 50

    g = KlondikeGame()
    g.from_state(st)
    before = g.scoring.score
    ok = g.apply_move({"type": "t2f", "from_col": 0})
    assert ok
    # +10 (to foundation) +5 (flip) => +15 total
    assert g.scoring.score == before + 15
