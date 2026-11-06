"""Justification templates (Spanish, user-facing). No free-form generated text."""
from __future__ import annotations

CRITERIA = "docs/criterios.md"

# key -> (justificacion, contexto, alternativa, criterio anchor)
TEMPLATES: dict[str, tuple[str, str, str, str]] = {
    # rule families
    "culpa_victima": (
        "Atribuye responsabilidad a la víctima por su conducta, apariencia o decisiones.",
        "Trasladar la culpa a la víctima refuerza el daño y desplaza la responsabilidad de quien ejerció la violencia.",
        "Omitir juicios sobre la conducta o apariencia de la víctima; centrar la nota en los hechos y en el agresor.",
        "#revictimización-victimización-secundaria"),
    "credibilidad": (
        "Pone en duda la credibilidad de la víctima sin un contexto judicial que lo justifique.",
        "Cuestionar el testimonio de la víctima desalienta la denuncia y reproduce la sospecha sobre ella.",
        "Usar 'víctima' o 'denunciante'; reservar 'presunto/a' para la persona señalada como agresora.",
        "#reglas-de-decisión"),
    "exposicion": (
        "Expone datos que permiten identificar o localizar a la víctima sin relevancia informativa.",
        "Publicar domicilio o datos de identificación aumenta el riesgo y la exposición pública de la víctima.",
        "Omitir domicilio y datos identificables; referir solo municipio o zona general si es necesario.",
        "#revictimización-victimización-secundaria"),
    "romantizacion": (
        "Romantiza o minimiza la violencia presentándola como producto de la pasión, el amor o los celos.",
        "Encuadrar un feminicidio como 'pasional' atenúa la responsabilidad del agresor y normaliza la violencia.",
        "Nombrar el hecho como feminicidio o violencia de género, según corresponda.",
        "#categorías"),
    "perfil_exculpatorio": (
        "Destaca cualidades positivas del agresor que funcionan como atenuante de la violencia.",
        "Resaltar que el agresor era 'trabajador' o 'buen padre' sugiere que la violencia es excepcional o comprensible.",
        "Informar antecedentes relevantes del agresor sin valoraciones que lo exculpen.",
        "#categorías"),
    "estereotipo": (
        "Usa una etiqueta o estereotipo que desvaloriza a la persona por su género, orientación, identidad u ocupación.",
        "Definir a la persona por una etiqueta estigmatizante reduce su humanidad y refuerza prejuicios sobre el grupo.",
        "Nombrar a la persona por su nombre o como 'mujer', 'persona'; mencionar ocupación o identidad solo si es relevante y con términos respetuosos.",
        "#categorías"),
    # model-only detections (whole sentence)
    "revictimizacion": (
        "La oración hace recaer culpa, sospecha o exposición sobre la víctima.",
        "Este encuadre traslada la responsabilidad a la víctima y refuerza el daño sufrido.",
        "Reescribir la oración centrándola en los hechos y en la responsabilidad de quien agredió.",
        "#revictimización-victimización-secundaria"),
    "justificacion_agresor": (
        "La oración minimiza, excusa o romantiza la violencia del agresor.",
        "Las explicaciones que justifican al agresor normalizan la violencia de género.",
        "Describir la violencia sin atenuantes ni motivaciones que la hagan comprensible.",
        "#categorías"),
    "discriminacion_estigmatizacion": (
        "La oración desvaloriza o estigmatiza por género, orientación, identidad u ocupación.",
        "Los estereotipos sobre grupos refuerzan la discriminación y la violencia contra ellos.",
        "Eliminar la generalización o etiqueta; usar lenguaje respetuoso y preciso.",
        "#categorías"),
    "sensacionalismo": (
        "El titular usa adjetivos o detalles que explotan el hecho violento.",
        "El sensacionalismo convierte la violencia en espectáculo y vulnera la dignidad de la víctima.",
        "Titular con los hechos de forma sobria: qué ocurrió, dónde y el estado de la investigación.",
        "#categorías"),
}

QUOTE_NOTE = " La nota reproduce la cita sin contrastarla."


def render(key: str, stance: str = "no_cita") -> dict:
    just, ctx, alt, anchor = TEMPLATES[key]
    if stance == "sin_postura":
        just += QUOTE_NOTE
    return {"justificacion": just, "contexto": ctx, "alternativa": alt, "criterio": CRITERIA + anchor}
