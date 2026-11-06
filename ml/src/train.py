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


def _pooled(y_true: np.ndarray, y_pred: np.ndarray) -> str:
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
    return f"{p:.2f} | {r:.2f} | {f:.2f}"


def _by_source(df, systems: dict[str, np.ndarray]) -> str:
    lines = ["| Fuente | Oraciones | Positivos | Sistema | Precisión | Recall | F1 |", "|---|---|---|---|---|---|---|"]
    for src, idx in df.groupby("fuente").groups.items():
        y = df.loc[idx, "categoria"].to_numpy() != NONE
        warn = " ⚠️ no concluyente" if y.sum() < 15 else ""
        for name, pred in systems.items():
            lines.append(f"| {src} | {len(idx)} | {int(y.sum())}{warn} | {name} | {_pooled(y, pred[idx] != NONE)} |")
    return "\n".join(lines)


def _headlines() -> str:
    from ml.src import headline

    hd = model.load_dataset(headlines=True)
    lines = ["| Fuente | Titulares | Sensacionalistas | Precisión | Recall | F1 |", "|---|---|---|---|---|---|"]
    for src, g in hd.groupby("fuente"):
        y = (g["categoria"] != NONE).to_numpy()
        pred = np.array([bool(headline.find(t)) for t in g["texto"]])
        lines.append(f"| {src} | {len(g)} | {int(y.sum())} | {_pooled(y, pred)} |")
    return "\n".join(lines)


def _quotes(df) -> str:
    from ml.src.quotes import is_quote

    label = df["postura_cita"].fillna("").replace("", "no_cita")
    lines = ["| Fuente | Detección de cita (exactitud, todas las oraciones) | Postura correcta en oraciones problemáticas citadas |",
             "|---|---|---|"]
    for src, idx in df.groupby("fuente").groups.items():
        det = (np.array([is_quote(t) for t in df.loc[idx, "texto"]]) == (label[idx] != "no_cita")).mean()
        prob = idx[(df.loc[idx, "categoria"] != NONE) & (label[idx] != "no_cita")]
        acc = f"{(label[prob] == df.loc[prob, 'stance']).mean():.2f} ({len(prob)})" if len(prob) else "— (0)"
        lines.append(f"| {src} | {det:.2f} ({len(idx)}) | {acc} |")
    return "\n".join(lines)


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

    by_source = _by_source(df, {"Solo reglas": _rules_predict(inp), "Híbrido (umbral 0.5)": _final(proba_h, cat_h, 0.5),
                                "Sistema final": final})

    def errors(mask) -> str:
        d = df.assign(pred=final)[mask]
        d = d.sort_values("fuente", key=lambda s: s == "semilla_sintetica")  # real notes first
        return "\n".join(f"- [{r.fuente}] {r.texto} _(real: {r.categoria}, pred: {r.pred})_"
                         for r in d.head(10).itertuples()) or "- (ninguno)"

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

## Por fuente (predicciones fuera de fold, agrupadas)
La semilla sintética la escribió el equipo junto con las reglas: sus cifras son optimistas. Las notas reales son la medida que importa.

{by_source}

## Titulares (sensacionalismo)
{_headlines()}

## Citas
{_quotes(df)}

La postura solo se evalúa en oraciones problemáticas, donde cambia el resultado (criterio en `docs/criterios.md`).

## Falsos positivos (hasta 10, primero notas reales)
{errors((final != NONE) & (cats == NONE))}

## Falsos negativos (hasta 10, primero notas reales)
{errors((final == NONE) & (cats != NONE))}

> Con un dataset pequeño estas cifras son orientativas; se recalculan al añadir notas reales etiquetadas.
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
