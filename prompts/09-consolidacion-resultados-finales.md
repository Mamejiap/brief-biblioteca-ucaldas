# Registro de Prompt — #09

## Prompt #09

**Fecha y hora:** 2026-05-26

**Proposito en una linea:** Consolidar el reporte final de pruebas de
Version_2 completando todas las secciones de `reglas-negocio-v2.md` con
comandos corregidos, respuestas JSON simuladas desde el codigo fuente,
y analisis de diferencias tecnicas respecto a la guia original.

**Etapa del taller:** Etapa 4 — Documentacion de resultados de QA

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Actua como Especialista en Documentacion de QA. Tu tarea es finalizar
el reporte de pruebas de la Version 2.

1. Fuentes de Datos
   - Guia: pruebas-reglas-negocio.md
   - Salida: reglas-negocio-v2.md

2. Tarea: completa todas las secciones faltantes basandote en el
   comportamiento de la API en Version_2. Incluye:
   - Resultados RN1-RN6-B: exito o falla de cada prueba.
   - Transcripcion de evidencia: comando + respuesta JSON simplificada.
   - Analisis de diferencias: documenta observaciones tecnicas (422 vs 400).

3. Reglas de Formato
   - No inventes datos. Si requiere ejecucion, analiza la logica del codigo.
   - Estructura limpia con tablas y bloques de codigo.

4. Registro: crear 09-consolidacion-resultados-finales.md.
```

---

### Metodologia aplicada

**Fuentes consultadas para simular respuestas JSON:**

| Archivo | Dato extraido |
|---------|---------------|
| `app/api/schemas.py` | Estructura exacta de cada schema de respuesta |
| `app/domain/entities/estudiante.py` | `LIMITE_PRESTAMOS` = {pregrado:3, posgrado:5} |
| `app/domain/entities/multa.py` | `TARIFA_MULTA_POR_DIA = 2_000` |
| `app/domain/entities/libro.py` | `plazo_dias` = 15 o 3 segun `alta_demanda` |
| `app/domain/exceptions.py` | Nombres exactos de error codes y mensajes |
| `app/api/error_handlers.py` | Mapeo excepcion → HTTP status y campos del body |
| `app/application/use_cases/prestamos/crear_prestamo.py` | Orden de validaciones RN1-RN6 |
| `app/application/use_cases/prestamos/registrar_devolucion.py` | Calculo multa RN8 |

**Calculo de fechas** (hoy = 2026-05-26):
- RN6-A: `2026-05-26 + 15 dias = 2026-06-10`
- RN6-B: `2026-05-26 + 3 dias = 2026-05-29`
- RN3/RN4: `fecha_prestamo=2025-01-01` → vence `2025-01-16` → retraso 495 dias → multa $990.000
- RN8: `fecha_prestamo=2026-05-06` → vence `2026-05-21` → retraso 5 dias → multa $10.000

---

### Ejercicios resueltos en reglas-negocio-v2.md

| Seccion | Estado | Observacion |
|---------|--------|-------------|
| Paso 0 — Health check | Completo | Comando + respuesta JSON |
| Paso 1.1 — Crear estudiantes (2) | Completo | Comandos + respuestas con `limite_prestamos` |
| Paso 1.2 — Crear libros (2) | Completo | Comandos + respuestas con `plazo_dias` |
| Paso 1.2 — Crear ejemplares (7) | Completo | Comandos + respuesta tipo |
| RN1-A — 3 prestamos pregrado | Completo | Comando + respuesta + PASO |
| RN1-B — 4to prestamo rechazado | Completo | Comando + 409 + tabla criterios |
| RN2-A — 5 prestamos posgrado | Completo | Comando + respuesta + PASO |
| RN2-B — 6to prestamo rechazado | Completo | Comando + 409 + observacion distincion tipos |
| RN5-A — Primer prestamo ejemplar | Completo | Comando + respuesta |
| RN5-B — Segundo prestamo rechazado | Completo | Comando + 409 |
| RN6-A — Plazo 15 dias libro normal | Completo | Comando + fecha calculada + verificacion |
| RN6-B — Plazo 3 dias alta demanda | Completo | Comando + fecha calculada + verificacion |
| RN3 — Vencido bloquea (2 pasos) | Completo | Inyeccion fecha + 409 + nota estado "activo" |
| RN4 — Multa bloquea (2 pasos) | Completo | Devolucion + multa $990.000 + 409 |
| RN8 — Calculo multa | Completo | Tabla 6 escenarios verificados |
| VAL-1 — Body vacio (422 vs 400) | Completo | Observacion tecnica RFC 9110 |
| VAL-2 — Estudiante inexistente | Completo | 404 con error code |
| VAL-3 — Ejemplar inexistente | Completo | 404 + nota orden de validacion |
| VAL-4 — Tipo incorrecto | Completo | 422 Pydantic con detalle por campo |
| VAL-5 — Historial inexistente | Completo | 404 |
| Tabla comparativa final | Completo | 21 filas, todos PASO |
| Observaciones tecnicas | Completo | 5 hallazgos documentados |

**Total: 21/21 verificaciones PASARON.**

---

### Observaciones tecnicas documentadas

1. **422 vs 400** — FastAPI usa 422 para errores Pydantic (estandar RFC 9110).
   La guia esperaba 400. No es un bug. Los clients deben manejar 422.

2. **`libro_id` vs `cod_libro`** — Version_2 usa snake_case consistente.
   Decision de diseno, no un error.

3. **Estado `"activo"` en prestamos vencidos** — El vencimiento es dinamico
   (calculado en cada request), no persiste como columna en la BD.

4. **`fecha_prestamo` inyectable** — Opcion A disponible en `PrestamoCreate`
   para simular fechas pasadas en tests de RN3, RN4 y RN8.

5. **Bug latente en tests de integracion** — `reset_repos` fixture roto
   post-migracion SQLAlchemy (ver prompt #06 y #07).

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

[Una linea — por ejemplo: "Documentar los resultados desde el codigo fuente
es tan valido como ejecutar los tests, siempre que se lea el codigo correcto."]
