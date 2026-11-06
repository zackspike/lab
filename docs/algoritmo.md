# Algoritmo de análisis

Herramienta de apoyo al análisis crítico del discurso periodístico con perspectiva de género. **El modelo de aprendizaje automático es el detector principal**; las reglas lingüísticas lo complementan como features, localizadores de fragmento y alertas de alta precisión. Criterios en [`criterios.md`](criterios.md).

## Pipeline
```
texto/PDF → normalizar + segmentar (offsets) ─┬→ titular → sensacionalismo (léxico, reglas, ortografía disfrazada, emojis, mayúsculas)
                                              └→ cada oración del cuerpo:
                              reglas (hits + spans)  ┐
                              citas (¿cita? postura) ├→ features → modelo 2 etapas → fusión → plantillas → fragmentos
                              embeddings MiniLM      ┘
```

1. **Ingesta y normalización** (`ml/src/text.py`). PDF → texto con `pypdf`; Unicode NFC, unión de palabras cortadas por guion, espacios colapsados. Todos los offsets se calculan sobre este texto normalizado, que es el que devuelve la API.
2. **Segmentación**. spaCy `es_core_news_md` → oraciones con `inicio/fin`, lemas, dependencias y entidades. La primera línea es el titular.
3. **Reglas** (`ml/src/rules.py`). Patrones por lema (spaCy `Matcher`) agrupados en familias. Guardas de contexto: negación cercana ("no fue un crimen pasional") y análisis de dependencias ("presunta víctima" ≠ "presunto agresor").
4. **Citas** (`ml/src/quotes.py`). Detecta discurso referido (comillas, "según", "de acuerdo con", verbos de reporte conjugados; excluye fuentes de datos y "como informamos") y estima la postura de la nota (avala / sin postura / desmiente) con señales en la oración y la siguiente.
5. **Titular** (`ml/src/headline.py`). Cinco señales (léxico, reglas del cuerpo, ortografía disfrazada, emojis violentos, mayúsculas); las que se solapan se fusionan en un fragmento con todos sus motivos. Categoría siempre `sensacionalismo`.
6. **Modelo** (`ml/src/model.py`).
   - Representación: embedding multilingüe `paraphrase-multilingual-MiniLM-L12-v2` de *oración previa + oración* (contexto), concatenado con flags de reglas y features de cita.
   - Etapa 1: regresión logística binaria (problemática / no), `class_weight="balanced"`; umbral elegido por validación cruzada para precisión ≥ 0.8.
   - Etapa 2: regresión logística de 3 clases, entrenada solo con positivos.
   - Explicabilidad: se adjuntan los ejemplos etiquetados más parecidos (similitud coseno).
7. **Fusión** (`ml/src/analyze.py`). Modelo y regla coinciden → `origen="regla+modelo"`, se resalta el fragmento de la regla. Solo modelo sobre el umbral → se resalta la oración. Solo regla → alerta de alta precisión (`origen="regla"`). Citas: `desmiente` anula, `sin_postura` reduce la confianza.
8. **Justificación** (`ml/src/templates.py`). Plantillas por categoría/familia que citan `criterios.md` y proponen una alternativa periodística. Sin texto generado libremente.

## Evaluación
`python -m ml.src.train` compara con validación cruzada estratificada (5 folds):

| Sistema | Descripción |
|---|---|
| Reglas | Solo patrones |
| TF-IDF + LR | n-gramas de caracteres 3–5 |
| Embeddings + LR | MiniLM |
| Híbrido | MiniLM + features de reglas y citas (sistema final) |

Reporta en `ml/reports/metricas.md`:
- precisión, recall y F1 (binario y por categoría) y matriz de confusión;
- las mismas métricas **por fuente** (semilla sintética frente a notas reales), porque la semilla se escribió junto con las reglas y es optimista;
- titulares: P/R del detector de sensacionalismo;
- citas: exactitud de la detección y de la postura en oraciones problemáticas;
- falsos positivos y negativos, primero los de notas reales.

## Límites conocidos
- Dataset pequeño: las métricas tienen alta varianza; se reportan con su desviación entre folds. Las notas reales aún son pocas.
- La postura ante citas es heurística (señales léxicas); el dataset incluye la columna `postura_cita` para evaluarla y, a futuro, aprenderla.
- Sensacionalismo solo en titular y por señales cerradas (sin modelo).
- Deadnaming no se detecta (ver `criterios.md`).
- La herramienta apoya el criterio humano; toda marca es revisable.
