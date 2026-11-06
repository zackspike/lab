from ml.src.quotes import is_quote, stance


def test_not_a_quote():
    assert stance(["La víctima fue hallada el lunes."], 0) == "no_cita"


def test_refuted():
    s = ["“Fue un crimen pasional”, dijo el abogado defensor.",
         "No obstante, la fiscalía descartó esa versión y lo investiga como feminicidio."]
    assert stance(s, 0) == "desmiente"


def test_endorsed():
    s = ["Según la madre del detenido, la joven lo provocaba constantemente.",
         "Efectivamente, la joven tenía discusiones con él."]
    assert stance(s, 0) == "avala"


def test_endorsed_by_restating():
    s = ["“Ella provocaba constantemente al acusado”, declaró un familiar.",
         "La joven provocaba constantemente discusiones en casa."]
    assert stance(s, 0) == "avala"


def test_no_stance():
    s = ["“Ella estaba en el lugar equivocado”, comentó un policía.", "La mujer tenía 31 años."]
    assert stance(s, 0) == "sin_postura"


def test_detection_forms():
    assert is_quote("El fiscal afirmó que no hay más detenidos.")
    assert is_quote("Según vecinos, se escucharon gritos.")
    assert not is_quote("La mujer desapareció el viernes.")
