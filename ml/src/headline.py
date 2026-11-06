"""Sensationalism in the headline only. Too few headlines to train a model; documented limit.

Reasons (each has a template in templates.py):
  sensacionalismo        sensationalist / dramatizing lexicon
  ortografia_disfrazada  violent words disguised with digits ("As3sin4d4")
  emoji_violento         weapon / blood / shock emojis
  mayusculas             headline mostly in capital letters
  <rule family>          any body rule (rules.py) fired on the headline, e.g. romantizacion
"""
from __future__ import annotations

import re

from ml.src import rules
from ml.src.text import nlp

# ponytail: closed lexicons; extend with team-reviewed terms or learn them once there are enough labeled headlines
_LEXICON = re.compile(
    r"\b(macabr\w+|brutal\w*|salvaj\w+|escalofriant\w+|horror\w*|horrend\w+|espeluznant\w+|"
    r"sanguinari\w+|atroz|dantesc\w+|bestial\w*|terrorífic\w+|"
    r"descuartizad\w+|desmembrad\w+|ensangrentad\w+|a sangre fría|baño de sangre|"
    r"tragedia|fatal desenlace|pareja (ideal|perfecta)|historia de amor|difícil de creer)\b",
    re.IGNORECASE,
)
_LEET = str.maketrans("3410578@", "eaiostba")  # 1:1 char map keeps offsets
_LEET_WORD = re.compile(r"\b(?=\w*\d)(?=\w*[^\W\d_])\w+")
_VIOLENT_STEMS = ("asesin", "muert", "homicid", "feminicid", "bala", "mat", "violad", "secuestr")
_EMOJI = re.compile("[🔫🔪🩸💀☠⚰😱🤬]")
CAPS_MIN_WORDS, CAPS_RATIO = 4, 0.7


def _signals(headline: str) -> list[tuple[int, int, str]]:
    out = [(m.start(), m.end(), "sensacionalismo") for m in _LEXICON.finditer(headline)]
    out += [(m.start(), m.end(), "ortografia_disfrazada") for m in _LEET_WORD.finditer(headline)
            if any(s in m.group(0).lower().translate(_LEET) for s in _VIOLENT_STEMS)]
    out += [(m.start(), m.end(), "emoji_violento") for m in _EMOJI.finditer(headline)]
    letters = [c for c in headline if c.isalpha()]
    if len(headline.split()) >= CAPS_MIN_WORDS and letters and \
            sum(c.isupper() for c in letters) / len(letters) >= CAPS_RATIO:
        out.append((0, len(headline), "mayusculas"))
    out += [(h.start, h.end, h.family) for h in rules.find(nlp()(headline))]
    return sorted(out)


def find(headline: str) -> list[tuple[int, int, list[str]]]:
    """(start, end, reasons) relative to the headline; overlapping signals are merged."""
    merged: list[tuple[int, int, list[str]]] = []
    for start, end, reason in _signals(headline):
        if merged and start < merged[-1][1]:
            s, e, reasons = merged[-1]
            merged[-1] = (s, max(e, end), reasons + [reason] * (reason not in reasons))
        else:
            merged.append((start, end, [reason]))
    return merged
