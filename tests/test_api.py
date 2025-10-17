from fastapi.testclient import TestClient

from solitaire.backend.app import create_app


def test_api_lifecycle():
    app = create_app()
    client = TestClient(app)
    # initial state
    r = client.get('/api/game/state')
    assert r.status_code == 200
    # new game
    r = client.post('/api/game/new', json={"mode":"standard","draw":1})
    assert r.status_code == 200
    gid = r.json()["id"]
    # draw
    r = client.post('/api/game/move', json={"move": {"type":"draw"}})
    assert r.status_code == 200
    # hint
    r = client.post('/api/game/hint')
    assert r.status_code == 200
    # list saves
    r = client.get('/api/saves')
    assert r.status_code == 200
    assert any(item["id"] == gid for item in r.json()["items"])

