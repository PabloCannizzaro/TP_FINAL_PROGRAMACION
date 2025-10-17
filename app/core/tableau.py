from typing import List
from .pile import Pile
from .card import Card

class TableauPile(Pile):
    # Visibles contiguas desde la cima hacia abajo
    def visible_run(self) -> List[Card]:
        run = []
        for c in reversed(self.cards):
            if c.face_up:
                run.append(c)
            else:
                break
        return list(reversed(run))

    @staticmethod
    def can_place(onto: Card, moving: Card) -> bool:
        # Alternando color y un punto menor
        return onto.face_up and onto.color != moving.color and onto.value() == moving.value() + 1
