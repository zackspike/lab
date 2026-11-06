"""Train the final model and write a comparison report.

Usage:
  python -m ml.src.train                      # CV comparison + fit final model + ml/reports/metricas.md
  python -m ml.src.train --kappa a.csv b.csv  # inter-annotator agreement on shared sentences
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (cohen_kappa_score, confusion_matrix, f1_score,
                             precision_recall_fscore_support)
from sklearn.model_selection import StratifiedKFold

from ml.src import model
from ml.src.model import NONE

REPORT = Path(__file__).resolve().parents[1] / "reports" / "metricas.md"
LABELS = [NONE] + model.BODY_CATEGORIES


def _rules_predict(inp: model.Inputs) -> np.ndarray:
    return np.array([h[0].category if h else NONE for h in inp.hits])


def _oof(X, cats: np.ndarray, folds) -> tuple[np.ndarray, np.ndarray]:
    """Out-of-fold P(problematic) and category for a feature matrix."""
    proba, pred_cat = np.zeros(len(cats)), np.empty(len(cats), dtype=object)
    for tr, te in folds:
        s1, s2 = model.fit(X[tr], cats[tr])
        proba[te] = s1.predict_proba(X[te])[:, 1]
        pred_cat[te] = s2.predict(X[te])
    return proba, pred_cat


def _final(proba, pred_cat, threshold) -> np.ndarray:
    return np.where(proba >= threshold, pred_cat, NONE)


def _system(proba, pred_cat, inp: model.Inputs, threshold) -> np.ndarray:
    """Exactly what analyze() does: model OR rule alert, quotes refuted by the note are dropped."""
    out = _final(proba, pred_cat, threshold)
    rule = _rules_predict(inp)
    out = np.where((out == NONE) & (rule != NONE), rule, out)
    return np.where(np.array(inp.stances) == "desmiente", NONE, out)


def _row(name, y, pred, folds) -> str:
    yb, pb = y != NONE, pred != NONE
    per_fold = [precision_recall_fscore_support(yb[te], pb[te], average="binary", zero_division=0)[:3]
                for _, te in folds]
    m, s = np.mean(per_fold, axis=0), np.std(per_fold, axis=0)
    macro = f1_score(y, pred, labels=model.BODY_CATEGORIES, average="macro", zero_division=0)
    return (f"| {name} | {m[0]:.2f} ± {s[0]:.2f} | {m[1]:.2f} ± {s[1]:.2f} | "
            f"{m[2]:.2f} ± {s[2]:.2f} | {macro:.2f} |")


def run() -> str:
    df = model.load_dataset()
    cats = df["categoria"].to_numpy()
    y_bin = (cats != NONE).astype(int)
    inp = model.inputs_from_df(df)
    folds = list(StratifiedKFold(5, shuffle=True, random_state=42).split(df, cats))

    emb = model.embed(inp.texts)
    X_hybrid = model.features(inp, emb)
    X_emb = emb
    X_tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1).fit_transform(inp.texts)
    # ponytail: TF-IDF vocabulary is fit on all data (no label leakage, tiny optimism); move into folds if it matters

    results = {}
    for name, X in [("TF-IDF + LR", X_tfidf), ("Embeddings + LR", X_emb), ("Híbrido (emb + reglas + citas)", X_hybrid)]:
        results[name] = _oof(X, cats, folds)

    proba_h, cat_h = results["Híbrido (emb + reglas + citas)"]
    threshold = model.pick_threshold(y_bin, proba_h)
    final = _system(proba_h, cat_h, inp, threshold)

    rows = [_row("Solo reglas", cats, _rules_predict(inp), folds)]
    rows += [_row(f"{n} (umbral 0.5)", cats, _final(p, c, 0.5), folds) for n, (p, c) in results.items()]
    rows.append(_row(f"**Sistema final** (híbrido umbral {threshold:.2f} + alertas de reglas + citas)",
                     cats, final, folds))

    cm = confusion_matrix(cats, final, labels=LABELS)
    cm_md = "| real \\ predicho | " + " | ".join(LABELS) + " |\n|" + "---|" * (len(LABELS) + 1) + "\n"
    cm_md += "\n".join(f"| {l} | " + " | ".join(map(str, r)) + " |" for l, r in zip(LABELS, cm))

    labeled_stance = df["postura_cita"].fillna("no_cita").replace("", "no_cita")
    quoted = labeled_stance != "no_cita"
    stance_acc = (labeled_stance[quoted] == df["stance"][quoted]).mean() if quoted.any() else float("nan")

    fp = df[(final != NONE) & (cats == NONE)]
    fn = df[(final == NONE) & (cats != NONE)]
    errors = lambda d, col: "\n".join(f"- {t} _(real: {c}, pred: {p})_" for t, c, p in
                                      zip(d["texto"][:10], d["categoria"][:10], col[:10])) or "- (ninguno)"

    # final model on all data
    s1, s2 = model.fit(X_hybrid, cats)
    pos = cats != NONE
    model.save({"stage1": s1, "stage2": s2, "threshold": threshold,
                "pos_emb": emb[pos], "pos_texts": df["texto"][pos].tolist(), "embedder": model.EMBEDDER})

    report = f"""# Métricas del modelo

Dataset: {len(df)} oraciones de cuerpo ({int(y_bin.sum())} problemáticas). Validación cruzada estratificada 5 folds (predicciones fuera de fold).
P/R/F1: detección binaria (problemática o no), media ± desviación entre folds. Macro-F1: categoría entre {", ".join(model.BODY_CATEGORIES)}.

| Sistema | Precisión | Recall | F1 | Macro-F1 categoría |
|---|---|---|---|---|
{chr(10).join(rows)}

Umbral elegido para precisión ≥ {model.TARGET_PRECISION}: **{threshold:.3f}**

## Matriz de confusión (sistema final)
{cm_md}

## Postura ante citas (heurística vs etiqueta)
Exactitud en {int(quoted.sum())} citas etiquetadas: **{stance_acc:.2f}**

## Falsos positivos (hasta 10)
{errors(fp, final[(final != NONE) & (cats == NONE)])}

## Falsos negativos (hasta 10)
{errors(fn, final[(final == NONE) & (cats != NONE)])}

> Con un dataset pequeño y sintético estas cifras son orientativas; se recalculan al añadir notas reales etiquetadas.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    return report


def kappa(a: Path, b: Path) -> float:
    da, db = (pd.read_csv(p, encoding="utf-8-sig", dtype=str) for p in (a, b))
    m = da.merge(db, on="id", suffixes=("_a", "_b"))
    ca, cb = (m[c].fillna("").replace("", NONE) for c in ("categoria_a", "categoria_b"))
    return cohen_kappa_score(ca, cb)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kappa", nargs=2, type=Path, metavar=("A", "B"))
    args = ap.parse_args()
    if args.kappa:
        print(f"Kappa de Cohen: {kappa(*args.kappa):.3f}")
    else:
        print(run())
