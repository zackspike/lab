"""Library entry point: analyze(text) -> list of fragments (contract in docs/api.md).

Expects text already normalized with ml.src.text.normalize (offsets refer to it).
The ML model is the main detector; rules locate fragments and act as high-precision alerts.
Without a trained model (ml/models/model.joblib) it degrades to rules only.
"""
from __future__ import annotations

from ml.src import headline, model, quotes, rules
from ml.src.templates import render, render_headline
from ml.src.text import segment

RULE_CONFIDENCE = 0.9  # ponytail: rules-only precision measured on the seed (ml/reports/metricas.md); recompute with real data
QUOTE_PENALTY = 0.6    # quote reproduced without stance


def _fragment(text, start, end, category, key, confidence, origin, stance="no_cita", similar=None) -> dict:
    f = {"texto": text[start:end], "inicio": start, "fin": end, "categoria": category,
         **render(key, stance), "confianza": round(confidence, 3), "origen": origin}
    if stance != "no_cita":
        f["postura_cita"] = stance
    if similar:
        f["similares"] = similar
    return f


def analyze(text: str) -> list[dict]:
    doc, sentences = segment(text)
    out: list[dict] = []

    if any(s.is_headline for s in sentences):  # whole first line: spaCy may split it ("🔵 [NOMBRE] LE ROGÓ…")
        for a, b, reasons in headline.find(text[:text.find("\n")]):
            out.append({"texto": text[a:b], "inicio": a, "fin": b,
                        "categoria": "sensacionalismo", **render_headline(reasons),
                        "confianza": RULE_CONFIDENCE, "origen": "regla"})

    body = [s for s in sentences if not s.is_headline]
    if body:
        all_hits = rules.find(doc)
        hits = [[h for h in all_hits if s.start <= h.start and h.end <= s.end] for s in body]
        texts = [s.text for s in body]
        inp = model.Inputs(texts, [""] + texts[:-1], hits, [quotes.stance(texts, i) for i in range(len(body))])
        bundle = model.load()
        preds = model.predict(bundle, inp) if bundle else [None] * len(body)

        for s, sent_hits, stance, pred in zip(body, hits, inp.stances, preds):
            if stance == "desmiente":
                continue  # the note itself refutes the quoted claim
            penalty = QUOTE_PENALTY if stance == "sin_postura" else 1.0
            flagged = pred is not None and pred.proba >= bundle["threshold"]
            if sent_hits:  # rule wins on category and gives the exact span
                origin = "regla+modelo" if flagged else "regla"
                conf = max(pred.proba, RULE_CONFIDENCE) if flagged else RULE_CONFIDENCE
                for h in sent_hits:
                    out.append(_fragment(text, h.start, h.end, h.category, h.family, conf * penalty, origin, stance))
            elif flagged:
                out.append(_fragment(text, s.start, s.end, pred.category, pred.category, pred.proba * penalty,
                                     "modelo", stance, pred.neighbors))

    out.sort(key=lambda f: f["inicio"])
    for i, f in enumerate(out, 1):
        f["id"] = f"f{i}"
    return out
