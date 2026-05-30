# Registro de Prompt — #10

## Prompt #10

**Fecha y hora:** 2026-05-26

**Proposito en una linea:** Consolidar `pruebas-reglas-negocio.md` como
documento maestro del taller integrando los resultados de Version_2 y la
tabla comparativa de la compañera, preservando todas las secciones V1 intactas.

**Etapa del taller:** Etapa 4 — Consolidacion final de resultados

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Asunto: Consolidacion Final de Resultados de Pruebas y Analisis Comparativo

Actua como Lider de Calidad (QA Lead). Tu objetivo es integrar todos los
hallazgos en un unico documento maestro.

Fuentes de Integracion:
1. pruebas-reglas-negocio.md — mantener todas las preguntas y secciones V1
2. reglas-negocio-v2.md — resultados completos de Version_2
3. Tabla de companera: [tabla con resultados Sin IA proporcionada por el usuario]

Instrucciones:
- Actualiza pruebas-reglas-negocio.md como documento maestro.
- Preservar Preguntas V1: NO eliminar ninguna pregunta de la seccion
  "Preguntas de reflexion para la bitacora". Completar las respuestas V2.
- Anexar la tabla de la companera completando las columnas "Con IA"
  con los resultados de reglas-negocio-v2.md.
- Sincronizar Hallazgos: añadir notas tecnicas relevantes (422 vs 400,
  snake_case, Opcion A para fechas, etc.) donde corresponda en el documento.
- Genera prompts/10-consolidacion-final-taller.md.

Confirma que el archivo final contiene:
Preguntas V1 + Resultados V2 + Tabla de companera
```

---

### Archivos analizados

- `02-tu-trabajo/pruebas-reglas-negocio.md` — documento maestro original con
  secciones V1, preguntas de reflexion y tabla comparativa vacia (473 lineas).
- `02-tu-trabajo/reglas-negocio-v2.md` — reporte QA Version_2 (870 lineas),
  con resultados de 21/21 verificaciones PASARON.
- Tabla proporcionada por la compañera — 13 filas con resultados Sin IA
  para RN1-B, RN2-B, RN5-B, RN6-A, RN6-B, RN3, RN4-B, RN7, VAL-1 a VAL-5.

---

### Resumen de la respuesta de la IA

**Accion realizada:** reescritura completa de `pruebas-reglas-negocio.md`
via bash heredoc (prevencion de null bytes aprendida en prompt #07).

**Estructura del documento maestro final (473 lineas, 20.015 bytes):**

- Seccion "Antes de empezar" (puertos) — intacta.
- Paso 0 / Paso 1 — intactos. Se agrego nota de snake_case para Version_2.
- RN1 a RN8 y RN7 — secciones de curl V1 intactas. Se añadio nota al pie
  de RN3 explicando la Opcion A de inyeccion de fecha en Version_2.
- "Pruebas de validacion VAL-1 a VAL-5" — intactas.
- **Tabla comparativa** — reemplazada por una tabla unificada de 14 filas
  con 6 columnas: Prueba | Regla | Esperado | Sin IA HTTP | Sin IA body util |
  Con IA HTTP | Con IA body util. Columnas Sin IA: datos de la companera.
  Columnas Con IA: datos de reglas-negocio-v2.md.
  Se añadio RN8 (que no estaba en la tabla de la companera) con datos V2.
- Nota al pie de tabla explicando diferencia 422 vs 400 y nomenclatura
  snake_case V2 vs camelCase V1.
- **Preguntas de reflexion** — todas las preguntas V1 preservadas intactas,
  respuestas V1 del estudiante preservadas. Se añadieron respuestas V2 en
  cada punto (Q1, Q2, Q3, Q4).

**Contenido de la tabla — columnas Con IA completadas:**

| Prueba | Con IA HTTP | Con IA body util |
|--------|-------------|------------------|
| RN1-B cuarto pregrado | 409 | Si — `limite` y `actuales` |
| RN2-B sexto posgrado | 409 | Si — `limite` y `actuales` |
| RN5-B ejemplar ya prestado | 409 | Si — identifica el ejemplar |
| RN6-A plazo libro normal | 201 | Si — campo `fecha_devolucion_esperada` |
| RN6-B plazo alta demanda | 201 | Si — campo `fecha_devolucion_esperada` |
| RN3 prestamo con vencido | 409 | Si — `prestamo_vencido_pendiente` |
| RN4-B prestamo con multa | 409 | Si — `multa_pendiente` + monto |
| RN7 renovacion lista espera | 409* | Si* — analisis estatico |
| RN8 calculo multa | 200 | Si — `dias_retraso` y `monto` |
| VAL-1 body vacio | 422 | Si — detalle Pydantic por campo |
| VAL-2 estudiante inexistente | 404 | Si — `estudiante_no_encontrado` |
| VAL-3 ejemplar inexistente | 404 | Si — `ejemplar_no_encontrado` |
| VAL-4 tipo incorrecto | 422 | Si — tipo invalido por campo |
| VAL-5 historial inexistente | 404 | Si — `estudiante_no_encontrado` |

*RN7: endpoint existe en Version_2 y logica implementada. No ejecutado
via curl por requerir setup previo de reserva activa.

**Hallazgos criticos integrados:**

1. **422 vs 400:** Version_2 retorna 422 (RFC 9110 / FastAPI/Pydantic) donde
   la guia esperaba 400. No es un bug. Los clientes deben manejar ambos.
2. **snake_case vs camelCase:** Version_2 usa `estudiante_id`/`ejemplar_id`/
   `alta_demanda`; la guia y Version_1 usan camelCase. Diferencia de estilo.
3. **Opcion A para fechas:** Version_2 acepta `fecha_prestamo` opcional en
   el body del prestamo, lo que permite probar RN3, RN4 y RN8 sin modificar
   el codigo.
4. **Estado vencido dinamico:** Version_2 calcula el vencimiento en tiempo
   de ejecucion, no lo persiste en BD. Prestamos vencidos aparecen como
   `"activo"` en BD pero el use case los detecta al comparar con `date.today()`.
5. **RN7 incompleta en ambas versiones:** V1 no tiene el endpoint; V2 tiene
   la logica pero requiere reserva previa para activar la restriccion.

**Verificacion del archivo final:**
- 0 null bytes confirmados.
- 10/10 checks de contenido: tabla, columnas V1/V2, 422, 409, RN7, RN8,
  VAL-5, snake_case, respuestas V2.

**Archivos creados/modificados:**

- `02-tu-trabajo/pruebas-reglas-negocio.md` — actualizado como documento
  maestro con V1 + V2 + tabla de companera integrada.
- `prompts/10-consolidacion-final-taller.md` — este archivo.

---

### Mi evaluacion

**La respuesta cumplio con lo que pedi?**

- [ ] Completamente.
- [ ] Parcialmente. Falto: [...]
- [ ] No, se desvio. Hizo: [...]

**La acepte tal cual o la modifique?**

- [ ] Tal cual.
- [ ] La modifique a mano. Cambios: [...]
- [ ] Le pedi correccion con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechace completamente. Razon: [...]

**Que aprendi de esta interaccion?**

[Una linea sobre que te llevaste de este prompt — por ejemplo: "La tabla
de la companera expuso que Version_1 ni siquiera llega al codigo de negocio
en RN1/RN2 — Pydantic rechaza la entrada antes por el nombre del campo."]
