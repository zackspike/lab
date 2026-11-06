# Algoritmo de análisis

Herramienta de apoyo al análisis crítico del discurso periodístico con perspectiva de género. **El modelo de aprendizaje automático es el detector principal**; las reglas lingüísticas lo complementan como features, localizadores de fragmento y alertas de alta precisión. Criterios en [`criterios.md`](criterios.md).

## Pipeline
```
texto/PDF → normalizar + segmentar (offsets) ─┬→ titular → sensacionalismo (léxico)
                                              └→ cada oración del cuerpo:
                              reglas (hits + spans)  ┐
                              citas (¿cita? postura) ├→ features → modelo 2 etapas → fusión → plantillas → fragmentos
                              embeddings MiniLM      ┘
```

1. **Ingesta y normalización** (`ml/src/texto.py`). PDF → texto con `pypdf`; Unicode NFC, unión de palabras cortadas por guion, espacios colapsados. Todos los offsets se calculan sobre este texto normalizado, que es el que devuelve la API.
2. **Segmentación**. spaCy `es_core_news_md` → oraciones con `inicio/fin`, lemas, dependencias y entidades. La primera línea es el titular.
3. **Reglas** (`ml/src/reglas.py`). Patrones por lema (spaCy `Matcher`) agrupados en familias. Guardas de contexto: negación cercana ("no fue un crimen pasional") y análisis de dependencias ("presunta víctima" ≠ "presunto agresor").
4. **Citas** (`ml/src/citas.py`). Detecta discurso referido y estima la postura de la nota (avala / sin postura / desmiente) buscando señales en la oración y las dos siguientes.
5. **Modelo** (`ml/src/modelo.py`).
   - Representación: embedding multilingüe `paraphrase-multilingual-MiniLM-L12-v2` de *oración previa + oración* (contexto), concatenado con flags de reglas y features de cita.
   - Etapa 1: regresión logística binaria (problemática / no), `class_weight="balanced"`; umbral elegido por validación cruzada para precisión ≥ 0.8.
   - Etapa 2: regresión logística de 3 clases, entrenada solo con positivos.
   - Explicabilidad: se adjuntan los ejemplos etiquetados más parecidos (similitud coseno).
6. **Fusión** (`ml/src/analizar.py`). Modelo y regla coinciden → `origen="regla+modelo"`, se resalta el fragmento de la regla. Solo modelo sobre el umbral → se resalta la oración. Solo regla → alerta de alta precisión (`origen="regla"`). Citas: `desmiente` anula, `sin_postura` reduce la confianza.
7. **Justificación** (`ml/src/plantillas.py`). Plantillas por categoría/familia que citan `criterios.md` y proponen una alternativa periodística. Sin texto generado libremente.

## Evaluación
`python -m ml.src.entrenar` compara con validación cruzada estratificada (5 folds):

| Sistema | Descripción |
|---|---|
| Reglas | Solo patrones |
| TF-IDF + LR | n-gramas de caracteres 3–5 |
| Embeddings + LR | MiniLM |
| Híbrido | MiniLM + features de reglas y citas (sistema final) |

Reporta precisión, recall y F1 (binario y por categoría), matriz de confusión y ejemplos de falsos positivos/negativos en `ml/reports/metricas.md`.

## Límites conocidos
- Dataset pequeño: las métricas tienen alta varianza; se reportan con su desviación entre folds.
- La postura ante citas es heurística (señales léxicas); el dataset incluye la columna `postura_cita` para evaluarla y, a futuro, aprenderla.
- Sensacionalismo solo en titular y por léxico.
- Deadnaming no se detecta (ver `criterios.md`).
- La herramienta apoya el criterio humano; toda marca es revisable.
