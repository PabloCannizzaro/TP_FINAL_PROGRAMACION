from typing import List, Optional
from .card import Card

class Pile:
    def __init__(self):
        self.cards: List[Card] = []

    def push(self, card: Card):
        self.cards.append(card)

    def pop(self) -> Card:
        return self.cards.pop()

    def peek(self) -> Optional[Card]:
        return self.cards[-1] if self.cards else None

    def __len__(self):
        return len(self.cards)

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def to_list(self):
        return [c.to_dict() for c in self.cards]

    @staticmethod
    def from_list(lst):
        p = Pile()
        from .card import Card
        p.cards = [Card.from_dict(d) for d in lst]
        return p
