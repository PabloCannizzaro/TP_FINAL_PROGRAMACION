from fastapi.testclient import TestClient

from solitaire.backend.app import create_app


def test_sessions_isolate_state_per_client():
    app = create_app()
    c1 = TestClient(app)
    c2 = TestClient(app)

    # Different client ids
    h1 = {"X-Client-Id": "client-1"}
    h2 = {"X-Client-Id": "client-2"}

    # Start games for both clients
    r = c1.post('/api/game/new', json={"mode": "standard", "draw": 1, "player_name": "A"}, headers=h1)
    assert r.status_code == 200
    r = c2.post('/api/game/new', json={"mode": "standard", "draw": 1, "player_name": "B"}, headers=h2)
    assert r.status_code == 200

    # Move only on client 1
    r = c1.post('/api/game/move', json={"move": {"type": "draw"}, "name": "A"}, headers=h1)
    assert r.status_code == 200
    st1 = r.json()["state"]
    # Client 2 state should still have 0 moves
    r = c2.get('/api/game/state', headers=h2)
    assert r.status_code == 200
    st2 = r.json()
    assert int(st1["moves"]) >= 1
    assert int(st2["moves"]) == 0


def test_scoreboard_entries_include_stats():
    app = create_app()
    client = TestClient(app)
    h = {"X-Client-Id": "scoreboard-client"}
    # Start a new game with a name
    r = client.post('/api/game/new', json={"mode": "standard", "draw": 1, "player_name": "Tester"}, headers=h)
    assert r.status_code == 200
    # Simulate some moves; we may not win, but scoreboard endpoint should be reachable
    client.post('/api/game/move', json={"move": {"type": "draw"}, "name": "Tester"}, headers=h)
    # Query scoreboard; entries format should contain keys
    r = client.get('/api/scoreboard')
    assert r.status_code == 200
    items = r.json().get("items", [])
    # If any entry exists, ensure it has fields of interest
    if items:
        row = items[0]
        assert set(["name", "score", "moves", "seconds", "draw"]).issubset(set(row.keys()))

