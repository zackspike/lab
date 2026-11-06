# Proyecto basado en Algoretica Lab — Análisis crítico del discurso periodístico con perspectiva de género

Hackathon de innovación social con IA. Prototipo/MVP con tiempo muy limitado: **prioriza simple y funcional sobre perfecto**.
Haz tareas pequeñas y verificables, y un `git commit` después de cada una.

## Qué es
Plataforma web donde se carga una nota periodística (PDF, TXT o texto pegado) sobre abuso, feminicidio o violencia contra mujeres y personas de la diversidad sexual y de género. El sistema señala:
1. **Fragmento exacto** problemático (con posición inicio/fin en el texto).
2. **Categoría**: revictimización, discriminación, estigmatización u otra forma de violencia.
3. **Justificación**: por qué es problemático, citando el criterio de `docs/criterios.md`.
4. **Contexto**: impacto del lenguaje y alternativa periodística recomendada.

Se plantea como **herramienta de análisis crítico del discurso periodístico con perspectiva de género**. Apoya el criterio humano, no lo sustituye.

## Principios (no negociables)
- **Revictimización ≠ cualquier discriminación.** Ver definición y criterios en `docs/criterios.md`.
- **El contexto manda.** Mencionar un feminicidio no es revictimizar. Una palabra sola no basta.
- **Precisión sobre cobertura.** Mejor marcar menos fragmentos, bien justificados.
- **Toda salida se justifica** y es revisable por una persona (la UI debe permitir confirmar/descartar).
- Lenguaje de la UI y de las justificaciones: español, tono respetuoso y no sensacionalista.

## Arquitectura (monorepo)
```
algoretica/
├── CLAUDE.md
├── docs/criterios.md      # definición, categorías, guía de etiquetado (fuente de verdad)
├── docs/api.md            # contrato de la API
├── ml/                    # LIBRERÍA de análisis (no es un servicio)
│   ├── data/{raw,labeled}
│   ├── notebooks/         # EDA y experimentos
│   └── src/               # preprocesamiento, reglas, modelo, analyze()
├── backend/app/           # FastAPI; importa `ml.src` y expone endpoints
└── frontend/              # UI: texto con fragmentos resaltados + panel de detalle
```

## Contrato central
`ml.src.analyze.analyze(text: str) -> list[dict]` y `POST /api/analizar` (ver `docs/api.md`).
Si cambias el formato, actualiza `docs/api.md`, backend y frontend juntos.

## Enfoque técnico (híbrido, por tiempo)
1. Segmentar el texto en oraciones (spaCy `es_core_news_md`), conservando offsets.
2. **Reglas/diccionario** de patrones documentados (`ml/src/rules.py`) → alta precisión y justificación fiable.
3. **Clasificador a nivel de oración**: embeddings multilingües (`paraphrase-multilingual-MiniLM-L12-v2`) + regresión logística. Baseline TF-IDF primero.
4. Combinar reglas + modelo; la justificación sale de plantillas por categoría citando el criterio.
5. Fine-tuning (BETO / XLM-R) solo si sobra tiempo y hay GPU.

## Orden de trabajo sugerido
1. Backend con respuesta simulada (mock) + frontend contra el mock → demo de punta a punta temprano.
2. `docs/criterios.md` afinado y dataset pequeño etiquetado (cientos de oraciones).
3. Reglas, luego modelo, reemplazando el mock.
4. Pulir demo. Última hora: nada de features nuevas.

## Comandos
- Backend: `pip install -r backend/requirements.txt && uvicorn backend.app.main:app --reload` (desde la raíz)
- ML: `pip install -r ml/requirements.txt && python -m spacy download es_core_news_md`
- Frontend: definir al elegir stack (React+Vite o Streamlit/Gradio si el tiempo aprieta).

## Reglas para Claude Code
- Código en inglés; comentarios breves; sin sobreingeniería.
- No inventes datos ni citas legales; si algo no está en `docs/criterios.md`, márcalo como pendiente.
- Datos de prueba: usa textos sintéticos o públicos; no incluyas datos personales de víctimas.
