# Métricas del modelo

Dataset: 153 oraciones de cuerpo (58 problemáticas). Validación cruzada estratificada 5 folds (predicciones fuera de fold).
P/R/F1: detección binaria (problemática o no), media ± desviación entre folds. Macro-F1: categoría entre revictimizacion, justificacion_agresor, discriminacion_estigmatizacion.

| Sistema | Precisión | Recall | F1 | Macro-F1 categoría |
|---|---|---|---|---|
| Solo reglas | 0.90 ± 0.10 | 0.53 ± 0.19 | 0.66 ± 0.17 | 0.68 |
| TF-IDF + LR (umbral 0.5) | 0.70 ± 0.14 | 0.57 ± 0.09 | 0.62 ± 0.08 | 0.47 |
| Embeddings + LR (umbral 0.5) | 0.72 ± 0.12 | 0.72 ± 0.07 | 0.71 ± 0.05 | 0.65 |
| Híbrido (emb + reglas + citas) (umbral 0.5) | 0.79 ± 0.11 | 0.72 ± 0.12 | 0.75 ± 0.11 | 0.68 |
| **Sistema final** (híbrido umbral 0.49 + alertas de reglas + citas) | 0.83 ± 0.10 | 0.81 ± 0.08 | 0.82 ± 0.09 | 0.73 |

Umbral elegido para precisión ≥ 0.8: **0.485**

## Matriz de confusión (sistema final)
| real \ predicho | ninguna | revictimizacion | justificacion_agresor | discriminacion_estigmatizacion |
|---|---|---|---|---|
| ninguna | 85 | 9 | 0 | 1 |
| revictimizacion | 7 | 17 | 0 | 1 |
| justificacion_agresor | 2 | 1 | 14 | 1 |
| discriminacion_estigmatizacion | 2 | 2 | 1 | 10 |

## Postura ante citas (heurística vs etiqueta)
Exactitud en 11 citas etiquetadas: **1.00**

## Falsos positivos (hasta 10)
- La mujer tenía 31 años. _(real: ninguna, pred: revictimizacion)_
- Familiares la describieron como una joven alegre y dedicada a sus estudios. _(real: ninguna, pred: revictimizacion)_
- Vecinos escucharon gritos alrededor de las once de la noche. _(real: ninguna, pred: revictimizacion)_
- La joven salió de su trabajo y no volvió a casa. _(real: ninguna, pred: revictimizacion)_
- La pareja tenía dos hijos, que quedaron bajo el cuidado de sus abuelos. _(real: ninguna, pred: revictimizacion)_
- La mujer desapareció el viernes por la tarde. _(real: ninguna, pred: revictimizacion)_
- El ataque ocurrió dentro del domicilio que compartían. _(real: ninguna, pred: revictimizacion)_
- La mujer era migrante y trabajaba en el sector agrícola. _(real: ninguna, pred: discriminacion_estigmatizacion)_
- La joven había acudido a una reunión con amigas. _(real: ninguna, pred: revictimizacion)_
- La víctima conocía a su agresor, quien era su vecino. _(real: ninguna, pred: revictimizacion)_

## Falsos negativos (hasta 10)
- La mujer aceptó subir al vehículo de un desconocido. _(real: revictimizacion, pred: ninguna)_
- La víctima regresaba de una fiesta en estado de ebriedad cuando fue atacada. _(real: revictimizacion, pred: ninguna)_
- La víctima conocía a su agresor y aun así decidió verlo. _(real: revictimizacion, pred: ninguna)_
- La mujer ya había sido detenida por faltas administrativas años atrás. _(real: revictimizacion, pred: ninguna)_
- La víctima provocó la discusión al revisar el teléfono de su pareja. _(real: revictimizacion, pred: ninguna)_
- El presunto responsable estaba bajo los efectos del alcohol, lo que explicaría su reacción. _(real: justificacion_agresor, pred: ninguna)_
- La mujer lo había humillado frente a sus amigos, por lo que él reaccionó con violencia. _(real: justificacion_agresor, pred: ninguna)_
- La víctima, una migrante indocumentada, era de las que se exponen a esos riesgos. _(real: discriminacion_estigmatizacion, pred: ninguna)_
- La víctima, una empleada doméstica sin estudios, fue atacada en la casa donde trabajaba. _(real: discriminacion_estigmatizacion, pred: ninguna)_
- Según la madre del detenido, la joven lo provocaba constantemente. _(real: revictimizacion, pred: ninguna)_

> Con un dataset pequeño y sintético estas cifras son orientativas; se recalculan al añadir notas reales etiquetadas.
