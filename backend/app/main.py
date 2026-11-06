import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader

from ml.src.analizar import analizar

app = FastAPI(title="Algoretica API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Entrada(BaseModel):
    texto: str


def _responder(texto: str):
    texto = texto.strip()
    if not texto:
        raise HTTPException(400, "Texto vacío")
    return {"texto": texto, "fragmentos": analizar(texto)}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analizar")
def analizar_texto(entrada: Entrada):
    return _responder(entrada.texto)


@app.post("/api/analizar/archivo")
async def analizar_archivo(archivo: UploadFile = File(...)):
    data = await archivo.read()
    if archivo.filename.lower().endswith(".pdf"):
        texto = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    else:
        texto = data.decode("utf-8", errors="ignore")
    return _responder(texto)
