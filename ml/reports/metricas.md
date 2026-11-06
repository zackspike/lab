# Métricas del modelo

Dataset: 201 oraciones de cuerpo (61 problemáticas). Validación cruzada estratificada 5 folds (predicciones fuera de fold).
P/R/F1: detección binaria (problemática o no), media ± desviación entre folds. Macro-F1: categoría entre revictimizacion, justificacion_agresor, discriminacion_estigmatizacion.

| Sistema | Precisión | Recall | F1 | Macro-F1 categoría |
|---|---|---|---|---|
| Solo reglas | 0.92 ± 0.07 | 0.56 ± 0.13 | 0.68 ± 0.10 | 0.69 |
| TF-IDF + LR (umbral 0.5) | 0.56 ± 0.21 | 0.34 ± 0.09 | 0.42 ± 0.13 | 0.28 |
| Embeddings + LR (umbral 0.5) | 0.53 ± 0.11 | 0.69 ± 0.20 | 0.60 ± 0.14 | 0.49 |
| Híbrido (emb + reglas + citas) (umbral 0.5) | 0.82 ± 0.11 | 0.76 ± 0.08 | 0.78 ± 0.05 | 0.73 |
| **Sistema final** (híbrido umbral 0.50 + alertas de reglas + citas) | 0.87 ± 0.08 | 0.82 ± 0.07 | 0.84 ± 0.03 | 0.76 |

Umbral elegido para precisión ≥ 0.8: **0.497**

## Matriz de confusión (sistema final)
| real \ predicho | ninguna | revictimizacion | justificacion_agresor | discriminacion_estigmatizacion |
|---|---|---|---|---|
| ninguna | 132 | 6 | 1 | 1 |
| revictimizacion | 6 | 18 | 0 | 1 |
| justificacion_agresor | 3 | 1 | 16 | 1 |
| discriminacion_estigmatizacion | 2 | 2 | 0 | 11 |

## Por fuente (predicciones fuera de fold, agrupadas)
La semilla sintética la escribió el equipo junto con las reglas: sus cifras son optimistas. Las notas reales son la medida que importa.

| Fuente | Oraciones | Positivos | Sistema | Precisión | Recall | F1 |
|---|---|---|---|---|---|---|
| dataset | 48 | 3 ⚠️ no concluyente | Solo reglas | 1.00 | 1.00 | 1.00 |
| dataset | 48 | 3 ⚠️ no concluyente | Híbrido (umbral 0.5) | 0.50 | 0.33 | 0.40 |
| dataset | 48 | 3 ⚠️ no concluyente | Sistema final | 0.75 | 1.00 | 0.86 |
| semilla_sintetica | 153 | 58 | Solo reglas | 0.91 | 0.53 | 0.67 |
| semilla_sintetica | 153 | 58 | Híbrido (umbral 0.5) | 0.82 | 0.78 | 0.80 |
| semilla_sintetica | 153 | 58 | Sistema final | 0.87 | 0.81 | 0.84 |

## Titulares (sensacionalismo)
| Fuente | Titulares | Sensacionalistas | Precisión | Recall | F1 |
|---|---|---|---|---|---|
| dataset | 4 | 4 | 1.00 | 1.00 | 1.00 |
| semilla_sintetica | 4 | 2 | 1.00 | 1.00 | 1.00 |

## Citas
| Fuente | Detección de cita (exactitud, todas las oraciones) | Postura correcta en oraciones problemáticas citadas |
|---|---|---|
| dataset | 0.85 (48) | 1.00 (1) |
| semilla_sintetica | 0.96 (153) | 1.00 (5) |

La postura solo se evalúa en oraciones problemáticas, donde cambia el resultado (criterio en `docs/criterios.md`).

## Falsos positivos (hasta 10, primero notas reales)
- [dataset] Según comentaron a Yucatán Ahora amigos en común de ambos, eran la típica pareja de clase media meridana a la que todos quieren ver llegar al altar, pero de un tiempo a la fecha todo eso cambió radicalmente y comenzaron a tener peleas cada vez más frecuentes, hasta que ella decidió dar por terminada la relación. _(real: ninguna, pred: justificacion_agresor)_
- [semilla_sintetica] Familiares la describieron como una joven alegre y dedicada a sus estudios. _(real: ninguna, pred: revictimizacion)_
- [semilla_sintetica] Vecinos escucharon gritos alrededor de las once de la noche. _(real: ninguna, pred: revictimizacion)_
- [semilla_sintetica] La joven salió de su trabajo y no volvió a casa. _(real: ninguna, pred: revictimizacion)_
- [semilla_sintetica] La mujer desapareció el viernes por la tarde. _(real: ninguna, pred: revictimizacion)_
- [semilla_sintetica] La mujer era migrante y trabajaba en el sector agrícola. _(real: ninguna, pred: discriminacion_estigmatizacion)_
- [semilla_sintetica] La joven había acudido a una reunión con amigas. _(real: ninguna, pred: revictimizacion)_
- [semilla_sintetica] La víctima conocía a su agresor, quien era su vecino. _(real: ninguna, pred: revictimizacion)_

## Falsos negativos (hasta 10, primero notas reales)
- [semilla_sintetica] La mujer aceptó subir al vehículo de un desconocido. _(real: revictimizacion, pred: ninguna)_
- [semilla_sintetica] La víctima conocía a su agresor y aun así decidió verlo. _(real: revictimizacion, pred: ninguna)_
- [semilla_sintetica] La mujer ya había sido detenida por faltas administrativas años atrás. _(real: revictimizacion, pred: ninguna)_
- [semilla_sintetica] La víctima provocó la discusión al revisar el teléfono de su pareja. _(real: revictimizacion, pred: ninguna)_
- [semilla_sintetica] El presunto responsable estaba bajo los efectos del alcohol, lo que explicaría su reacción. _(real: justificacion_agresor, pred: ninguna)_
- [semilla_sintetica] La mujer lo había humillado frente a sus amigos, por lo que él reaccionó con violencia. _(real: justificacion_agresor, pred: ninguna)_
- [semilla_sintetica] La discusión subió de tono y el hombre no pudo contenerse. _(real: justificacion_agresor, pred: ninguna)_
- [semilla_sintetica] La víctima, una migrante indocumentada, era de las que se exponen a esos riesgos. _(real: discriminacion_estigmatizacion, pred: ninguna)_
- [semilla_sintetica] La víctima, una empleada doméstica sin estudios, fue atacada en la casa donde trabajaba. _(real: discriminacion_estigmatizacion, pred: ninguna)_
- [semilla_sintetica] Según la madre del detenido, la joven lo provocaba constantemente. _(real: revictimizacion, pred: ninguna)_

> Con un dataset pequeño estas cifras son orientativas; se recalculan al añadir notas reales etiquetadas.
