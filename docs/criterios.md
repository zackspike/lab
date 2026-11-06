# Criterios: definición y categorías

> BORRADOR para el hackathon. Debe revisarlo el equipo (idealmente con apoyo de alguien con experiencia en perspectiva de género) y citar fuentes antes de la presentación. **Fuentes: PENDIENTE.**

## Revictimización (victimización secundaria)
Nuevo daño o refuerzo del daño sufrido por una persona sobreviviente de violencia, causado no por el agresor sino por el trato, el discurso o las prácticas que la rodean (medios, instituciones, entorno). En una nota periodística aparece cuando el texto:
- Atribuye total o parcial responsabilidad a la víctima.
- Expone innecesariamente su identidad, intimidad o historial.
- Cuestiona su credibilidad o conducta.
- Revive detalles gráficos sin función informativa.

## Categorías
El modelo clasifica oraciones del **cuerpo** de la nota en tres categorías. `sensacionalismo` se evalúa **solo en el titular**.

| Identificador | Categoría | Idea clave | Ejemplo orientativo |
|---|---|---|---|
| `revictimizacion` | Revictimización | Hace recaer daño, culpa o sospecha sobre la víctima concreta del caso | "Salía sola de madrugada y vestía provocativamente" |
| `justificacion_agresor` | Justificación del agresor / romantización | Minimiza, excusa o romantiza la violencia | "Crimen pasional", "lo hizo por celos", "era un hombre trabajador" |
| `discriminacion_estigmatizacion` | Discriminación / estigmatización | Desvaloriza o etiqueta por género, orientación, identidad u ocupación; estereotipos de grupo | "Como todo trans, estaba en ambientes peligrosos"; "La prostituta fue hallada…" |
| `sensacionalismo` | Sensacionalismo (solo titular) | Titular que explota el hecho con adjetivos o detalle gráfico | "Macabro hallazgo: brutal asesinato…" |
| `ninguna` | Ninguna | Información factual, sin atribución de culpa | "La víctima, de 24 años, fue hallada el lunes…" |

## Reglas de decisión
1. Mencionar el hecho violento o el feminicidio **no** es, por sí solo, un problema.
2. Evaluar **frase en contexto** (oración + la anterior), no palabras sueltas.
3. En duda, no marcar (precisión sobre cobertura).
4. Un fragmento tiene una sola categoría principal.
5. "Presunto/a" aplicado al **agresor** es correcto (presunción de inocencia). Aplicado a la **víctima** ("presunta víctima") cuestiona su credibilidad.

## Citas de terceros
Cuando la nota reproduce lo dicho por otra persona (entre comillas, "según X", "declaró que…"), se evalúa la **postura de la nota** respecto a la cita:

| Postura (`postura_cita`) | Cómo se reconoce | Qué se hace |
|---|---|---|
| `avala` | El narrador repite o adopta la afirmación fuera de la cita | Se marca normalmente |
| `sin_postura` | La nota reproduce la cita sin contrastar ni comentar | Se marca con confianza reducida: "la nota reproduce sin contrastar" |
| `desmiente` | La nota la contradice o contextualiza **en la misma oración o en la siguiente** ("sin embargo", "especialistas advierten", "la fiscalía descartó") | No se marca |
| `no_cita` | La oración no es una cita | — |

- Un contraste que llega más tarde no anula la reproducción: idealizar al agresor sigue siendo problemático aunque la nota lo matice párrafos después.
- Citar **datos** ("según datos recabados", "de acuerdo con los reportes") no es citar a una persona. Tampoco lo es la referencia del medio a sí mismo ("como informamos").

## Sensacionalismo en el titular
Todo lo que se marca en el titular sale como `sensacionalismo`; la justificación indica el motivo:
- **Léxico** dramatizante: "macabro", "brutal", "tragedia", "fatal desenlace", "pareja ideal", "difícil de creer"…
- **Reglas del cuerpo** aplicadas al titular: "investigan posible crimen pasional".
- **Ortografía disfrazada** de palabras violentas para evadir moderación: "As3sin4d4".
- **Emojis** de armas, sangre o impacto: 🔫 🔪 🩸 💀 😱.
- **Mayúsculas** en la mayor parte del titular.

## Patrones iniciales (para `ml/src/rules.py`)
- Culpa a la víctima: "por andar sola", "vestía provocativamente", "se lo buscó", "estaba en un lugar indebido".
- Credibilidad: "supuesta/presunta víctima", "según ella" sin contexto judicial.
- Romantización: "crimen pasional", "arrebato de celos", "por amor".
- Perfil exculpatorio del agresor: "hombre trabajador", "respetable", "buen padre".
- Exposición: nombre de la víctima junto a domicilio o historial íntimo sin relevancia informativa.
- Estereotipo de grupo: "como todo/toda…", ocupación usada como definición de la persona.

## Pendientes (fuera de alcance del MVP)
- **Deadnaming / mal-género a personas trans.** Requiere saber que la persona es trans y cuál es el nombre con el que se identifica; no se puede determinar de forma general a partir del texto. Queda documentado, no se detecta.
- Fuentes bibliográficas y normativas de estos criterios.

## Guía de etiquetado (para el dataset)
- Unidad: oración. Generar la plantilla con `python -m ml.src.prepare ml/data/raw/`.
- Columnas: `id, nota, idx, es_titulo, texto, categoria, fragmento, postura_cita, justificacion, etiquetador`.
  - `categoria`: uno de los identificadores de arriba (vacío = `ninguna`).
  - `fragmento`: copia exacta del trozo problemático (opcional; vacío = toda la oración).
  - `postura_cita`: `no_cita`, `avala`, `sin_postura` o `desmiente`. **Obligatoria solo en oraciones problemáticas** (es donde cambia el resultado); en las demás puede quedar vacía.
- Anonimizar antes de commitear: nombres de víctimas **y de agresores** → `[NOMBRE]`; lugares de trabajo → `[LUGAR]`; domicilios → `[DIRECCIÓN]`; placas → `[PLACAS]`. El nombre del archivo en `raw/` se usa como id de la nota: no debe contener nombres.
- Dos personas etiquetan una muestra común; se reporta la kappa de Cohen (`python -m ml.src.train --kappa a.csv b.csv`).
