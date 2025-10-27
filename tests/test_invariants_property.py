import itertools

import pytest

try:
    from hypothesis import given, strategies as st  # type: ignore
except Exception:  # pragma: no cover - optional dependency in some envs
    import pytest as _pytest

    _pytest.skip("hypothesis not installed", allow_module_level=True)

from solitaire.backend.core.klondike import KlondikeGame
from solitaire.backend.core.models import Card, Suit, Rank


def flatten_state(g: KlondikeGame):
    stock = list(g.stock.cartas())
    waste = list(g.waste.cartas())
    tableau = [list(col.cartas()) for col in g.tableau]
    foundations = {s: list(p.cartas()) for s, p in g.foundations.items()}
    return stock, waste, tableau, foundations


def card_key(c: Card):
    return (int(c.rank), c.suit.value)


@given(seed=st.integers(min_value=1, max_value=10_000))
def test_invariants_total_and_unique(seed: int):
    g = KlondikeGame(seed=seed)
    stock, waste, tableau, foundations = flatten_state(g)
    all_cards = list(stock) + list(waste) + list(itertools.chain.from_iterable(tableau)) + list(
        itertools.chain.from_iterable(foundations.values())
    )
    assert len(all_cards) == 52
    assert len({card_key(c) for c in all_cards}) == 52


@given(seed=st.integers(min_value=1, max_value=5_000))
def test_foundations_ascending_and_same_suit(seed: int):
    g = KlondikeGame(seed=seed)
    # hacer algunos robos y autoplays para exponer cartas
    for _ in range(5):
        g.draw_from_stock()
        g.autoplay(limit=20)
    _, _, _, foundations = flatten_state(g)
    for suit, pile in foundations.items():
        if not pile:
            continue
        # cartas por palo correcto y ascendente
        assert all(pile[i].suit.value == suit for i in range(len(pile)))
        assert all(int(pile[i].rank) == i + 1 for i in range(len(pile)))


@given(seed=st.integers(min_value=1, max_value=5_000))
def test_tableau_alternating_descending_visible_pairs(seed: int):
    g = KlondikeGame(seed=seed)
    # tras el reparto, sólo la carta superior es visible por columna
    for col in g.tableau:
        cards = col.cartas()
        if not cards:
            continue
        # el tope debe estar boca arriba
        assert cards[-1].face_up
        # pares visibles (de arriba hacia abajo) deben alternar color y descender
        for i in range(len(cards) - 1, 0, -1):
            if not cards[i - 1].face_up:
                break
            hi, lo = cards[i - 1], cards[i]
            assert hi.suit.color != lo.suit.color
            assert int(hi.rank) == int(lo.rank) + 1
