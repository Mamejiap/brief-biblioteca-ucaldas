# Registro de Prompt — #11

## Prompt #11

**Fecha y hora:** 2026-05-30

**Proposito en una linea:** Auditar y expandir la documentacion tecnica del
chatbot Ollama sincronizando las reglas de negocio de la especificacion formal
con el system prompt, corrigiendo los endpoints contra el codigo real de
Version_2, y generando 6 preguntas de prueba desafiantes.

**Etapa del taller:** Etapa 5 — Integracion de IA Local (Ollama)

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Asunto: Integracion de IA Local (Ollama) y Expansion de Reglas de Negocio
Actua como Arquitecto de Soluciones de IA. Estamos integrando Ollama como
chatbot para nuestra biblioteca. Necesito que audites y expandas la
documentacion tecnica.

1. Auditoria y Cruce de Informacion
   - Fuente A: plantilla-especificacion.md
   - Fuente B: taller-ollama-chatbot.md (Especialmente el punto 4.2)

2. Tareas de Actualizacion (Punto 4.2)
   a. Sincronizacion: reglas de la especificacion no cubiertas en el chatbot.
   b. Expansion: total de 7 reglas adicionales (spec + logicas propuestas,
      sin duplicados).
   c. Auditoria de Endpoints: comparar guia vs codigo real en Version_2;
      agregar faltantes y eliminar inexistentes.

3. Generacion de Pruebas (Punto 5): 6 preguntas adicionales desafiantes.

4. Salida: taller-ollama-chatbot-v2.md + prompts/11-configuracion-chatbot-ollama.md
```

---

### Archivos analizados

- `02-tu-trabajo/plantilla-especificacion.md` — especificacion formal con
  entidades, 10 reglas de negocio (RN1-RN10), endpoints REST y decisiones.
- `02-tu-trabajo/taller-ollama-chatbot.md` — chatbot original con 8 reglas
  (RN1-RN8) y 10 endpoints en el SYSTEM_PROMPT.
- `Version_2/app/api/routers/libros.py` — rutas reales de libros y ejemplares.
- `Version_2/app/api/routers/prestamos.py` — rutas reales de prestamos.
- `Version_2/app/api/routers/estudiantes.py` — rutas reales de estudiantes.
- `Version_2/app/api/routers/reservas.py` — rutas reales de reservas.

---

### Resumen de la respuesta de la IA

**Hallazgos de la auditoria:**

**Reglas presentes en plantilla-especificacion.md pero ausentes del chatbot:**
1. RN6/spec — Proceso de devolucion: cambia estado prestamo, libera ejemplar,
   genera multa automaticamente. El chatbot mencionaba RN8 (multa) pero no
   el flujo completo de devolucion ni el 409 por prestamo ya devuelto.
2. RN8/spec — Renovacion: condiciones completas (activo, no vencido, sin espera).
   El chatbot solo mencionaba la parte de lista de espera, omitiendo que
   el prestamo debe estar activo y no vencido.
3. RN9/spec — Calculo dinamico de vencidos: el estado "vencido" no se persiste.
4. RN10/spec — Historial completo: incluye prestamos + multas + monto pendiente.

**Reglas logicas propuestas (no estaban en ningun documento):**
5. Alta demanda no renovable — libros alta_demanda=true tienen plazo fijo,
   no aplica renovacion independientemente de la lista de espera.
6. Reservas FIFO — prioridad de atencion por fecha_reserva mas antigua.
7. Cancelacion de reserva desbloquea renovacion.

**Endpoints incorrectos en chatbot v1:**
- `GET /api/estudiantes` — listado de todos los estudiantes NO existe en
  Version_2 (no hay router para eso). Eliminado del SYSTEM_PROMPT.
- `GET /api/prestamos` — listado general NO existe en Version_2. Eliminado.

**Endpoints faltantes en chatbot v1 que si existen en Version_2:**
- `GET /api/libros/:id` — detalle de libro con ejemplares
- `GET /api/libros?sala=&alta_demanda=&disponible=` — filtros de catalogo
- `GET /api/estudiantes/:id` — obtener estudiante individual
- `GET /api/prestamos/vencidos` — lista dinamica de vencidos
- `GET /api/prestamos/:id` — obtener un prestamo por ID
- `POST /api/reservas` — crear solicitud de reserva
- `DELETE /api/reservas/:id` — cancelar reserva

**Brecha documentada:**
- `POST /multas/:id/pago` — existe en la especificacion (D6) pero NO fue
  implementado en Version_2. Se incluye en las notas de implementacion del
  SYSTEM_PROMPT como brecha conocida. La pregunta 6-E del chatbot
  explicitamente pregunta al modelo si detecta esta brecha.

**Resultado final del SYSTEM_PROMPT v2:**
- 15 reglas de negocio (8 originales + 7 nuevas).
- 14 endpoints correctos (vs 10 originales con 2 incorrectos).
- Notas de implementacion agregadas: snake_case, Opcion A, 422 vs 400,
  endpoints inexistentes advertidos.

**6 preguntas desafiantes generadas (Sesion 6):**

| # | Pregunta | Reglas que valida |
|---|----------|-------------------|
| 6-A | Conflicto simultáneo: limite + vencido + multa | RN1+RN3+RN4 — orden de evaluacion |
| 6-B | Renovacion de libro alta demanda sin reserva | RN10 vs RN9 — no confundir |
| 6-C | Calculo multa con inyeccion de fecha | RN8 + Opcion A — campo fecha_prestamo |
| 6-D | Reserva que bloquea renovacion | RN9+RN13 — interaccion entre reglas |
| 6-E | Desbloqueo por pago — brecha de implementacion | RN4 + brecha POST /multas/:id/pago |
| 6-F | Error 422 por camelCase en Version_2 | Nomenclatura snake_case + Pydantic 422 |

**Archivos creados:**
- `02-tu-trabajo/taller-ollama-chatbot-v2.md` — version expandida (596 lineas,
  0 null bytes, 16/16 verificaciones OK).
- `prompts/11-configuracion-chatbot-ollama.md` — este archivo.

**Archivo NO modificado:** `02-tu-trabajo/taller-ollama-chatbot.md` — original
preservado intacto segun la instruccion del prompt.

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

[Una linea — por ejemplo: "El chatbot v1 le decia al modelo que existian
endpoints que nunca se implementaron; eso habria causado que generara curls
invalidos en produccion."]
