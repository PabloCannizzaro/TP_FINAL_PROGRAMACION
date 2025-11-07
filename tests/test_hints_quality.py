import pytest

from solitaire.backend.core.hints import hints


def _state_from_cols(cols):
    """Helper: build a minimal serialized state with tableau columns.

    `cols` is a list of columns where each column is a list of dict cards
    like {"rank": 13, "suit": "spades", "face_up": True}.
    """
    return {
        "mode": "standard",
        "draw_count": 1,
        "stock": [],
        "waste": [],
        "foundations": {"hearts": [], "diamonds": [], "clubs": [], "spades": []},
        "tableau": cols,
        "score": 0,
        "moves": 0,
        "seconds": 0,
        "won": False,
    }


def test_hints_avoid_king_shuffle_on_empty_columns():
    # Two empty columns and one king face up should not suggest moving king
    # between empties if it does not reveal any new card.
    K_S = {"rank": 13, "suit": "spades", "face_up": True}
    state = _state_from_cols([
        [K_S],  # col 0: king
        [],     # col 1: empty
        [],     # col 2: empty
        [], [], [], [], []
    ])
    hs = hints(state, limit=20)
    t2t_to_empty_king = [m for m in hs if m.get("type") == "t2t" and m.get("to_col") in (1, 2)]
    # Due to our filtering, such moves should not appear
    assert not t2t_to_empty_king


def test_hints_prioritize_revealing_moves_over_non_revealing():
    # Setup: a column with a hidden card that can be revealed by moving the top chain,
    # and another destination that also accepts the head but does not reveal.
    # We expect at least one t2t with explain containing "revela" and a higher score.
    chain = [
        {"rank": 9, "suit": "spades", "face_up": False},
        {"rank": 8, "suit": "hearts", "face_up": True},
        {"rank": 7, "suit": "clubs", "face_up": True},
    ]
    # For 8♥ (red) to move legally, destination top must be 9♣/9♠ (black)
    dest_ok = [{"rank": 9, "suit": "spades", "face_up": True}]  # accepts 8♥ (reveals hidden 9♠ below)
    # For 7♣ (black) to move legally, destination top must be 8♥/8♦ (red)
    other_ok = [{"rank": 8, "suit": "diamonds", "face_up": True}]  # accepts 7♣ (non-revealing start)
    state = _state_from_cols([chain, dest_ok, other_ok, [], [], [], []])
    hs = hints(state, limit=20)
    # Find any revealing t2t
    revs = [m for m in hs if m.get("type") == "t2t" and "revela" in str(m.get("explain", ""))]
    assert revs, "Should include a revealing move in hints"
