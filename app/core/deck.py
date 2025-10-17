import random
from typing import List
from .card import Card, SUITS, RANKS

class Deck:
    def __init__(self):
        self.cards: List[Card] = [Card(suit, rank, False) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Card:
        if not self.cards:
            raise IndexError("Deck is empty")
        return self.cards.pop()

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def __len__(self):
        return len(self.cards)
