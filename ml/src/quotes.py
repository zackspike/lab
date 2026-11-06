"""Reported-speech detection and the note's stance toward the quote.

Stances: no_cita | avala | sin_postura | desmiente (see docs/criterios.md).
ponytail: cue-word heuristic; the dataset's `postura_cita` column lets us evaluate it and later learn it.
"""
from __future__ import annotations

import re

STANCES = ["no_cita", "avala", "sin_postura", "desmiente"]

# Explicit conjugated forms: loose stems matched nouns ("indicios que"). "informamos" is left out on
# purpose: it is the outlet citing itself, not a third party.
_REPORT_VERBS = (
    r"(dijo|dijeron|dice|dicen|declaró|declararon|afirmó|afirmaron|afirma|señaló|señalaron|"
    r"aseguró|aseguraron|asegura|aseguran|comentó|comentaron|explicó|explicaron|indicó|indicaron|"
    r"refirió|refirieron|manifestó|manifestaron|expresó|expresaron|sostuvo|sostuvieron|relató|"
    r"relataron|mencionó|mencionaron|catalogó|catalogaron|narró|narraron)"
)
# "según datos recabados" / "de acuerdo con los reportes" cite data, not a person's claim
_DATA_SOURCE = r"(?!\s+(?:\w+\s+)?(datos|cifras|reportes?|informaci\w+|registros|estadísticas)\b)"
_QUOTE = re.compile(
    r"[“«\"][^”»\"]{3,}[”»\"]"                       # text in quotes
    rf"|\b(según|de acuerdo con){_DATA_SOURCE}"       # según X / de acuerdo con X
    rf"|,\s*(como\s+)?(lo\s+|la\s+)?{_REPORT_VERBS}\b"  # ..., declaró un vecino / como lo catalogaron
    rf"|\b{_REPORT_VERBS}\s+que\b"                    # afirmó que ...
    r"|\bversiones que han trascendido\b|\bse puede leer\b",
    re.IGNORECASE,
)
_REFUTES = re.compile(
    r"\bsin embargo\b|\bno obstante\b|\bfals[oa]\b|\bdescart\w*|\bcontrario a\b|\bdesmint\w*|\brechaz\w*"
    r"|\b(especialistas|expertas?|organizaciones|colectiv\w+)\b[^.]{0,40}\b(advi\w+|señal\w+|recuerd\w+|critic\w+)"
    r"|\bno justific\w*|\bbusca\w* justificar\b",
    re.IGNORECASE,
)
_ENDORSES = re.compile(r"\befectivamente\b|\ben efecto\b|\bcomo se confirmó\b|\bse confirmó\b", re.IGNORECASE)
_WORD = re.compile(r"\w{6,}")


def is_quote(text: str) -> bool:
    return bool(_QUOTE.search(text))


def _content_words(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text)}


def stance(sentences: list[str], i: int) -> str:
    """Stance of the note toward the quote in sentence i.

    Only the quoting sentence (outside the quoted words) and the NEXT sentence count: a contrast
    further away does not undo the earlier reproduction (team decision, docs/criterios.md).
    """
    if not is_quote(sentences[i]):
        return "no_cita"
    nxt = sentences[i + 1] if i + 1 < len(sentences) else ""
    own = re.sub(r"[“«\"][^”»\"]*[”»\"]", "", sentences[i])
    if _REFUTES.search(own) or _REFUTES.search(nxt):
        return "desmiente"
    if _ENDORSES.search(nxt):
        return "avala"
    if nxt and not is_quote(nxt) and len(_content_words(sentences[i]) & _content_words(nxt)) >= 2:
        return "avala"  # narrator restates the claim in their own voice
    return "sin_postura"
