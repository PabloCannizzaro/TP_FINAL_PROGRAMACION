from .pile import Pile
from .card import Card

class Foundation(Pile):
    def __init__(self, suit: str):
        super().__init__()
        self.suit = suit

    def can_accept(self, card: Card) -> bool:
        if card.suit != self.suit:
            return False
        if self.is_empty():
            return card.rank == 'A'
        top = self.peek()
        return top.value() + 1 == card.value()

    def to_dict(self):
        return {'suit': self.suit, 'cards': [c.to_dict() for c in self.cards]}

    @staticmethod
    def from_dict(d):
        from .card import Card
        f = Foundation(d['suit'])
        f.cards = [Card.from_dict(x) for x in d['cards']]
        return f
