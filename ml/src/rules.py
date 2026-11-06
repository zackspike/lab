"""Lemma-based linguistic rules (spaCy Matcher) with context guards.

Rules are high-precision cues: they feed the model as features, locate the exact
fragment to highlight, and raise an alert on their own when the model misses.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from ml.src.text import nlp

R, J, D = "revictimizacion", "justificacion_agresor", "discriminacion_estigmatizacion"

# family -> (category, list of Matcher patterns)
FAMILIES: dict[str, tuple[str, list[list[dict]]]] = {
    "culpa_victima": (R, [
        [{"LEMMA": {"IN": ["vestir", "vestido", "ropa", "foto", "fotografía"]}, "OP": "?"},
         {"LOWER": {"REGEX": "^provocativ"}}],
        [{"LEMMA": {"IN": ["andar", "salir", "caminar", "ir"]}}, {"LEMMA": "solo"}],
        [{"LOWER": "se"}, {"LOWER": {"IN": ["lo", "la"]}}, {"LEMMA": "buscar"}],
        [{"LEMMA": "lugar"}, {"LOWER": {"IN": ["indebido", "equivocado", "inadecuado"]}}],
    ]),
    "credibilidad": (R, [
        [{"LEMMA": {"IN": ["supuesto", "presunto"]}}, {"LEMMA": {"IN": ["víctima", "agraviado", "agraviada"]}}],
        [{"LOWER": "según"}, {"LOWER": "ella"}],
        [{"LEMMA": "poner"}, {"LOWER": "en"}, {"LOWER": "duda"}, {"LOWER": "su", "OP": "?"},
         {"LOWER": {"IN": ["relato", "versión", "testimonio", "denuncia"]}, "OP": "?"}],
    ]),
    "exposicion": (R, [
        [{"LOWER": {"IN": ["calle", "avenida", "andador", "privada"]}}, {"IS_TITLE": True, "OP": "+"},
         {"LOWER": {"IN": ["número", "no.", "#", "núm."]}, "OP": "?"}, {"LIKE_NUM": True}],
    ]),
    "romantizacion": (J, [
        [{"LEMMA": {"IN": ["crimen", "drama", "tragedia", "homicidio", "asesinato"]}},
         {"LEMMA": {"IN": ["pasional", "amoroso"]}}],
        [{"LEMMA": {"IN": ["arrebato", "ataque"]}}, {"LOWER": "de"}, {"LEMMA": "celo"}],
        [{"LOWER": {"REGEX": "^cegad"}}, {"LOWER": "por"}, {"LOWER": "los", "OP": "?"}, {"LEMMA": "celo"}],
        [{"LOWER": "por"}, {"LOWER": "amor"}],
        [{"LEMMA": "perder"}, {"LOWER": "el"}, {"LOWER": "control"}],
    ]),
    "perfil_exculpatorio": (J, [
        [{"LEMMA": "hombre"}, {"LOWER": {"IN": ["trabajador", "respetable", "ejemplar", "tranquilo", "honrado"]}}],
        [{"LOWER": {"IN": ["buen", "excelente", "tranquilo", "ejemplar"]}},
         {"LEMMA": {"IN": ["padre", "esposo", "hombre", "vecino", "muchacho", "hijo"]}}],
    ]),
    "estereotipo": (D, [
        [{"LOWER": "como"}, {"LEMMA": "todo"}, {"POS": {"IN": ["NOUN", "ADJ", "PROPN"]}}],
        [{"LOWER": "como"}, {"LOWER": "es"}, {"LOWER": "común"}, {"LOWER": "entre"}],
        [{"POS": "DET"}, {"LOWER": {"IN": ["prostituta", "travesti", "homosexual", "sexoservidora",
                                            "meretriz", "mujerzuela"]}}],
        [{"LOWER": "vida"}, {"LOWER": {"IN": ["galante", "fácil", "alegre", "desordenada", "licenciosa"]}}],
        [{"LOWER": {"IN": ["dudosa", "mala"]}}, {"LOWER": "reputación"}],
        [{"LOWER": "se"}, {"LOWER": "dan"}, {"LOWER": "a"}, {"LOWER": "respetar"}],
    ]),
}

NEGATIONS = {"no", "nunca", "jamás", "ni", "tampoco", "ninguno", "ninguna", "nadie"}
# The sentence talks *about* the expression (critique/denial), not with it.
META_PREFIXES = ("término", "llamar", "descart", "denomin", "calific", "expresión", "etiqueta")


@dataclass
class Hit:
    rule_id: str
    family: str
    category: str
    start: int  # char offsets in the analyzed text
    end: int
    text: str


@lru_cache(maxsize=1)
def _matcher():
    from spacy.matcher import Matcher

    m = Matcher(nlp().vocab)
    for family, (_, patterns) in FAMILIES.items():
        for i, p in enumerate(patterns):
            m.add(f"{family}:{i}", [p])
    return m


def _negated(span) -> bool:
    """True if the clause governing the match is negated ('no fue un crimen pasional')."""
    tok = span.root
    while tok.pos_ not in {"VERB", "AUX"} and tok.head.i != tok.i:
        if tok.dep_.startswith("nsubj"):
            return False  # the match is the subject; 'no' negates the predicate, not it
        tok = tok.head
    for child in tok.children:
        if child.lower_ in NEGATIONS:
            return True
        if child.dep_.startswith("nsubj") and any(c.lower_ in NEGATIONS for c in child.children):
            return True
    return False


def _meta(sent) -> bool:
    return any(t.lower_.startswith(META_PREFIXES) for t in sent)


def find(doc) -> list[Hit]:
    from spacy.util import filter_spans

    spans = []
    for match_id, s, e in _matcher()(doc):
        span = doc[s:e]
        span.label_ = nlp().vocab.strings[match_id]
        spans.append(span)
    hits = []
    for span in filter_spans(spans):  # keep longest, non-overlapping
        if _negated(span) or _meta(span.sent):
            continue
        family = span.label_.split(":")[0]
        hits.append(Hit(span.label_, family, FAMILIES[family][0], span.start_char, span.end_char, span.text))
    return hits


def families_in(hits: list[Hit]) -> list[int]:
    """Binary feature vector, one slot per family (stable order)."""
    present = {h.family for h in hits}
    return [int(f in present) for f in FAMILIES]
