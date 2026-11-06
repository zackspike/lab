# Criterios: definición y categorías

> BORRADOR para el hackathon. Debe revisarlo el equipo (idealmente con apoyo de alguien con experiencia en perspectiva de género) y citar fuentes antes de la presentación.

## Revictimización (victimización secundaria)
Nuevo daño o refuerzo del daño sufrido por una persona sobreviviente de violencia, causado no por el agresor sino por el trato, el discurso o las prácticas que la rodean (medios, instituciones, entorno). En una nota periodística aparece cuando el texto:
- Atribuye total o parcial responsabilidad a la víctima.
- Expone innecesariamente su identidad, intimidad o historial.
- Cuestiona su credibilidad o conducta.
- Revive detalles gráficos sin función informativa.

## Cómo distinguirla de otras categorías
| Categoría | Idea clave | Ejemplo orientativo |
|---|---|---|
| **Revictimización** | Hace recaer daño o culpa sobre la víctima concreta del caso | "Salía sola de madrugada y vestía provocativamente" |
| **Discriminación** | Trato o lenguaje que desvaloriza por género/orientación/identidad, sin necesidad de ser sobre una víctima concreta | "Como todo trans, estaba involucrado en ambientes peligrosos" |
| **Estigmatización** | Etiqueta o estereotipo negativo sobre un grupo o persona | "La prostituta fue hallada..." usado como definición |
| **Justificación del agresor / romantización** | Minimiza o excusa la violencia | "Crimen pasional", "lo hizo por celos" |
| **Detalle morboso / sensacionalismo** | Descripción gráfica o titulares que explotan el hecho | Descripción gráfica sin valor informativo |
| **Ninguna** | Información factual, sin atribución de culpa | "La víctima, de 24 años, fue hallada el lunes..." |

> Las categorías son un punto de partida; el equipo puede fusionarlas o ajustarlas. Identificador técnico en `snake_case`: `revictimizacion`, `discriminacion`, `estigmatizacion`, `justificacion_agresor`, `sensacionalismo`, `ninguna`.

## Reglas de decisión
1. Mencionar el hecho violento o el feminicidio **no** es, por sí solo, un problema.
2. Evaluar **frase en contexto**, no palabras sueltas.
3. En duda, no marcar (precisión sobre cobertura).
4. Un fragmento puede tener una sola categoría principal; anotar una secundaria si aplica.

## Patrones iniciales (para `ml/src/reglas.py`)
- Culpa a la víctima: "por andar sola", "vestía provocativamente", "se lo buscó", "estaba en un lugar indebido".
- Justificación: "crimen pasional", "arrebato de celos", "hombre trabajador y respetable".
- Cuestionamiento de credibilidad: "supuesta víctima", "según ella", sin contexto judicial.
- Exposición: nombre completo, domicilio o historial íntimo sin relevancia informativa.
- Deadnaming / mal-género a personas trans.

## Guía de etiquetado (para el dataset)
- Unidad: oración. Una fila = una oración con su categoría y, si aplica, el fragmento exacto.
- Formato CSV en `ml/data/labeled/`: `id, texto, categoria, fragmento, justificacion`.
- Dos personas deben etiquetar una muestra común y comparar desacuerdos.
