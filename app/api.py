# app/api.py
from flask import request, jsonify, render_template
from .services.game_manager import game_manager

def register_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.post("/new_game")
    def new_game():
        gid = game_manager.new_game()
        game = game_manager.get_game(gid)
        return jsonify({
            "game_id": gid,
            "tableau": game.get_tableau_state(),
            "foundations": game.get_foundation_state(),
            "stock": game.get_stock_state(),
            "waste": game.get_waste_state(),
            "game_won": game.is_won(),
            "moves": game.moves,
        })

    @app.post("/get_game_state")
    def get_state():
        gid = request.json.get("game_id")
        game = game_manager.get_game(gid)
        return jsonify({
            "game_id": gid,
            "tableau": game.get_tableau_state(),
            "foundations": game.get_foundation_state(),
            "stock": game.get_stock_state(),
            "waste": game.get_waste_state(),
            "game_won": game.is_won(),
            "moves": game.moves,
        })

    @app.post("/draw_card")
    def draw_card():
        gid = request.json.get("game_id")
        game = game_manager.get_game(gid)
        game.draw_card()
        return jsonify({
            "stock": game.get_stock_state(),
            "waste": game.get_waste_state(),
            "game_won": game.is_won(),
            "moves": game.moves,
        })

    @app.post("/move_card")
    def move_card():
        data = request.json
        gid = data.get("game_id")
        src = data.get("from_pile")
        dst = data.get("to_pile")
        game = game_manager.get_game(gid)

        ok = False
        if isinstance(src, dict) and src.get("type") == "tableau" and dst.get("type") == "foundation":
            ok = game.move_tableau_to_foundation(src["index"])
        elif src == "waste" and dst == "foundation":
            ok = game.move_waste_to_foundation()
        elif src == "waste" and isinstance(dst, dict) and dst.get("type") == "tableau":
            ok = game.move_waste_to_tableau(dst["index"])
        elif isinstance(src, dict) and isinstance(dst, dict) and src.get("type") == "tableau" and dst.get("type") == "tableau":
            ok = game.move_tableau_to_tableau(src["index"], dst["index"])

        return jsonify({
            "ok": ok,
            "tableau": game.get_tableau_state(),
            "foundations": game.get_foundation_state(),
            "stock": game.get_stock_state(),
            "waste": game.get_waste_state(),
            "game_won": game.is_won(),
            "moves": game.moves,
        })

    @app.post("/undo")
    def undo():
        gid = request.json.get("game_id")
        game = game_manager.get_game(gid)
        ok = game.undo()
        return jsonify({
            "ok": ok,
            "tableau": game.get_tableau_state(),
            "foundations": game.get_foundation_state(),
            "stock": game.get_stock_state(),
            "waste": game.get_waste_state(),
            "game_won": game.is_won(),
            "moves": game.moves,
        })

    @app.post("/hint")
    def hint():
        gid = request.json.get("game_id")
        game = game_manager.get_game(gid)
        return jsonify({"move": game.find_simple_hint()})

    @app.post("/save_game")
    def save_game():
        gid = request.json.get("game_id")
        name = request.json.get("name")
        game_manager.save_game(gid, name)
        return jsonify({"ok": True})

    @app.post("/load_game")
    def load_game():
        name = request.json.get("name")
        gid = game_manager.load_game(name)
        game = game_manager.get_game(gid)
        return jsonify({
            "game_id": gid,
            "tableau": game.get_tableau_state(),
            "foundations": game.get_foundation_state(),
            "stock": game.get_stock_state(),
            "waste": game.get_waste_state(),
            "game_won": game.is_won(),
            "moves": game.moves,
        })

    @app.get("/list_saves")
    def list_saves():
        return jsonify({"saves": game_manager.list_saves()})
