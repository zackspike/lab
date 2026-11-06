from ml.src.text import normalize, segment

NOTE = (
    "Hallan sin vida a mujer en Mérida\n\n"
    "La víctima, de 24 años, fue hallada el lunes en una vivienda de la colo-\n"
    "nia Centro. Vecinos dieron aviso\na la policía.\n"
)


def test_normalize_joins_lines_and_hyphens():
    t = normalize(NOTE)
    assert t.split("\n")[0] == "Hallan sin vida a mujer en Mérida"
    assert "colonia Centro" in t
    assert "aviso a la policía" in t


def test_offsets_and_headline():
    t = normalize(NOTE)
    _, sentences = segment(t)
    assert sentences[0].is_headline and not any(s.is_headline for s in sentences[1:])
    assert len(sentences) >= 3
    for s in sentences:
        assert t[s.start:s.end] == s.text
