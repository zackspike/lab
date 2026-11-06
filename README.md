# Proyecto basado en Algoretica Lab
Herramienta de análisis crítico del discurso periodístico con perspectiva de género: detecta revictimización y otras formas de violencia en notas periodísticas (hackathon).
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
python -m ml.src.prepare ml/data/raw/        # notas -> CSV para etiquetar (con sugerencias)
python -m ml.src.prepare ml/data/raw/prueba/ -o ml/data/labeled/prueba.csv --sin-sugerencias
python -m ml.src.train                       # entrena + ml/reports/metricas.md
python -m ml.src.train --kappa a.csv b.csv   # acuerdo entre anotadores
pytest ml/tests backend/tests
```

> El modelo entrenado (`ml/models/model.joblib`) no se versiona: después de clonar, ejecutar `python -m ml.src.train`.
> Sin modelo, la API funciona igual pero solo con reglas.
