from fastapi.testclient import TestClient

from backend.app.main import app


def test_offsets_are_utf16_for_js():
    text = "🔵 MACABRO HALLAZGO EN LA COLONIA CENTRO 🔫\nFue un crimen pasional, dijo un vecino 💔."
    r = TestClient(app).post("/api/analizar", json={"texto": text}).json()
    units = r["texto"].encode("utf-16-le")
    assert r["fragmentos"]
    for f in r["fragmentos"]:  # emulate JS texto.slice(inicio, fin)
        assert units[2 * f["inicio"]:2 * f["fin"]].decode("utf-16-le") == f["texto"]
