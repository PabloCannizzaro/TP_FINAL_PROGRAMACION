"""Motor de reglas para Klondike (puro Python, sin I/O).

Incluye: inicialización de partida, validación/aplicación de movimientos,
deshacer/rehacer (historial), pistas y autocompletar.
"""
from __future__ import annotations

import random
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ...tads.cola import ColaTAD
from ...tads.deque_historial import HistorialMovimientos
from ...tads.lista import ListaTAD
from .abstracciones import PilaAbstracta
from .models import Card, MoveType, Rank, Suit
from .scoring import Scoring
from .serializer import deserialize_state, serialize_state


class PilaFundacion(PilaAbstracta):
    """Pila de fundación: asciende por palo desde As a Rey."""

    def puede_recibir_carta(self, carta: Card) -> bool:  # type: ignore[override]
        tope = self.ver_tope()
        if tope is None:
            return carta.rank == Rank.AS
        return carta.suit == tope.suit and carta.rank == Rank(tope.rank + 1)


class PilaTableau(PilaAbstracta):
    """Pila de tableau: desciende alternando color; vacío solo acepta Rey."""

    def puede_recibir_carta(self, carta: Card) -> bool:  # type: ignore[override]
        tope = self.ver_tope()
        if tope is None:
            return carta.rank == Rank.REY
        return (
            tope.rank == Rank(carta.rank + 1)
            and tope.suit.color != carta.suit.color
        )


class PilaDescarte(PilaAbstracta):
    """Pila de descarte (waste). Acepta cualquier carta boca arriba."""

    def puede_recibir_carta(self, carta: Card) -> bool:  # type: ignore[override]
        return True


class PilaMazo(PilaAbstracta):
    """Pila de mazo (stock) sobre una ``ColaTAD``.

    Mantiene un espejo de lista para serialización.
    """

    def __init__(self, cartas: Optional[Iterable[Card]] = None) -> None:
        super().__init__([])
        self._cola: ColaTAD[Card] = ColaTAD()
        self._snapshot: List[Card] = []
        if cartas:
            for c in cartas:
                self.apilar(c)

    def puede_recibir_carta(self, carta: Card) -> bool:  # type: ignore[override]
        return True

    def apilar(self, carta: Card) -> None:  # type: ignore[override]
        self._cola.encolar(carta)
        self._snapshot.append(carta)

    def desapilar(self) -> Card:  # type: ignore[override]
        if self._cola.esta_vacia():
            raise ValueError("Pila vacía")
        c = self._cola.desencolar()
        # sincronizar snapshot removiendo primer elemento
        if self._snapshot:
            self._snapshot.pop(0)
        return c

    def ver_tope(self) -> Optional[Card]:  # type: ignore[override]
        # No tope definido en una cola; retornamos primer elemento si existe.
        return self._snapshot[0] if self._snapshot else None

    def cartas(self) -> List[Card]:  # type: ignore[override]
        return list(self._snapshot)

    def vaciar_en(self, destino: PilaAbstracta) -> None:
        for c in list(self._snapshot):
            _ = self.desapilar()
            destino.apilar(c)


class KlondikeGame:
    """Estado y lógica del juego Klondike.

    Atributos clave:
    - ``mode``: modo de puntaje ("standard"/"vegas")
    - ``draw_count``: 1 o 3 cartas por robo
    - ``seed``: semilla para barajado reproducible
    - ``scoring``: puntaje, movimientos, temporizador
    - ``history``: historial para deshacer/rehacer (serializado)
    - ``tableau``: lista de 7 pilas ``PilaTableau`` (envueltas con ``ListaTAD`` para TAD)
    - ``foundations``: dict palo -> ``PilaFundacion``
    - ``waste``: ``PilaDescarte``
    - ``stock``: ``PilaMazo`` (usa ``ColaTAD``)
    """

    def __init__(self, mode: str = "standard", draw_count: int = 1, seed: Optional[int] = None) -> None:
        if draw_count not in (1, 3):
            raise ValueError("draw_count debe ser 1 o 3")
        self.mode = mode
        self.draw_count = draw_count
        self.seed = seed or random.randrange(1 << 30)
        self.scoring = Scoring("standard" if mode not in ("standard", "vegas") else mode)
        self.history: HistorialMovimientos[Dict[str, Any]] = HistorialMovimientos()

        self.tableau: List[PilaTableau] = [PilaTableau() for _ in range(7)]
        self.foundations: Dict[str, PilaFundacion] = {s.value: PilaFundacion() for s in Suit}
        self.waste = PilaDescarte()
        self.stock = PilaMazo()

        self._init_game()

    # -------------------- Inicialización --------------------
    def _new_deck(self) -> List[Card]:
        deck = [Card(rank=r, suit=s, face_up=False) for s in Suit for r in Rank]
        rng = random.Random(self.seed)
        rng.shuffle(deck)
        return deck

    def _init_game(self) -> None:
        deck = self._new_deck()
        # repartir a tableau
        for col_idx in range(7):
            for _ in range(col_idx + 1):
                c = deck.pop(0)
                self.tableau[col_idx]._cartas.append(c)
            # voltear la ultima
            last = self.tableau[col_idx].ver_tope()
            if last and not last.face_up:
                self.tableau[col_idx]._cartas[-1] = last.flips()
        # resto al mazo
        for c in deck:
            self.stock.apilar(c)
        self.scoring.start()
        self._snapshot_for_undo()

    # -------------------- Serialización --------------------
    def to_state(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "draw_count": self.draw_count,
            "stock": self.stock.cartas(),
            "waste": self.waste.cartas(),
            "foundations": {k: v.cartas() for k, v in self.foundations.items()},
            "tableau": [col.cartas() for col in self.tableau],
            "score": self.scoring.score,
            "moves": self.scoring.moves,
            "seconds": self.scoring.seconds(),
        }

    def from_state(self, data: Dict[str, Any]) -> None:
        state = deserialize_state(serialize_state(data))  # normaliza
        self.mode = state["mode"]
        self.draw_count = state["draw_count"]
        # reconstruir estructuras
        self.tableau = [PilaTableau(col) for col in state["tableau"]]
        self.foundations = {k: PilaFundacion(v) for k, v in state["foundations"].items()}
        self.waste = PilaDescarte(state["waste"])
        self.stock = PilaMazo(state["stock"])
        self.scoring.score = state["score"]
        self.scoring.moves = state["moves"]

    def _snapshot_for_undo(self) -> None:
        self.history.push_undo(serialize_state(self.to_state()))

    # -------------------- Utilidades reglas --------------------
    @staticmethod
    def _can_place_on_tableau(dest: PilaTableau, card: Card) -> bool:
        try:
            return dest.puede_recibir_carta(card)
        except Exception:
            return False

    @staticmethod
    def _can_place_on_foundation(dest: PilaFundacion, card: Card) -> bool:
        try:
            return dest.puede_recibir_carta(card)
        except Exception:
            return False

    def _flip_top_if_needed(self, col: PilaTableau) -> None:
        top = col.ver_tope()
        if top and not top.face_up:
            col._cartas[-1] = top.flips()

    # -------------------- Movimientos --------------------
    def draw_from_stock(self) -> bool:
        """Robar 1 o 3 cartas del mazo al descarte.

        Si el mazo está vacío, recicla el descarte (boca abajo) al mazo.
        """

        if self.stock.ver_tope() is None:
            # reciclar: mover descarte al mazo en el mismo orden pero boca abajo
            if not self.waste.cartas():
                return False
            tmp = list(reversed(self.waste.cartas()))
            self.waste._cartas.clear()
            for c in tmp:
                if c.face_up:
                    c = Card(c.rank, c.suit, False)
                self.stock.apilar(c)
            self.scoring.add_points(-20)  # penalización ligera por reciclar
            self.scoring.add_move()
            return True

        moved = 0
        for _ in range(self.draw_count):
            top = self.stock.ver_tope()
            if top is None:
                break
            c = self.stock.desapilar()
            if not c.face_up:
                c = c.flips()
            self.waste.apilar(c)
            moved += 1
        if moved:
            self.scoring.add_move()
        return moved > 0

    def move_tableau_to_tableau(self, from_col: int, start_index: int, to_col: int) -> bool:
        origen = self.tableau[from_col]
        destino = self.tableau[to_col]
        if start_index < 0 or start_index >= len(origen._cartas):
            return False
        subpila = origen._cartas[start_index:]
        if not subpila or not subpila[0].face_up:
            return False
        # validar cadena descendente y alternando colores
        for i in range(len(subpila) - 1):
            a, b = subpila[i], subpila[i + 1]
            if not (a.rank == Rank(b.rank + 1) and a.suit.color != b.suit.color and b.face_up):
                return False
        if not self._can_place_on_tableau(destino, subpila[0]):
            return False
        # aplicar
        destino._cartas.extend(subpila)
        del origen._cartas[start_index:]
        self._flip_top_if_needed(origen)
        self.scoring.add_points(3)
        self.scoring.add_move()
        return True

    def move_tableau_to_foundation(self, from_col: int) -> bool:
        origen = self.tableau[from_col]
        top = origen.ver_tope()
        if not top or not top.face_up:
            return False
        dest = self.foundations[top.suit.value]
        if not self._can_place_on_foundation(dest, top):
            return False
        dest.apilar(top)
        origen.desapilar()
        self._flip_top_if_needed(origen)
        self.scoring.add_points(10)
        self.scoring.add_move()
        return True

    def move_waste_to_tableau(self, to_col: int) -> bool:
        top = self.waste.ver_tope()
        if not top:
            return False
        dest = self.tableau[to_col]
        if not self._can_place_on_tableau(dest, top):
            return False
        dest.apilar(top)
        self.waste.desapilar()
        self.scoring.add_points(5)
        self.scoring.add_move()
        return True

    def move_waste_to_foundation(self) -> bool:
        top = self.waste.ver_tope()
        if not top:
            return False
        dest = self.foundations[top.suit.value]
        if not self._can_place_on_foundation(dest, top):
            return False
        dest.apilar(top)
        self.waste.desapilar()
        self.scoring.add_points(10)
        self.scoring.add_move()
        return True

    # -------------------- Interfaz pública --------------------
    def apply_move(self, move: Dict[str, Any]) -> bool:
        """Aplica un movimiento representado por un dict.

        Tipos soportados:
            - {"type": "draw"}
            - {"type": "t2t", "from_col": i, "start_index": j, "to_col": k}
            - {"type": "t2f", "from_col": i}
            - {"type": "w2t", "to_col": i}
            - {"type": "w2f"}
        """

        mtype = move.get("type")
        self._snapshot_for_undo()
        ok = False
        if mtype == MoveType.DRAW.value:
            ok = self.draw_from_stock()
        elif mtype == MoveType.TABLEAU_TO_TABLEAU.value:
            ok = self.move_tableau_to_tableau(int(move["from_col"]), int(move["start_index"]), int(move["to_col"]))
        elif mtype == MoveType.TABLEAU_TO_FOUNDATION.value:
            ok = self.move_tableau_to_foundation(int(move["from_col"]))
        elif mtype == MoveType.WASTE_TO_TABLEAU.value:
            ok = self.move_waste_to_tableau(int(move["to_col"]))
        elif mtype == MoveType.WASTE_TO_FOUNDATION.value:
            ok = self.move_waste_to_foundation()
        else:
            # movimiento desconocido, descartar snapshot
            _ = self.history.pop_undo()
            return False

        if not ok:
            # revertir snapshot si no se pudo
            _ = self.history.pop_undo()
        return ok

    def hint(self) -> Optional[Dict[str, Any]]:
        """Devuelve un movimiento válido simple si existe."""

        # 1) waste -> foundation
        top = self.waste.ver_tope()
        if top and self._can_place_on_foundation(self.foundations[top.suit.value], top):
            return {"type": MoveType.WASTE_TO_FOUNDATION.value}
        # 2) waste -> tableau
        if top:
            for i, col in enumerate(self.tableau):
                if self._can_place_on_tableau(col, top):
                    return {"type": MoveType.WASTE_TO_TABLEAU.value, "to_col": i}
        # 3) tableau -> foundation
        for i, col in enumerate(self.tableau):
            c = col.ver_tope()
            if c and c.face_up and self._can_place_on_foundation(self.foundations[c.suit.value], c):
                return {"type": MoveType.TABLEAU_TO_FOUNDATION.value, "from_col": i}
        # 4) tableau -> tableau (buscar cadena válida)
        for i, col in enumerate(self.tableau):
            for start in range(len(col._cartas)):
                if start < len(col._cartas) and col._cartas[start].face_up:
                    cand = col._cartas[start]
                    for j, dest in enumerate(self.tableau):
                        if i == j:
                            continue
                        if self._can_place_on_tableau(dest, cand):
                            return {
                                "type": MoveType.TABLEAU_TO_TABLEAU.value,
                                "from_col": i,
                                "start_index": start,
                                "to_col": j,
                            }
        # 5) draw
        return {"type": MoveType.DRAW.value}

    def autoplay(self, limit: int = 200) -> int:
        """Mueve automáticamente cartas a la fundación hasta que no se pueda.

        Limita a ``limit`` movimientos para evitar loops.
        Retorna la cantidad de movimientos aplicados.
        """

        applied = 0
        while applied < limit:
            moved = False
            # waste -> foundation
            while self.move_waste_to_foundation():
                moved = True
                applied += 1
            # tableau tops -> foundation
            progress = True
            while progress:
                progress = False
                for i in range(7):
                    if self.move_tableau_to_foundation(i):
                        progress = True
                        moved = True
                        applied += 1
            if not moved:
                break
        return applied

    # -------------------- Deshacer / Rehacer --------------------
    def undo(self) -> bool:
        prev = self.history.pop_undo()
        if not prev:
            return False
        # guardar actual en redo
        self.history.push_redo(serialize_state(self.to_state()))
        self.from_state(prev)
        return True

    def redo(self) -> bool:
        nxt = self.history.pop_redo()
        if not nxt:
            return False
        # push actual a undo
        self.history.push_undo(serialize_state(self.to_state()))
        self.from_state(nxt)
        return True

