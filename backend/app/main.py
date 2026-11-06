from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ml.src.analyze import analyze
from ml.src.text import normalize, read_file

app = FastAPI(title="API - Proyecto basado en Algoretica Lab")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Entrada(BaseModel):
    texto: str


def _utf16(text: str, idx: int) -> int:
    return len(text[:idx].encode("utf-16-le")) // 2


def _respond(text: str):
    text = normalize(text)
    if not text:
        raise HTTPException(400, "Texto vacío")
    fragments = analyze(text)
    # Python offsets are code points; JS String.slice uses UTF-16 units (emojis count as 2)
    for f in fragments:
        f["inicio"], f["fin"] = _utf16(text, f["inicio"]), _utf16(text, f["fin"])
    # offsets refer to the normalized text, so return that same text
    return {"texto": text, "fragmentos": fragments}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analizar")
def analyze_text(entrada: Entrada):
    return _respond(entrada.texto)


@app.post("/api/analizar/archivo")
async def analyze_file(archivo: UploadFile = File(...)):
    return _respond(read_file(archivo.filename or "", await archivo.read()))
