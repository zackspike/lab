import pytest

from ml.src import model
from ml.src.analyze import analyze
from ml.src.text import normalize

NOTE = normalize(
    "Macabro hallazgo en la colonia Centro\n\n"
    "La joven salía sola de madrugada y vestía provocativamente.\n"
    "“Fue un crimen pasional”, dijo el abogado defensor.\n"
    "No obstante, la fiscalía descartó esa versión y lo investiga como feminicidio.\n"
    "El presunto agresor fue detenido.\n"
)
KEYS = {"id", "texto", "inicio", "fin", "categoria", "justificacion", "contexto",
        "alternativa", "criterio", "confianza", "origen"}


def _check_contract(frags):
    for f in frags:
        assert KEYS <= f.keys()
        assert NOTE[f["inicio"]:f["fin"]] == f["texto"]
        assert 0 <= f["confianza"] <= 1


def test_rules_only_fallback(monkeypatch):
    monkeypatch.setattr(model, "load", lambda: None)
    frags = analyze(NOTE)
    _check_contract(frags)
    cats = [f["categoria"] for f in frags]
    assert "sensacionalismo" in cats and "revictimizacion" in cats
    assert all("crimen pasional" not in f["texto"] for f in frags)  # refuted quote
    assert all("presunto agresor" not in f["texto"] for f in frags)


@pytest.mark.skipif(not model.MODEL_PATH.exists(), reason="run `python -m ml.src.train` first")
def test_with_model():
    frags = analyze(NOTE)
    _check_contract(frags)
    assert any(f["origen"] in {"regla+modelo", "modelo"} for f in frags)
    assert all("crimen pasional" not in f["texto"] for f in frags)
