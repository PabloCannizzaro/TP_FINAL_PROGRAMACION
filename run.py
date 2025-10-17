# run.py
from flask import send_file
from pathlib import Path
from app import create_app

app = create_app()
for r in app.url_map.iter_rules():
    print("ROUTE:", r, "METHODS:", sorted(r.methods))
# --- BYPASS: servir index.html directo (diagnóstico) ---
@app.get("/")
def root_index():
    base = Path(__file__).resolve().parent  # carpeta raíz del repo
    return send_file(base / "templates" / "index.html")

# (deja el resto igual)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
