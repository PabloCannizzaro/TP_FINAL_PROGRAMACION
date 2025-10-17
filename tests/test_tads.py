import pytest

from solitaire.tads.cola import ColaTAD
from solitaire.tads.lista import ListaTAD
from solitaire.tads.deque_historial import HistorialMovimientos


def test_cola_tad_fifo():
    q = ColaTAD([1, 2, 3])
    assert q.desencolar() == 1
    q.encolar(4)
    assert q.desencolar() == 2
    assert q.desencolar() == 3
    assert q.desencolar() == 4
    with pytest.raises(ValueError):
        q.desencolar()


def test_lista_tad_ops():
    lst = ListaTAD([1, 2, 3])
    lst.insertar(1, 99)
    assert lst.to_list() == [1, 99, 2, 3]
    assert lst.quitar(2) == 2
    sub = lst.sublista(1)
    assert sub.to_list() == [99, 3]
    lst.concatenar(ListaTAD([7]))
    assert lst.to_list() == [1, 99, 3, 7]


def test_historial_undo_redo():
    h = HistorialMovimientos[int]()
    h.push_undo(1)
    h.push_undo(2)
    assert h.can_undo()
    assert h.pop_undo() == 2
    h.push_redo(2)
    assert h.can_redo()
    assert h.pop_redo() == 2

