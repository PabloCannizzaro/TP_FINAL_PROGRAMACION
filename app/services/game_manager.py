import os
import json
import time
from typing import Dict, Optional
from ..core.game_engine import SolitaireGame

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

class GameManager:
    def __init__(self):
        self.games: Dict[str, SolitaireGame] = {}

    def new_game(self) -> str:
        game = SolitaireGame()
        game.new_game()
        game_id = str(int(time.time() * 1000))
        self.games[game_id] = game
        return game_id

    def get_game(self, game_id: str) -> SolitaireGame:
        if game_id not in self.games:
            raise KeyError(f"Game {game_id} not found")
        return self.games[game_id]

    def save_game(self, game_id: str, name: str) -> None:
        game = self.get_game(game_id)
        path = os.path.join(DATA_DIR, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(game.serialize(), f, ensure_ascii=False, indent=2)

    def load_game(self, name: str) -> str:
        path = os.path.join(DATA_DIR, f"{name}.json")
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        game = SolitaireGame.deserialize(state)
        game_id = str(int(time.time() * 1000))
        self.games[game_id] = game
        return game_id

    def list_saves(self):
        return [fn[:-5] for fn in os.listdir(DATA_DIR) if fn.endswith('.json')]

game_manager = GameManager()
