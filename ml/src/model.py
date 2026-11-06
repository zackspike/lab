"""Sentence classifier: multilingual embeddings + rule/quote features -> 2-stage logistic regression.

Stage 1: problematic vs not (binary, threshold tuned for precision).
Stage 2: category among the 3 body categories (trained on positives only).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from ml.src import quotes, rules
from ml.src.text import nlp

EMBEDDER = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LABELED_DIR = Path(__file__).resolve().parents[1] / "data" / "labeled"
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "model.joblib"
NONE = "ninguna"
BODY_CATEGORIES = [rules.R, rules.J, rules.D]
TARGET_PRECISION = 0.8


@lru_cache(maxsize=1)
def embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDER)


def embed(texts: list[str]) -> np.ndarray:
    return embedder().encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)


# ---------- data ----------

def load_dataset(paths: list[Path] | None = None) -> pd.DataFrame:
    """Body sentences from every labeled CSV (except the empty template), with previous-sentence context."""
    paths = paths or [p for p in sorted(LABELED_DIR.glob("*.csv")) if p.name != "por_etiquetar.csv"]
    df = pd.concat([pd.read_csv(p, encoding="utf-8-sig", dtype=str) for p in paths], ignore_index=True)
    df["categoria"] = df["categoria"].fillna("").str.strip().replace("", NONE)
    df["idx"] = df["idx"].astype(int)
    df = df.sort_values(["nota", "idx"]).reset_index(drop=True)
    df["prev"] = df.groupby("nota")["texto"].shift(1).fillna("")
    df["stance"] = [quotes.stance(g["texto"].tolist(), i)
                    for _, g in df.groupby("nota", sort=False) for i in range(len(g))]
    return df[df["es_titulo"].astype(int) == 0].reset_index(drop=True)


# ---------- features ----------

@dataclass
class Inputs:
    texts: list[str]
    prevs: list[str]
    hits: list[list[rules.Hit]]
    stances: list[str]


def inputs_from_df(df: pd.DataFrame) -> Inputs:
    hits = [rules.find(doc) for doc in nlp().pipe(df["texto"].tolist())]
    return Inputs(df["texto"].tolist(), df["prev"].tolist(), hits, df["stance"].tolist())


def symbolic_features(inp: Inputs) -> np.ndarray:
    rule_flags = [rules.families_in(h) for h in inp.hits]
    stance_onehot = [[int(s == k) for k in quotes.STANCES] for s in inp.stances]
    return np.hstack([np.array(rule_flags), np.array(stance_onehot)]).astype(float)


def features(inp: Inputs, sentence_emb: np.ndarray | None = None) -> np.ndarray:
    """[emb(sentence) | emb(previous sentence) | rule family flags | quote stance one-hot]."""
    emb = embed(inp.texts) if sentence_emb is None else sentence_emb
    prev = np.zeros_like(emb)
    has_prev = [i for i, p in enumerate(inp.prevs) if p]
    if has_prev:
        prev[has_prev] = embed([inp.prevs[i] for i in has_prev])
    return np.hstack([emb, prev, symbolic_features(inp)])


# ---------- training / inference ----------

def _lr():
    from sklearn.linear_model import LogisticRegression

    return LogisticRegression(class_weight="balanced", max_iter=2000, C=1.0)


def fit(X: np.ndarray, categories: np.ndarray):
    y_bin = (categories != NONE).astype(int)
    stage1 = _lr().fit(X, y_bin)
    stage2 = _lr().fit(X[y_bin == 1], categories[y_bin == 1])
    return stage1, stage2


def pick_threshold(y_true: np.ndarray, proba: np.ndarray, target: float = TARGET_PRECISION) -> float:
    """Lowest threshold whose precision >= target (max recall); falls back to best-F1 threshold."""
    from sklearn.metrics import precision_recall_curve

    p, r, t = precision_recall_curve(y_true, proba)
    ok = np.where(p[:-1] >= target)[0]
    if len(ok):
        return float(t[ok[0]])
    f1 = 2 * p[:-1] * r[:-1] / np.clip(p[:-1] + r[:-1], 1e-9, None)
    return float(t[int(np.argmax(f1))])


def save(bundle: dict, path: Path = MODEL_PATH) -> None:
    import joblib

    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)


@lru_cache(maxsize=1)
def load(path: Path = MODEL_PATH) -> dict | None:
    import joblib

    return joblib.load(path) if path.exists() else None


@dataclass
class Prediction:
    proba: float          # P(problematic)
    category: str         # best body category (meaningful when proba >= threshold)
    neighbors: list[str]  # most similar labeled positive sentences


def predict(bundle: dict, inp: Inputs) -> list[Prediction]:
    emb = embed(inp.texts)
    X = features(inp, emb)
    proba = bundle["stage1"].predict_proba(X)[:, 1]
    cats = bundle["stage2"].predict(X)
    sims = emb @ bundle["pos_emb"].T
    out = []
    for i in range(len(inp.texts)):
        top = np.argsort(-sims[i])[:2]
        out.append(Prediction(float(proba[i]), str(cats[i]), [bundle["pos_texts"][j] for j in top]))
    return out
