from fastapi.testclient import TestClient

from solitaire.backend.app import create_app


def test_invalid_move_returns_400():
    app = create_app()
    client = TestClient(app)
    # ensure game exists
    r = client.post('/api/game/new', json={"mode":"standard","draw":1})
    assert r.status_code == 200
    # send invalid move payload
    r = client.post('/api/game/move', json={"move": {"type": "unknown"}})
    assert r.status_code == 400

