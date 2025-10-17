from dataclasses import dataclass

SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

def color_of(suit: str) -> str:
    return 'red' if suit in ('hearts','diamonds') else 'black'

@dataclass
class Card:
    suit: str
    rank: str
    face_up: bool = False

    @property
    def color(self):
        return color_of(self.suit)

    def value(self) -> int:
        return RANKS.index(self.rank) + 1

    def to_dict(self):
        return {'suit': self.suit, 'rank': self.rank, 'face_up': self.face_up}

    @staticmethod
    def from_dict(d):
        return Card(d['suit'], d['rank'], d.get('face_up', False))

    def __repr__(self):
        return f"{self.rank} of {self.suit}{' ↑' if self.face_up else ' ↓'}"
