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

## Motor de análisis (ml/)
Ver `docs/algoritmo.md`.
```
pip install -r ml/requirements.txt -r ml/requirements-dev.txt
python -m spacy download es_core_news_md
python -m ml.src.prepare ml/data/raw/        # notas -> CSV para etiquetar
python -m ml.src.train                       # entrena + ml/reports/metricas.md
python -m ml.src.train --kappa a.csv b.csv   # acuerdo entre anotadores
pytest ml/tests
```
