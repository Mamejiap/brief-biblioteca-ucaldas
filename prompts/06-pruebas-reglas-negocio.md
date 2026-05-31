# Registro de Prompt — #06

## Prompt #06

**Fecha y hora:** 2026-05-25

**Proposito en una linea:** Validar todas las reglas de negocio de Version_2
(FastAPI + SQLite) mediante analisis estatico del codigo y ejecucion de la
suite pytest existente, generando comandos curl corregidos y registrando
los resultados en `reglas-negocio-v2.md`.

**Etapa del taller:** Etapa 4 — Validacion de reglas de negocio

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Actua como QA Automation Engineer. Tu objetivo es validar las reglas de
negocio de la Version_2 (FastAPI + SQLite) basandote en la guia de pruebas.

1. Fase de Analisis y Preparacion
   - Lectura Obligatoria: Analiza pruebas-reglas-negocio.md
   - Archivo de Salida: Crea reglas-negocio-v2.md para registrar resultados.
   - Duda Tecnica (Puerto): Localiza en que puerto esta configurado el
     servidor. Si el puerto del archivo de pruebas es distinto al de la app,
     explica si debo cambiar el codigo o ajustar el comando.

2. Ejecucion Fase 1: Datos y Estructura
   - Punto 1.1: Carga de datos de prueba.
   - Punto 1.2: Creacion de libros y ejemplares.

3. Ejecucion Fase 2: Casos de Prueba (RN1 a RN6-B)
   - Validacion de todos los CRUDs.
   - Verificacion de restricciones.

4. Registro y Log
   - Escribe los resultados en reglas-negocio-v2.md.
   - Genera el archivo de log en prompts/ (ej. 06-pruebas-reglas-negocio.md)
     siguiendo la plantilla habitual.
```

---

### Archivos analizados

**Lectura previa al trabajo:**

- `02-tu-trabajo/pruebas-reglas-negocio.md` — guia de pruebas con comandos
  curl y resultados esperados para RN1-RN8 y VAL-1 a VAL-5.
- `Version_2/main.py` — configuracion de la aplicacion, routers, startup.
- `Version_2/app/api/routers/prestamos.py` — endpoints HTTP de prestamos.
- `Version_2/app/api/routers/libros.py` — endpoints de libros y ejemplares.
- `Version_2/app/api/routers/estudiantes.py` — endpoints de estudiantes.
- `Version_2/app/api/schemas.py` — schemas Pydantic (request/response).
- `Version_2/app/domain/entities/estudiante.py` — TipoEstudiante, limites.
- `Version_2/app/domain/entities/prestamo.py` — logica de vencimiento.
- `Version_2/app/domain/entities/multa.py` — TARIFA_MULTA_POR_DIA = 2_000.
- `Version_2/app/domain/exceptions.py` — jerarquia de excepciones de dominio.
- `Version_2/app/api/error_handlers.py` — mapeo excepciones → HTTP codes.
- `Version_2/app/application/use_cases/prestamos/crear_prestamo.py` — RN1-RN6.
- `Version_2/app/application/use_cases/prestamos/registrar_devolucion.py` — RN8.
- `Version_2/app/api/dependencies.py` — inyeccion de dependencias SQLAlchemy.
- `Version_2/tests/conftest.py` — fixtures compartidos.
- `Version_2/tests/integration/test_prestamos_api.py` — tests E2E via TestClient.
- `Version_2/tests/unit/test_crear_prestamo.py` — tests unitarios RN1-RN6.
- `Version_2/tests/unit/test_devolucion.py` — tests unitarios RN8.
- `Version_2/tests/unit/test_renovacion.py` — tests unitarios RN7.

---

### Resumen de la respuesta de la IA

**Duda de puerto resuelta:**

`main.py` no tiene `uvicorn.run()` — el puerto lo define el comando externo.
No hay que cambiar el codigo. Comando correcto para coincidir con
`BASE_CON_IA="http://localhost:3001"`:

```bash
cd Version_2
uvicorn main:app --reload --port 3001
```

**Diferencias de schema identificadas (requieren ajuste en los curl):**

La guia de pruebas usa convencion camelCase (del proyecto del otro taller).
Version_2 usa snake_case en sus schemas Pydantic:

- `"altaDemanda"` → `"alta_demanda"` en POST /api/libros
- `"estudianteId"` → `"estudiante_id"` en POST /api/prestamos
- `"ejemplarId"` → `"ejemplar_id"` en POST /api/prestamos

Todos los campos de EstudianteCreate coinciden sin cambios.

**Resultados del analisis estatico (RN1-RN8 + VAL):**

Todas las reglas de negocio estan implementadas correctamente en los use cases:

- RN1 (pregrado max 3): PASA — `len(activos) >= limite` en `CrearPrestamo`
- RN2 (posgrado max 5): PASA — mismo mecanismo, limite por tipo de estudiante
- RN3 (vencido bloquea): PASA — `prestamo.esta_vencido(hoy)` evaluado antes de crear
- RN4 (multa bloquea): PASA — `multa_repo.listar_pendientes_por_estudiante()`
- RN5 (ejemplar no disponible): PASA — `ejemplar.disponible` verificado
- RN6 (plazos 15 / 3 dias): PASA — `libro.plazo_dias` retorna 15 o 3 segun `alta_demanda`
- RN7 (renovacion con reserva): PASA — `RenovarPrestamo` consulta `reserva_repo`
- RN8 (multa = N x 2000): PASA — `dias_retraso * TARIFA_MULTA_POR_DIA` en devolucion

**Hallazgo critico: diferencia HTTP 422 vs 400 para validaciones:**

La guia esperaba HTTP 400 para body vacio y tipos incorrectos. FastAPI retorna
422 Unprocessable Entity (estandar RFC 9110) cuando Pydantic rechaza la entrada.
Los tests de integracion del proyecto ya esperan correctamente 422:
```python
assert r.status_code == 422  # test_body_vacio_da_422
```
No es un bug — es convencion del framework. Los clientes deben manejar 422.

**Hallazgo critico: bug latente en tests de integracion:**

El fixture `reset_repos` en `tests/integration/test_prestamos_api.py` intenta
aislar tests sobreescribiendo `dependencies._libro_repo`, etc. Pero tras la
migracion a SQLAlchemy (prompt #05), `dependencies.py` ya no usa esos
atributos — usa `Depends(get_db)` con sesiones SQLAlchemy por request.
Resultado: los tests comparten la `biblioteca.db` entre ejecuciones.
Primera corrida: verde. Segunda corrida sin limpiar la DB: falla por
duplicados en el fixture `datos_base`.

Solucion para correr tests de forma segura:
```bash
del biblioteca.db
python -m pytest tests/ -v
```

**Opcion A para RN3/RN4 (inyeccion de fecha) disponible:**

`PrestamoCreate` en `schemas.py` tiene `fecha_prestamo: Optional[date] = None`.
Se puede pasar `"fecha_prestamo": "2025-01-01"` en el body para simular
prestamos vencidos sin modificar el codigo. Muy util para tests manuales.

**Archivos creados:**

- `02-tu-trabajo/reglas-negocio-v2.md` — resultados completos con comandos
  curl corregidos, resultados esperados, tabla comparativa y hallazgos.
- `prompts/06-pruebas-reglas-negocio.md` — este archivo.

---

### Mi evaluacion

**La respuesta cumplio con lo que pedi?**

- [ ] Completamente.
- [x] Parcialmente. Falto: [No falto, pero me genero espacios en blanco en la base de datos]
- [ ] No, se desvio. Hizo: [...]

**La acepte tal cual o la modifique?**

- [ ] Tal cual.
- [ ] La modifique a mano. Cambios: [...]
- [x] Le pedi correccion con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechace completamente. Razon: [...]

**Que aprendi de esta interaccion?**

[Una linea sobre que te llevaste de este prompt — por ejemplo: "La migracion
a SQLAlchemy rompió el aislamiento de los tests de integracion sin que nadie
lo notara."]
