# Contrato de la API

## POST /api/analizar
Entrada: `multipart` con `archivo` (PDF/TXT) **o** JSON `{ "texto": "..." }`.

Salida:
```json
{
  "texto": "texto completo normalizado",
  "fragmentos": [
    {
      "id": "f1",
      "texto": "vestía provocativamente",
      "inicio": 120,
      "fin": 143,
      "categoria": "revictimizacion",
      "justificacion": "Atribuye responsabilidad a la víctima por su vestimenta.",
      "contexto": "Este tipo de frase traslada la culpa de la violencia a la víctima y refuerza el daño.",
      "alternativa": "Omitir la referencia a la vestimenta; centrar la nota en el hecho y el agresor.",
      "criterio": "docs/criterios.md#revictimización",
      "confianza": 0.87,
      "origen": "regla"
    }
  ]
}
```
- `inicio`/`fin`: offsets de caracteres sobre `texto` (fin exclusivo).
- `origen`: `regla` | `modelo` | `regla+modelo`.
- `categoria`: `revictimizacion | justificacion_agresor | discriminacion_estigmatizacion | sensacionalismo` (`sensacionalismo` solo en el titular).
- `postura_cita` (opcional): `avala | sin_postura | desmiente` cuando el fragmento está dentro de una cita.
- `similares` (opcional): lista de oraciones etiquetadas parecidas, cuando `origen` incluye `modelo`.

## GET /api/health
`{"status": "ok"}`
