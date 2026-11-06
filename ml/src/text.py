"""Ingestion, normalization and sentence segmentation (offsets over normalized text)."""
from __future__ import annotations

import io
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

SPACY_MODEL = "es_core_news_md"
_SENTENCE_END = (".", "!", "?", ":", "”", '"', "»")


@lru_cache(maxsize=1)
def nlp():
    import spacy

    return spacy.load(SPACY_MODEL)


def read_file(name: str, data: bytes) -> str:
    if name.lower().endswith(".pdf"):
        from pypdf import PdfReader

        return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    return data.decode("utf-8", errors="ignore")


def normalize(text: str) -> str:
    """NFC, de-hyphenate line breaks, join wrapped lines, collapse spaces.

    Paragraph breaks are kept as a single '\n'; the first line is the headline.
    """
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in text.split("\n")]
    paragraphs: list[str] = []
    current = ""
    for line in lines:
        if not line:
            if current:
                paragraphs.append(current)
                current = ""
            continue
        current = f"{current} {line}" if current else line
        # ponytail: wrapped-line heuristic (end punctuation / first line); odd PDF layouts may need tuning
        if not paragraphs or current.endswith(_SENTENCE_END):
            paragraphs.append(current)
            current = ""
    if current:
        paragraphs.append(current)
    return "\n".join(paragraphs)


@dataclass
class Sentence:
    idx: int
    text: str
    start: int
    end: int
    is_headline: bool


def segment(text: str):
    """Return (spaCy Doc, sentences), also splitting at line breaks."""
    doc = nlp()(text)
    headline_end = text.find("\n")
    sentences: list[Sentence] = []
    for sent in doc.sents:
        pos = sent.start_char
        for chunk in re.split(r"(\n)", text[sent.start_char:sent.end_char]):
            if chunk.strip():
                start = pos + len(chunk) - len(chunk.lstrip())
                end = pos + len(chunk.rstrip())
                sentences.append(Sentence(len(sentences), text[start:end], start, end, end <= headline_end))
            pos += len(chunk)
    return doc, sentences
