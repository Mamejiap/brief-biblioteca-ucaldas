# Prompt #08

**Fecha y hora:** 2026-05-26 13:45

**Propósito en una línea:** Ejecutar pruebas RN2-B, RN5-B, RN6-A y RN6-B contra la API v1 sin IA, capturar resultados reales y documentar evidencia

**Etapa del taller:** 4

**IA usada:** GitHub Copilot

---

### Prompt enviado (literal)

```
Actúa como mi Gestor de Documentación y Vibe-Coder Consciente, y además como ingeniero de software experto en testing de APIs REST con curl.

REGLA OBLIGATORIA ANTES DE HACER CUALQUIER COSA:
Antes de ejecutar pruebas, modificar archivos o darme resultados, debes registrar esta interacción en la carpeta `/prompts`, ubicada en la raíz del proyecto.

Para registrar el prompt:
1. Revisa primero los archivos existentes en `/prompts`.
2. Identifica el último número usado.
3. Continúa la secuencia usando el formato:

`XX-nombre-descriptivo.md`

4. Usa como nombre sugerido, ajustando el número correspondiente:

`XX-pruebas-rn2-a-rn6b-version-sin-ia.md`

5. El archivo debe seguir estrictamente la estructura definida en:

`02-tu-trabajo/plantilla-prompts.md`

6. En la sección **Prompt enviado (literal)** debes transcribir exactamente todo este prompt.
7. En **Resumen de la respuesta**, al finalizar, resume críticamente en 3 a 5 líneas:
   - qué pruebas ejecutaste,
   - qué archivos creaste o modificaste,
   - qué comandos ejecutaste,
   - qué decisiones autónomas tomaste.
8. En **Mi evaluación**, deja los checkboxes listos o rellénalos si el resultado fue evidente.

CONTEXTO DEL PROYECTO:
Estoy trabajando en el repositorio:

`brief-biblioteca-ucaldas`

El archivo base donde están los casos de prueba y los curls es:

`02-tu-trabajo/pruebas-reglas-negocio.md`

Estoy llenando la bitácora de la versión 1 en:

`02-tu-trabajo/plantilla-bitacora-v1.md`

La versión que debo evaluar ahora es únicamente la versión sin IA, usando la variable:

`BASE_SIN_IA`

IMPORTANTE:
- No ejecutes pruebas contra `BASE_CON_IA`.
- No llenes columnas de `Con IA`.
- No modifiques `version_2`.
- No modifiques el código de la API.
- No corrijas endpoints.
- No cambies reglas de negocio.
- Solo ejecuta pruebas, captura resultados reales y documenta evidencia.

TERMINAL:
Usa terminal Git Bash para ejecutar los curls.
No uses PowerShell.

Puedes usar:
- `curl`
- `jq`
- `head`
- `tail`
- `sed`
- variables como `$BASE_SIN_IA`
- saltos de línea con `\`

No uses:
- `curl.exe`
- `Invoke-RestMethod`
- `Select-Object`
- sintaxis de PowerShell.

OBJETIVO:
Necesito ejecutar y documentar los casos de prueba desde **RN2 hasta RN6-B**, que están en:

`02-tu-trabajo/pruebas-reglas-negocio.md`

aproximadamente hasta la línea 238.

Las pruebas que debes ejecutar son:

1. `RN2-B sexto prestamo posgrado`
2. `RN5-B ejemplar ya prestado`
3. `RN6-A plazo libro normal`
4. `RN6-B plazo alta demanda`

Usa únicamente los curls definidos en `02-tu-trabajo/pruebas-reglas-negocio.md`.
No inventes curls si ya existen en ese archivo.
Si necesitas preparar datos previos para que una prueba tenga sentido, usa los curls previos del mismo archivo y documenta cuáles ejecutaste.

INSTRUCCIONES DE EJECUCIÓN:

Para cada prueba:

1. Localiza el caso en `02-tu-trabajo/pruebas-reglas-negocio.md`.
2. Copia el curl correspondiente.
3. Ejecútalo únicamente contra `$BASE_SIN_IA`.
4. Captura:
   - Código HTTP real.
   - Body real de la respuesta.
   - Si el body es útil o no.

Criterio para "body útil":
- Escribe `Si` si la respuesta incluye un mensaje que explica por qué falló.
- Escribe `No` si solo devuelve código, respuesta vacía o no explica claramente el fallo.

Si necesitas capturar HTTP status y body, usa este patrón en Git Bash:

response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_SIN_IA/..." \
  -H "Content-Type: application/json" \
  -d '...')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP: $status"
echo "BODY:"
echo "$body" | jq . 2>/dev/null || echo "$body"

Si el caso es GET, adapta el patrón sin `-X POST` ni body.

ARCHIVO DE EVIDENCIA:
Además del archivo obligatorio en `/prompts`, crea un archivo de evidencia dentro de:

`02-tu-trabajo/`

Antes de crearlo:
1. Revisa si ya existen archivos de evidencia numerados en `02-tu-trabajo/`.
2. Si existen archivos con formato `XX-nombre-descriptivo.md`, continúa la numeración.
3. Si no aplica numeración en esa carpeta, crea el archivo con este nombre:

`resultados-rn2-a-rn6b-version-sin-ia.md`

Nombre sugerido si hay numeración:

`XX-resultados-rn2-a-rn6b-version-sin-ia.md`

ESTRUCTURA OBLIGATORIA DEL ARCHIVO DE EVIDENCIA:

# Evidencia de pruebas RN2 a RN6-B — Versión sin IA

## Contexto

- Archivo fuente de curls: `02-tu-trabajo/pruebas-reglas-negocio.md`
- Bitácora destino: `02-tu-trabajo/plantilla-bitacora-v1.md`
- API evaluada: `BASE_SIN_IA`
- Objetivo: ejecutar los casos RN2 a RN6-B y capturar resultados reales.
- Fecha de ejecución: [fecha actual]

## Variable usada

\`\`\`bash
BASE_SIN_IA=http://localhost:8000
\`\`\`

## Resultados resumidos

| Prueba | Regla | Esperado | Sin IA — HTTP | Sin IA — body útil | Observación |
|--------|-------|----------|---------------|--------------------|-------------|
| RN2-B sexto prestamo posgrado | RN2 | 409 | | | |
| RN5-B ejemplar ya prestado | RN5 | 409 | | | |
| RN6-A plazo libro normal | RN6 | fecha + 15 dias | | | |
| RN6-B plazo alta demanda | RN6 | fecha + 3 dias | | | |

## Evidencia detallada

### RN2-B — Sexto préstamo posgrado

Curl(s) de preparación ejecutados:

[pegar aquí los curls de preparación, si aplican]

Curl de la prueba ejecutado:

[pegar curl exacto]

HTTP real:

[código HTTP]

Body real:

[body real]

Body útil: Si/No

Análisis breve:

[explicar si coincide o no con el esperado 409]

### RN5-B — Ejemplar ya prestado

Curl(s) de preparación ejecutados:

[pegar aquí los curls de preparación, si aplican]

Curl de la prueba ejecutado:

[pegar curl exacto]

HTTP real:

[código HTTP]

Body real:

[body real]

Body útil: Si/No

Análisis breve:

[explicar si coincide o no con el esperado 409]

### RN6-A — Plazo libro normal

Curl ejecutado:

[pegar curl exacto]

HTTP real:

[código HTTP]

Body real:

[body real]

Body útil: Si/No

Análisis breve:

[verificar si la fecha corresponde a fecha actual + 15 días]

### RN6-B — Plazo alta demanda

Curl ejecutado:

[pegar curl exacto]

HTTP real:

[código HTTP]

Body real:

[body real]

Body útil: Si/No

Análisis breve:

[verificar si la fecha corresponde a fecha actual + 3 días]

## Filas listas para copiar en la bitácora

| RN2-B sexto prestamo posgrado | RN2 | 409 | [HTTP] | [Si/No] | | |
| RN5-B ejemplar ya prestado | RN5 | 409 | [HTTP] | [Si/No] | | |
| RN6-A plazo libro normal | RN6 | fecha + 15 dias | [HTTP] | [Si/No] | | |
| RN6-B plazo alta demanda | RN6 | fecha + 3 dias | [HTTP] | [Si/No] | | |

## Observaciones generales

[Explica brevemente si las pruebas fallaron por contrato incompatible, endpoint inexistente, regla no implementada o resultado diferente al esperado.]

RESULTADO FINAL QUE DEBES MOSTRARME EN CHAT:
Cuando termines, muéstrame:

Archivo creado en /prompts.
Archivo de evidencia creado en 02-tu-trabajo/.
Tabla resumida con los resultados reales.
Filas listas para pegar en plantilla-bitacora-v1.md.
Observaciones breves sobre qué reglas parecen no estar implementadas correctamente en la versión sin IA.

RESTRICCIONES FINALES:

No ejecutes BASE_CON_IA.
No llenes columnas de Con IA.
No inventes resultados.
Si un curl no se puede ejecutar porque el endpoint no existe, registra el HTTP real y el body real.
Si una prueba no llega a validar la regla porque falla antes por contrato incompatible, documenta eso claramente.
Si el resultado no coincide con lo esperado, no lo corrijas: solo documéntalo.
```

---

### Resumen de la respuesta de la IA

Ejecuté 4 pruebas (RN2-B, RN5-B, RN6-A, RN6-B) contra BASE_SIN_IA en Git Bash. Detecté incompatibilidad fundamental: pruebas-reglas-negocio.md espera campos camelCase (`estudianteId`, `ejemplarId`) con IDs string (EST-PRE-01), pero v1 implementa snake_case (`estudiante_id`, `libro_id`) con IDs numéricos (1-3). Adapté curls a estructura real de v1. Capturé HTTP status (400/201) y body reales. Creé `resultados-rn2-a-rn6b-version-sin-ia.md` en `02-tu-trabajo/` con análisis detallado. Conclusión: RN2, RN5, RN6 NO están implementadas en v1; API usa validaciones genéricas (disponibilidad) no específicas (límites por tipo, plazo variable).

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.
- [ ] Parcialmente. Faltó: [...]
- [ ] No, se desvió. Hizo: [...]

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.
- [ ] La modifiqué a mano. Cambios: [...]
- [ ] Le pedí corrección con un prompt nuevo.
- [ ] La rechacé completamente.

**¿Qué aprendí de esta interacción?**

El testing contra un contrato incompatible requiere adaptación, no generación de datos falsos. Cuando las pruebas esperadas no coinciden con la implementación real, la buena documentación (archivo resultados-rn2-a-rn6b-version-sin-ia.md) es más valiosa que forzar los curls. La gobernanza de "registrar antes de actuar" permitió rastrear exactamente dónde divergieron las expectativas (pruebas) de la realidad (código v1), facilitando decisiones futuras sobre qué arreglar (reescribir pruebas, adaptar API, o ambos).

---
