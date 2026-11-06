"""Reported-speech detection and the note's stance toward the quote.

Stances: no_cita | avala | sin_postura | desmiente (see docs/criterios.md).
ponytail: cue-word heuristic; the dataset's `postura_cita` column lets us evaluate it and later learn it.
"""
from __future__ import annotations

import re

STANCES = ["no_cita", "avala", "sin_postura", "desmiente"]

_REPORT_VERBS = r"(declar|dij|dice|afirm|señal|asegur|coment|explic|indic|refiri|manifest|sostuv|relat)\w*"
_QUOTE = re.compile(
    r"[“«\"][^”»\"]{3,}[”»\"]"                       # text in quotes
    r"|\bsegún\b"                                     # según X
    rf"|,\s*{_REPORT_VERBS}\b"                        # ..., declaró un vecino
    rf"|\b{_REPORT_VERBS}\s+que\b",                   # afirmó que ...
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
    """Stance of the note toward the quote in sentence i, looking at it and the next 2 sentences."""
    if not is_quote(sentences[i]):
        return "no_cita"
    following = sentences[i + 1:i + 3]
    # refutation inside the quoting sentence itself only counts outside the quoted words
    own = re.sub(r"[“«\"][^”»\"]*[”»\"]", "", sentences[i])
    if _REFUTES.search(own) or any(_REFUTES.search(s) for s in following):
        return "desmiente"
    if any(_ENDORSES.search(s) for s in following):
        return "avala"
    quoted = _content_words(sentences[i])
    if any(not is_quote(s) and len(quoted & _content_words(s)) >= 2 for s in following[:1]):
        return "avala"  # narrator restates the claim in their own voice
    return "sin_postura"
