"""Sensationalism in the headline only (lexicon). Too few headlines to train a model; documented limit."""
from __future__ import annotations

import re

# ponytail: closed lexicon; extend with team-reviewed terms or learn it once there are enough labeled headlines
_LEXICON = re.compile(
    r"\b(macabr\w+|brutal\w*|salvaj\w+|escalofriant\w+|horror\w*|horrend\w+|espeluznant\w+|"
    r"sanguinari\w+|atroz|dantesc\w+|bestial\w*|terrorífic\w+|"
    r"descuartizad\w+|desmembrad\w+|ensangrentad\w+|a sangre fría|baño de sangre)\b",
    re.IGNORECASE,
)


def find(headline: str) -> list[tuple[int, int, str]]:
    """(start, end, text) of sensationalist expressions, offsets relative to the headline."""
    return [(m.start(), m.end(), m.group(0)) for m in _LEXICON.finditer(headline)]


if __name__ == "__main__":
    assert [t for *_, t in find("Macabro hallazgo: mujer brutalmente asesinada")] == ["Macabro", "brutalmente"]
    assert find("Investigan feminicidio de mujer de 24 años en Mérida") == []
    print("ok")
