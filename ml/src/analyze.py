"""Punto de entrada de la librería de análisis.

Versión MOCK: devuelve fragmentos detectados con reglas mínimas para poder
desarrollar backend y frontend en paralelo. Reemplazar por reglas + modelo reales.
"""
from __future__ import annotations
import re

REGLAS = [
    (r"vest[ií]a provocativamente|se lo busc[oó]|por andar sola",
     "revictimizacion",
     "Atribuye responsabilidad a la víctima por su conducta o apariencia.",
     "Este tipo de frase traslada la culpa de la violencia a la víctima y refuerza el daño.",
     "Omitir la referencia y centrar la nota en el hecho y en quien ejerció la violencia."),
    (r"crimen pasional|arrebato de celos",
     "justificacion_agresor",
     "Romantiza o minimiza la violencia presentándola como un acto de pasión.",
     "Presentar el feminicidio como 'pasional' atenúa la responsabilidad del agresor.",
     "Usar 'feminicidio' o 'violencia contra la mujer' según corresponda."),
]


def analizar(texto: str) -> list[dict]:
    fragmentos = []
    for patron, cat, just, ctx, alt in REGLAS:
        for m in re.finditer(patron, texto, flags=re.IGNORECASE):
            fragmentos.append({
                "id": f"f{len(fragmentos) + 1}",
                "texto": m.group(0),
                "inicio": m.start(),
                "fin": m.end(),
                "categoria": cat,
                "justificacion": just,
                "contexto": ctx,
                "alternativa": alt,
                "criterio": "docs/criterios.md",
                "confianza": 0.9,
                "origen": "regla",
            })
    fragmentos.sort(key=lambda f: f["inicio"])
    return fragmentos
