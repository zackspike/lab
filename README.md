# Algoretica
Detector de revictimización y violencia de género en notas periodísticas (hackathon).
Ver `CLAUDE.md` para contexto y arquitectura, y `docs/` para criterios y contrato de la API.

## Arranque rápido
```
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```
Prueba: `POST http://localhost:8000/api/analizar` con `{"texto": "..."}`.
