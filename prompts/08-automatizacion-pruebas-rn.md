# Registro de Prompt — #08

## Prompt #08

**Fecha y hora:** 2026-05-25

**Proposito en una linea:** Generar un script Python automatizado que valide
secuencialmente las reglas de negocio RN1-RN8 y VAL contra el servidor
FastAPI en http://localhost:3001, imprimiendo un reporte PASO/FALLO por
cada verificacion.

**Etapa del taller:** Etapa 4 — Validacion automatizada de reglas de negocio

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Asunto: Automatizacion y Ejecucion de Casos de Prueba RN1-RN6

Actua como QA Engineer. Ya tengo el servidor FastAPI corriendo en
http://localhost:3001 y la base de datos SQLite conectada.

1. Tarea: Crear Script de Validacion
   Genera un archivo ejecutar_pruebas_taller.py en
   Version_2\tests. Debe usar requests para ejecutar:
   - Fase 1: Crear estudiantes, libros y ejemplares (1.1 y 1.2).
   - Fase 2: Casos de prueba RN1 a RN6-B.
   Ejemplo: Intentar un prestamo que debe fallar y verificar el error.

2. Requerimientos
   - Imprimir: RN1: PASO o RN1: FALLO (Razon).
   - Campos snake_case corregidos (estudiante_id, alta_demanda).

3. Instrucciones para mi: como ejecutar el script.

4. Registro: crear prompts/08-automatizacion-pruebas-rn.md.
```

---

### Descripcion del script generado

**Archivo:** `Version_2/tests/ejecutar_pruebas_taller.py`
**Lineas:** 574 | **Dependencia:** `requests` (pip install requests)

El script tiene 5 secciones en secuencia:

**PASO 0 — Health check**
Verifica que el servidor responda en `/` antes de comenzar.
Aborta si no hay conexion, con instruccion clara de como arrancar uvicorn.

**FASE 1 — Carga de datos (1.1 y 1.2)**
Crea EST-PRE-01, EST-POS-01, LIB-001, LIB-002, EJ-001-01 a EJ-001-06,
EJ-002-01. Maneja el caso "ya existia" (HTTP 400 con "ya existe") como
resultado valido — permite correr el script multiples veces sin borrar la BD.

**Fase 2 — Reglas de negocio:**

| Funcion | Regla | Logica de verificacion |
|---------|-------|------------------------|
| `rn1_pregrado_max_3()` | RN1 | 3 prestamos → 201 x3; 4to → 409; cleanup devolucion |
| `rn2_posgrado_max_5()` | RN2 | 5 prestamos → 201 x5; 6to → 409; cleanup devolucion |
| `rn5_ejemplar_ya_prestado()` | RN5 | Prestamo A → 201; Prestamo B mismo ej → 409; cleanup |
| `rn6_plazos()` | RN6 | Normal: fecha+15; Alta demanda: fecha+3; verifica campo |
| `rn3_vencido_bloquea()` | RN3 | Inyecta fecha_prestamo=2025-01-01; nuevo prestamo → 409 |
| `rn4_multa_bloquea()` | RN4 | Devuelve el prestamo vencido (genera multa); nuevo → 409 |
| `rn8_calculo_multa()` | RN8 | Inyecta fecha hace 20 dias; devolucion hoy = 5 dias retraso; multa=$10.000 |
| `val_validaciones()` | VAL | Body vacio, estudiante/ejemplar inexistente, historial 404 |

**Decisiones tecnicas relevantes:**

- Los tests comparten la BD SQLite. Cada funcion devuelve sus prestamos al
  terminar (limpieza explicita) para no contaminar el siguiente test.
- RN3 y RN4 estan encadenados: RN3 devuelve el `prestamo_vencido_id` que RN4
  usa para registrar la devolucion y generar la multa.
- Se usa `"fecha_prestamo"` en el body (Opcion A disponible en Version_2) para
  simular prestamos vencidos sin modificar el codigo ni la base de datos.
- VAL-1 acepta tanto 422 (Pydantic/FastAPI estandar) como 400 como correcto.
- El script usa codigos ANSI para color: verde PASO, rojo FALLO, cyan detalles.
- Imprime resumen final con conteo de pasaron/fallaron y exit code 1 si hay fallos.

---

### Comando para ejecutar

```bash
# 1. Asegurate de tener el servidor corriendo:
cd C:\Users\matem\brief-biblioteca-ucaldas-1\Version_2
uvicorn main:app --reload --port 3001

# 2. En otra terminal, instala requests si no lo tienes:
pip install requests

# 3. Ejecuta el script desde la carpeta Version_2:
cd C:\Users\matem\brief-biblioteca-ucaldas-1\Version_2
python tests/ejecutar_pruebas_taller.py
```

El script imprime un reporte como este:

```
══════════════════════════════════════════════════════════════
  Suite de Validacion — Biblioteca UCaldas Version_2
  Objetivo: http://localhost:3001
══════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────
  PASO 0 — Verificacion del servidor
────────────────────────────────────────────────────────────
  PASO ✅  Servidor responde correctamente  (version=2.0.0)

────────────────────────────────────────────────────────────
  RN1 — Pregrado: maximo 3 prestamos simultaneos
────────────────────────────────────────────────────────────
  PASO ✅  RN1-A: 3 prestamos simultaneos creados  (201 x 3)
  PASO ✅  RN1-B: 4to prestamo pregrado rechazado  (409 error=limite_prestamos_alcanzado limite=3)
...

══════════════════════════════════════════════════════════════
  RESUMEN FINAL
══════════════════════════════════════════════════════════════
  Verificaciones totales : 24
  Pasaron  : 24
  Fallaron : 0
  Todas las reglas de negocio validadas correctamente.
```

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

[Una linea — por ejemplo: "El orden de los tests en un script compartido
de BD importa tanto como la logica de cada test individual."]
