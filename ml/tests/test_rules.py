import pytest

from ml.src.rules import find
from ml.src.text import nlp


def families(text: str) -> set[str]:
    return {h.family for h in find(nlp()(text))}


# (problematic, contrast that must NOT fire, expected family)
PAIRS = [
    ("Fue un crimen pasional.", "No fue un crimen pasional, sino un feminicidio.", "romantizacion"),
    ("Fue un crimen pasional.", "La fiscalía descartó que fuera un crimen pasional.", "romantizacion"),
    ("Fue un crimen pasional.", "Organizaciones pidieron no usar el término crimen pasional.", "romantizacion"),
    ("La supuesta víctima no presentó pruebas.", "El presunto agresor fue detenido.", "credibilidad"),
    ("Ella se lo buscó.", "Ninguna mujer se lo busca.", "culpa_victima"),
    ("La joven vestía provocativamente.", "La joven vestía uniforme escolar.", "culpa_victima"),
    ("La prostituta fue hallada sin vida.", "La víctima era trabajadora sexual.", "estereotipo"),
    ("El agresor era un hombre trabajador y respetable.", "El agresor trabajaba como taxista.", "perfil_exculpatorio"),
]


@pytest.mark.parametrize("bad,good,family", PAIRS)
def test_contrast_pairs(bad, good, family):
    assert family in families(bad)
    assert family not in families(good)


def test_hit_offsets_and_exposure():
    text = "La joven, que vive en la calle Sauce número 14, relató el abuso."
    hits = find(nlp()(text))
    assert [h.family for h in hits] == ["exposicion"]
    assert text[hits[0].start:hits[0].end] == hits[0].text


def test_negation_does_not_leak_across_clauses():
    assert "credibilidad" in families("La mujer no denunció antes, lo que pone en duda su relato.")
