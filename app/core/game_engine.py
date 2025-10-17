import copy
from typing import Dict, List, Optional, Tuple
from .deck import Deck
from .tableau import TableauPile
from .foundation import Foundation
from .card import Card, SUITS

DRAW_COUNT = 3  # puede ponerse en 1 si se desea

class SolitaireGame:
    def __init__(self):
        self.tableau: List[TableauPile] = [TableauPile() for _ in range(7)]
        self.foundations: Dict[str, Foundation] = {s: Foundation(s) for s in SUITS}
        self.stock: List[Card] = []
        self.waste: List[Card] = []
        self.moves: int = 0
        self._undo_stack: List[dict] = []

    # ---------- Setup ----------
    def new_game(self):
        deck = Deck()
        deck.shuffle()
        # Reparto clásico
        for col in range(7):
            for row in range(col + 1):
                c = deck.draw()
                c.face_up = (row == col)
                self.tableau[col].push(c)
        self.stock = []
        while len(deck) > 0:
            self.stock.append(deck.draw())

    # ---------- Helpers ----------
    def _snapshot(self):
        return copy.deepcopy(self.serialize())

    def _push_undo(self):
        self._undo_stack.append(self._snapshot())

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        state = self._undo_stack.pop()
        restored = SolitaireGame.deserialize(state)
        self.__dict__.update(restored.__dict__)
        return True

    def is_won(self) -> bool:
        return all(len(f.cards) == 13 for f in self.foundations.values())

    # ---------- Actions ----------
    def draw_card(self):
        if not self.stock and self.waste:
            # Reciclar waste -> stock boca abajo
            while self.waste:
                c = self.waste.pop()
                c.face_up = False
                self.stock.append(c)
            return

        self._push_undo()
        draw_num = min(DRAW_COUNT, len(self.stock))
        for _ in range(draw_num):
            if self.stock:
                c = self.stock.pop()
                c.face_up = True
                self.waste.append(c)

    def move_tableau_to_foundation(self, t_index: int) -> bool:
        pile = self.tableau[t_index]
        if pile.is_empty():
            return False
        card = pile.peek()
        if not card.face_up:
            return False
        f = self.foundations[card.suit]
        if f.can_accept(card):
            self._push_undo()
            pile.pop()
            f.push(card)
            self._auto_flip(t_index)
            self.moves += 1
            return True
        return False

    def move_waste_to_foundation(self) -> bool:
        if not self.waste:
            return False
        card = self.waste[-1]
        f = self.foundations[card.suit]
        if f.can_accept(card):
            self._push_undo()
            self.waste.pop()
            f.push(card)
            self.moves += 1
            return True
        return False

    def move_waste_to_tableau(self, t_index: int) -> bool:
        if not self.waste:
            return False
        card = self.waste[-1]
        dest = self.tableau[t_index]
        top = dest.peek()
        if top:
            ok = TableauPile.can_place(top, card)
        else:
            ok = (card.rank == 'K')  # Solo reyes a columna vacía
        if ok:
            self._push_undo()
            self.waste.pop()
            dest.push(card)
            self.moves += 1
            return True
        return False

    def move_tableau_to_tableau(self, src: int, dst: int) -> bool:
        if src == dst:
            return False
        source = self.tableau[src]
        if source.is_empty():
            return False
        moving = source.peek()
        if not moving.face_up:
            return False
        dest = self.tableau[dst]
        top = dest.peek()
        if top:
            ok = TableauPile.can_place(top, moving)
        else:
            ok = (moving.rank == 'K')
        if ok:
            self._push_undo()
            source.pop()
            dest.push(moving)
            self._auto_flip(src)
            self.moves += 1
            return True
        return False

    def _auto_flip(self, t_index: int):
        pile = self.tableau[t_index]
        # Si hay una carta boca abajo en el tope, voltear
        for c in reversed(pile.cards):
            if not c.face_up:
                c.face_up = True
                break
            else:
                # Si ya estábamos en un bloque visible, no seguir
                break

    # ---------- Hint ----------
    def find_simple_hint(self) -> Optional[dict]:
        # 1) tableau -> foundation
        for i, p in enumerate(self.tableau):
            if p.is_empty():
                continue
            c = p.peek()
            if c.face_up and self.foundations[c.suit].can_accept(c):
                return {'type': 'tableau->foundation', 'from': i, 'to': c.suit}
        # 2) waste -> foundation
        if self.waste:
            c = self.waste[-1]
            if self.foundations[c.suit].can_accept(c):
                return {'type': 'waste->foundation'}
        # 3) waste -> tableau
        if self.waste:
            c = self.waste[-1]
            for i, p in enumerate(self.tableau):
                top = p.peek()
                if (top and TableauPile.can_place(top, c)) or (not top and c.rank == 'K'):
                    return {'type': 'waste->tableau', 'to': i}
        return None

    # ---------- Serialization ----------
    def serialize(self) -> dict:
        return {
            'tableau': [[c.to_dict() for c in p.cards] for p in self.tableau],
            'foundations': {s: f.to_dict() for s, f in self.foundations.items()},
            'stock': [c.to_dict() for c in self.stock],
            'waste': [c.to_dict() for c in self.waste],
            'moves': self.moves
        }

    @staticmethod
    def deserialize(state: dict) -> 'SolitaireGame':
        g = SolitaireGame()
        from .card import Card, SUITS
        g.tableau = []
        for pile in state['tableau']:
            tp = TableauPile()
            tp.cards = [Card.from_dict(x) for x in pile]
            g.tableau.append(tp)
        g.foundations = {}
        for suit in SUITS:
            g.foundations[suit] = Foundation.from_dict(state['foundations'][suit])
        g.stock = [Card.from_dict(x) for x in state['stock']]
        g.waste = [Card.from_dict(x) for x in state['waste']]
        g.moves = state.get('moves', 0)
        g._undo_stack = []
        return g

    # ---------- State for API ----------
    def get_tableau_state(self):
        return [[c.to_dict() for c in p.cards] for p in self.tableau]

    def get_foundation_state(self):
        return {s: [c.to_dict() for c in f.cards] for s, f in self.foundations.items()}

    def get_stock_state(self):
        return len(self.stock)

    def get_waste_state(self):
        return [c.to_dict() for c in self.waste]
