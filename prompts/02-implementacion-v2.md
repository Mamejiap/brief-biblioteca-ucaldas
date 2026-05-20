# Registro de Prompt — #02

## Prompt #02

**Fecha y hora:** 2026-05-20 04:45 (aprox.)

**Propósito en una línea:** Aprobación del árbol de directorios y elección de Opción A para reservas; dar luz verde a la IA para escribir todo el código de la Versión 2.

**Etapa del taller:** Etapa 2 — Generación del proyecto con IA

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Apruebo el arbol de directorios y prefiero la Opcion A para las reservas
```

---

### Resumen de la respuesta de la IA

Con este único mensaje de aprobación, la IA procedió a escribir la totalidad del proyecto. Creó los siguientes grupos de archivos en orden secuencial:

**Archivos base:** `.gitignore`, `.env`, `requirements.txt`, `README.md`, `main.py`.

**Capa Domain (10 archivos):** entidades (`Libro`, `Ejemplar`, `Estudiante`, `Prestamo`, `Multa`, `Reserva`), interfaces de repositorio abstractas (5 archivos ABC), y `exceptions.py` con 13 excepciones de dominio tipadas mapeadas a códigos HTTP específicos.

**Capa Application (11 casos de uso):** `CrearLibro`, `AgregarEjemplar`, `ListarLibros`/`ObtenerLibro`, `CrearEstudiante`, `ObtenerHistorial`, `CrearPrestamo` (evalúa RN1–RN5), `RegistrarDevolucion` (RN8), `RenovarPrestamo` (RN7), `ListarVencidos`, `CrearReserva`, `CancelarReserva`.

**Capa Infrastructure (5 repositorios):** implementaciones en memoria usando `dict[str, Entidad]`.

**Capa API (7 archivos):** schemas Pydantic separados de las entidades de dominio, 4 routers (`/api/libros`, `/api/estudiantes`, `/api/prestamos`, `/api/reservas`), `dependencies.py` con singletons de repositorios, `error_handlers.py` que mapea cada excepción de dominio a su código HTTP.

**Tests (4 archivos):** `conftest.py` con fixtures, 3 archivos de tests unitarios (sin HTTP), 1 archivo de tests de integración con 20 tests usando `TestClient`.

**Decisiones que la IA tomó sin que se las pidiera explícitamente:**

- Separó los schemas Pydantic (`api/schemas.py`) de las entidades de dominio — el prompt original no especificaba esta separación.
- Usó `dataclass` para las entidades de dominio en lugar de `BaseModel` de Pydantic, preservando la independencia de la capa de dominio respecto a frameworks externos.
- Agregó el parámetro opcional `fecha_prestamo` en `CrearPrestamoInput` para permitir inyección de fechas en tests (necesario para simular RN3 y RN4 con préstamos vencidos).
- Definió `TARIFA_MULTA_POR_DIA = 2_000` como constante en `multa.py` en lugar de hardcodearla en los casos de uso.
- Creó un endpoint `GET /api/prestamos/vencidos` que además actualiza el estado de los préstamos a `"vencido"` como efecto secundario — esta doble responsabilidad no fue solicitada.
- En `ListarVencidos`, decidió que el endpoint también muta el estado de los préstamos, lo cual mezcla lectura y escritura.
- Los repositorios en `dependencies.py` son singletons globales (variables de módulo), no instancias creadas por FastAPI en cada request.

**Limitación admitida:** El sandbox no tenía acceso a internet para instalar dependencias y correr `pytest` formalmente. En su lugar, la IA ejecutó un script Python que importó todos los módulos de dominio + infrastructure (sin FastAPI) y verificó las 7 reglas de negocio directamente. Todos los tests pasaron. También ejecutó `py_compile` sobre los 30+ archivos del proyecto sin errores.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.
- [ ] Parcialmente. Faltó: [...]
- [ ] No, se desvió. Hizo: [...]

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.
- [ ] La modifiqué a mano. Cambios: [...]
- [ ] Le pedí corrección con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechacé completamente. Razón: [...]

**¿Qué aprendí de esta interacción?**

[Una línea sobre qué te llevaste de este prompt. Por ejemplo:
> "Un prompt de 7 palabras ('Apruebo el arbol y prefiero la Opcion A') fue suficiente para que la IA generara ~1.000 líneas de código. El contexto de la conversación anterior era todo el briefing que necesitaba."]
