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


# --- phrasing from real (anonymized) notes ---

def test_real_attribution_forms():
    assert is_quote("Ambos triunfadores, de acuerdo con la opinión que tienen de ellos sus amigos.")
    assert is_quote("Amigos en común expresaron que les resulta difícil de creer.")
    assert is_quote("[NOMBRE] era considerado un buen muchacho, como lo catalogaron sus amigos.")
    assert is_quote("Compañeros universitarios asegura que [NOMBRE] ya había terminado la relación.")


def test_not_quotes():
    assert not is_quote("Las diligencias permitieron el aseguramiento de diversos indicios que serían analizados.")
    assert not is_quote("Según datos recabados, los hechos ocurrieron antes de las 7 de la mañana.")
    assert not is_quote("De acuerdo con los reportes difundidos, ambos salieron de la cafetería.")
    assert not is_quote("Como informamos, los hechos ocurrieron alrededor de las 4 de la tarde.")


def test_contrast_two_sentences_later_does_not_refute():
    s = ["[NOMBRE] era considerado un buen muchacho, como lo catalogaron sus amigos.",
         "Sus vecinos tienen la misma opinión de él.",
         "Sin embargo, luego surgieron otras versiones sobre la personalidad del joven."]
    assert stance(s, 0) == "sin_postura"
