from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ml.src.analyze import analyze
from ml.src.text import normalize, read_file

app = FastAPI(title="Algoretica API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Entrada(BaseModel):
    texto: str


def _respond(text: str):
    text = normalize(text)
    if not text:
        raise HTTPException(400, "Texto vacío")
    # offsets refer to the normalized text, so return that same text
    return {"texto": text, "fragmentos": analyze(text)}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analizar")
def analyze_text(entrada: Entrada):
    return _respond(entrada.texto)


@app.post("/api/analizar/archivo")
async def analyze_file(archivo: UploadFile = File(...)):
    return _respond(read_file(archivo.filename or "", await archivo.read()))
