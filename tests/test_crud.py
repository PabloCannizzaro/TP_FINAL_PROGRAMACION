from pathlib import Path

from solitaire.backend.domain.partida import Partida
from solitaire.backend.domain.repositorio import RepositorioPartidasJSON


def test_crud_json_repo(tmp_path: Path):
    repo = RepositorioPartidasJSON(tmp_path / "saves.json")
    p = Partida.nueva(id="abc", modo="standard", draw_count=1, seed=123)
    repo.crear(p)
    got = repo.obtener("abc")
    assert got is not None and got.id == "abc"
    got.puntaje += 10
    repo.actualizar(got)
    assert repo.obtener("abc").puntaje == got.puntaje
    repo.eliminar("abc")
    assert repo.obtener("abc") is None

