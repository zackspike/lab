"""Turn raw notes (.txt/.pdf) into a sentence-level CSV ready for labeling.

Usage:
  python -m ml.src.prepare ml/data/raw/ [-o ml/data/labeled/por_etiquetar.csv]
  python -m ml.src.prepare ml/data/raw/prueba/ -o ml/data/labeled/prueba.csv --sin-sugerencias

By default each sentence gets the current system's suggestion in separate `sug_*` columns
(the label columns stay empty so the annotator decides, instead of just approving).
Use --sin-sugerencias for notes reserved for the final test, so suggestions can't bias them.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ml.src import quotes
from ml.src.text import normalize, read_file, segment

# Column names are in Spanish on purpose: annotators fill this file by hand.
COLUMNS = ["id", "nota", "idx", "es_titulo", "texto", "categoria", "fragmento",
           "postura_cita", "justificacion", "etiquetador"]
SUGGESTION_COLUMNS = ["sug_categoria", "sug_fragmento", "sug_postura", "sug_confianza", "sug_origen"]


def _suggestions(text: str, sentences) -> dict[int, dict]:
    """Sentence idx -> suggestion, from analyze() (model + rules, or rules only without a model)."""
    from ml.src.analyze import analyze

    body = [s.text for s in sentences if not s.is_headline]
    stances = iter(quotes.stance(body, i) for i in range(len(body)))
    out = {s.idx: {"sug_postura": "" if s.is_headline else next(stances)} for s in sentences}
    for f in analyze(text):
        s = next(s for s in sentences if f["inicio"] < s.end and f["fin"] > s.start)
        sug = out[s.idx]
        if "sug_categoria" in sug:  # several fragments in one sentence: keep the first, list all spans
            sug["sug_fragmento"] += " | " + f["texto"]
            continue
        sug.update(sug_categoria=f["categoria"], sug_confianza=f["confianza"], sug_origen=f["origen"],
                   sug_fragmento="" if f["texto"] == s.text else f["texto"])
    return out


def prepare(raw_dir: Path, out: Path, suggest: bool = True) -> int:
    rows = []
    for path in sorted(raw_dir.iterdir()):
        if path.suffix.lower() not in {".txt", ".pdf"}:
            continue
        text = normalize(read_file(path.name, path.read_bytes()))
        _, sentences = segment(text)
        sugs = _suggestions(text, sentences) if suggest else {}
        for s in sentences:
            rows.append({"id": f"{path.stem}-{s.idx}", "nota": path.stem, "idx": s.idx,
                         "es_titulo": int(s.is_headline), "texto": s.text, **sugs.get(s.idx, {})})
    out.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig so Excel opens accents correctly
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS + (SUGGESTION_COLUMNS if suggest else []))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_dir", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path("ml/data/labeled/por_etiquetar.csv"))
    ap.add_argument("--sin-sugerencias", action="store_true", help="notas reservadas para la prueba final")
    args = ap.parse_args()
    n = prepare(args.raw_dir, args.out, suggest=not args.sin_sugerencias)
    print(f"{n} oraciones -> {args.out}")
