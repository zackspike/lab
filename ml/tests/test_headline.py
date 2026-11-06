import pytest

from ml.src.headline import find

# real headlines (anonymized) labeled as sensationalist by the team, with the reason we expect
REAL = [
    ("Doble tragedia en Pensiones difícil de creer; eran la pareja ideal, dicen amigos", "sensacionalismo"),
    ("Hallan sin vida a dos estudiantes de la UV; investigan posible crimen pasional", "romantizacion"),
    ("📛Identifican a la Mujer As3sin4d4 de #Ticul y a su Feminicida 📛", "ortografia_disfrazada"),
    ("🔵 [NOMBRE] LE ROGÓ A [NOMBRE] PARA QUE REGRESARAN, ELLA NO QUISO Y SE FUERON JUNTOS 🚗🔫", "mayusculas"),
]
NEUTRAL = [
    "Investigan feminicidio de mujer de 24 años en Mérida",
    "Detienen a presunto feminicida en Valladolid",
    "Fiscalía investiga muerte de dos estudiantes en Xalapa",
]


@pytest.mark.parametrize("headline,reason", REAL)
def test_real_headlines_flagged(headline, reason):
    reasons = {r for *_, rs in find(headline) for r in rs}
    assert reason in reasons


@pytest.mark.parametrize("headline", NEUTRAL)
def test_neutral_headlines_not_flagged(headline):
    assert find(headline) == []


def test_offsets_and_merge():
    h = "MACABRO HALLAZGO EN LA COLONIA CENTRO 🔫"
    spans = find(h)
    assert len(spans) == 1 and spans[0][:2] == (0, len(h))  # caps covers all, others merged in
    assert {"mayusculas", "sensacionalismo", "emoji_violento"} <= set(spans[0][2])
