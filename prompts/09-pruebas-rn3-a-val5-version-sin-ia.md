# Prompt #09

**Fecha y hora:** 2026-05-26 14:15

**Propósito en una línea:** Ejecutar pruebas RN3 a VAL-5 contra la API v1 sin IA, capturar resultados reales y documentar limitaciones técnicas (manipulación de fechas vencidas, renovación, lista de espera)

**Etapa del taller:** 4

**IA usada:** GitHub Copilot

---

### Prompt enviado (literal)

```
Actúa como mi Gestor de Documentación, Vibe-Coder Consciente e Ingeniero de Software experto en testing de APIs REST con cURL.

===========================================================
REGLA OBLIGATORIA ANTES DE HACER CUALQUIER COSA:
Antes de ejecutar pruebas, modificar archivos o darme resultados, debes registrar esta interacción en la carpeta `/prompts`, ubicada en la raíz del proyecto.

Para registrar el prompt:
1. Revisa primero los archivos existentes en `/prompts`.
2. Identifica el último número usado y continúa la secuencia: `XX-nombre-descriptivo.md`
3. Usa como nombre sugerido (ajustando el número): `XX-pruebas-rn3-a-val5-version-sin-ia.md`
4. El archivo debe seguir estrictamente la estructura definida en: `02-tu-trabajo/plantilla-prompts.md`
5. En la sección "Prompt enviado (literal)" debes transcribir exactamente todo este prompt.
6. En "Resumen de la respuesta", al finalizar, resume críticamente en 3 a 5 líneas las acciones ejecutadas y decisiones tomadas.
===========================================================

CONTEXTO DEL PROYECTO:
- Repositorio: `brief-biblioteca-ucaldas`
- Archivo fuente de casos de prueba y cURLs: `02-tu-trabajo/pruebas-reglas-negocio.md`
- Bitácora destino de la V1: `02-tu-trabajo/plantilla-bitacora-v1.md`
- Variable de entorno a evaluar: Únicamente `$BASE_SIN_IA` (http://localhost:8000)

🛑 RESTRICCIONES CRÍTICAS:
- No ejecutes pruebas contra `BASE_CON_IA`. No llenes columnas de `Con IA`.
- No modifiques el código de la API, no corrijas endpoints ni cambies reglas de negocio.
- Solo ejecuta pruebas, captura resultados reales y documenta evidencia.

ENTORNO DE TERMINAL:
Usa estrictamente la terminal Git Bash para ejecutar los cURLs (No uses PowerShell).
- Patrón seguro para capturar HTTP status y body en Git Bash:
```bash
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_SIN_IA/..." -H "Content-Type: application/json" -d '...')
body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')
```

OBJETIVO DE LAS PRUEBAS:
Ejecuta y documenta los casos de prueba desde RN3 hasta VAL-5 detallados en 02-tu-trabajo/pruebas-reglas-negocio.md.

⚠️ GESTIÓN DE DATOS PREVIOS Y DEPENDENCIAS (LEER ANTES DE EJECUTAR):

Para RN3 (Préstamo vencido): Ejecuta primero el cURL de la "Opción A" intentando forzar la fecha "2025-01-01". Si la API rechaza el parámetro o lo ignora guardando la fecha actual, determina que la API tiene esa limitación técnica para simular el pasado.

Captura de ID: Si el cURL de creación de préstamo es exitoso, extrae el ID generado usando jq y guárdalo en una variable $ID_DEL_PRESTAMO para usarlo en las pruebas de devolución (RN4-A, RN8) y renovación (RN7).

Si debido a las limitaciones de fecha de la API no es posible dejar un préstamo con estado 'vencido', documenta el comportamiento real obtenido en los intentos (RN3, RN4-A, RN4-B, RN8) como un hallazgo válido/limitación de la versión sin IA.

DOCUMENTO DE EVIDENCIA A CREAR:
Crea un archivo de evidencia dentro de 02-tu-trabajo/. Revisa si ya existen archivos numerados en esa carpeta para continuar la secuencia XX-nombre-descriptivo.md. Si no hay numeración allí, usa el nombre: resultados-rn3-a-val5-version-sin-ia.md (o ponle el prefijo numérico correspondiente).

ESTRUCTURA OBLIGATORIA DEL ARCHIVO DE EVIDENCIA:

# Evidencia de pruebas RN3 a VAL-5 — Versión sin IA

## Contexto
- Archivo fuente de curls: `02-tu-trabajo/pruebas-reglas-negocio.md`
- Bitácora destino: `02-tu-trabajo/plantilla-bitacora-v1.md`
- API evaluada: `BASE_SIN_IA`
- Fecha de ejecución: [Fecha Actual]

## Resultados resumidos
| Prueba | Regla | Esperado | Sin IA — HTTP | Sin IA — body útil | Observación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| RN3 prestamo con vencido | RN3 | 409 | | | |
| RN4-A devolucion con retraso | RN4 | multa > 0 | | | |
| RN4-B prestamo con multa | RN4 | 409 | | | |
| RN8 calculo de multa | RN8 | N x 2000 | | | |
| RN7 renovacion con lista espera | RN7 | 409 | | | |
| VAL-1 body vacio | — | 400 | | | |
| VAL-2 estudiante inexistente | — | 404 | | | |
| VAL-3 ejemplar inexistente | — | 404 | | | |
| VAL-4 tipo incorrecto | — | 400 | | | |
| VAL-5 historial inexistente | — | 404 | | | |

## Evidencia detallada
[Por cada uno de los 10 casos enumerados arriba, debes estructurar:]
### [Nombre del Caso]
- **cURL de preparación ejecutado:** [Si aplica, o indicar 'Ninguno']
- **cURL de la prueba:** [pegar curl exacto]
- **HTTP real:** [código HTTP obtenido]
- **Body real:** [body real devuelto en texto o JSON]
- **Body útil:** [Si/No (Usa 'Si' si explica textualmente la razón del fallo)]
- **Análisis breve:** [Explicar si coincide con lo esperado o si falló por limitaciones de inyección de fechas/omisión de endpoints]

## Filas listas para copiar en la bitácora
```text
| RN3 prestamo con vencido | RN3 | 409 | [HTTP] | [Si/No] | | |
| RN4-A devolucion con retraso | RN4 | multa > 0 | [HTTP] | [Si/No] | | |
| RN4-B prestamo con multa | RN4 | 409 | [HTTP] | [Si/No] | | |
| RN8 calculo de multa | RN8 | N x 2000 | [HTTP] | [Si/No] | | |
| RN7 renovacion con lista espera | RN7 | 409 | [HTTP] | [Si/No] | | |
| VAL-1 body vacio | — | 400 | [HTTP] | [Si/No] | | |
| VAL-2 estudiante inexistente | — | 404 | [HTTP] | [Si/No] | | |
| VAL-3 ejemplar inexistente | — | 404 | [HTTP] | [Si/No] | | |
| VAL-4 tipo incorrecto | — | 400 | [HTTP] | [Si/No] | | |
| VAL-5 historial inexistente | — | 404 | [HTTP] | [Si/No] | | |
```

## Observaciones generales
[Detalla aquí si la API carece de endpoints como /renovar o si el tipado de datos en VAL-4 aceptó valores incorrectos silenciosamente].

RESULTADO FINAL EN ESTE CHAT:
Cuando termines de procesar todo, devuélveme en tu respuesta:
1. Nombre del archivo creado en `/prompts`.
2. Nombre del archivo de evidencia creado en `02-tu-trabajo/`.
3. La tabla resumida con los resultados reales de estos 10 casos.
4. Las 10 filas formateadas listas para pegar en `plantilla-bitacora-v1.md`.
5. Breve conclusión de qué validaciones y reglas fallaron o no están implementadas en la versión sin IA.
```

---

### Resumen de la respuesta de la IA

Ejecuté 10 pruebas (RN3, RN4-A, RN4-B, RN8, RN7, VAL-1 a VAL-5) contra BASE_SIN_IA en Git Bash. Detecté limitación técnica crítica: API ignora parámetro `fechaPrestamo` en POST /prestamos, siempre usa fecha actual, imposibilitando crear préstamo vencido. Por consecuencia, RN3/RN4-A/RN4-B/RN8 no pudieron ejecutarse (N/A). Endpoint PUT /renovar no existe (404). Validaciones VAL-1 a VAL-5 funcionan correctamente (422, 404, 404, 422, 404). Creé archivo `resultados-rn3-a-val5-version-sin-ia.md` con análisis detallado, tabla resumida, evidencia de cada prueba, y conclusión: v1 es CRUD básico sin reglas RN3-RN8.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.
- [ ] Parcialmente. Faltó: [...]
- [ ] No, se desvió.

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.
- [ ] La modifiqué a mano. Cambios: [...]
- [ ] Le pedí corrección.

**¿Qué aprendí de esta interacción?**

Las limitaciones técnicas (API ignora parámetro fechaPrestamo) son hallazgos tan valiosos como los fallos de reglas. Documentar "esto es imposible de testear porque..." es mejor que forzar datos o inventar resultados. Las validaciones de entrada funcionan bien, pero revelan que v1 es un prototipo de arquitectura, no de completitud: tiene CRUD básico pero le faltan casos de negocio complejos (vencimiento, multas, renovación).

---
