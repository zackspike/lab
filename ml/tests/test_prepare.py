import csv

from ml.src import model
from ml.src.prepare import prepare

NOTE = ("Macabro hallazgo en Mérida\n\n"
        "La víctima, de 24 años, fue hallada el lunes.\n"
        "“Fue un crimen pasional”, dijo un vecino.\n"
        "El cuerpo fue trasladado al Semefo.\n")


def _rows(path):
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def test_suggestions_in_separate_columns(tmp_path, monkeypatch):
    monkeypatch.setattr(model, "load", lambda: None)  # rules only: deterministic
    (tmp_path / "nota1.txt").write_text(NOTE, encoding="utf-8")
    out = tmp_path / "out.csv"
    prepare(tmp_path, out)
    rows = _rows(out)
    assert all(r["categoria"] == "" for r in rows)  # annotator decides
    assert rows[0]["sug_categoria"] == "sensacionalismo" and rows[0]["sug_fragmento"] == "Macabro"
    quote = next(r for r in rows if "crimen pasional" in r["texto"])
    assert (quote["sug_categoria"], quote["sug_fragmento"], quote["sug_postura"]) == \
        ("justificacion_agresor", "crimen pasional", "sin_postura")
    neutral = next(r for r in rows if "lunes" in r["texto"])
    assert neutral["sug_categoria"] == "" and neutral["sug_postura"] == "no_cita"


def test_without_suggestions(tmp_path):
    (tmp_path / "nota1.txt").write_text(NOTE, encoding="utf-8")
    out = tmp_path / "out.csv"
    prepare(tmp_path, out, suggest=False)
    assert "sug_categoria" not in _rows(out)[0]
