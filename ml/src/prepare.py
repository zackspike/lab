"""Turn raw notes (.txt/.pdf) into a sentence-level CSV ready for labeling.

Usage: python -m ml.src.prepare ml/data/raw/ [-o ml/data/labeled/por_etiquetar.csv]
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ml.src.text import normalize, read_file, segment

# Column names are in Spanish on purpose: annotators fill this file by hand.
COLUMNS = ["id", "nota", "idx", "es_titulo", "texto", "categoria", "fragmento",
           "postura_cita", "justificacion", "etiquetador"]


def prepare(raw_dir: Path, out: Path) -> int:
    rows = []
    for path in sorted(raw_dir.iterdir()):
        if path.suffix.lower() not in {".txt", ".pdf"}:
            continue
        _, sentences = segment(normalize(read_file(path.name, path.read_bytes())))
        for s in sentences:
            rows.append({"id": f"{path.stem}-{s.idx}", "nota": path.stem, "idx": s.idx,
                         "es_titulo": int(s.is_headline), "texto": s.text})
    out.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig so Excel opens accents correctly
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_dir", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path("ml/data/labeled/por_etiquetar.csv"))
    args = ap.parse_args()
    print(f"{prepare(args.raw_dir, args.out)} oraciones -> {args.out}")
