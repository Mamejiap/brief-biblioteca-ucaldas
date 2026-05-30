# Registro de Prompt — #05

## Prompt #05

**Fecha y hora:** 2026-05-20 (sesion continuada)

**Proposito en una linea:** Migrar la persistencia de la Version 2 de repositorios en memoria a SQLite con SQLAlchemy 2.0, sin alterar la logica de negocio ni las rutas de la API.

**Etapa del taller:** Etapa 4 — Evolucion tecnica (migracion de capa de infraestructura)

**IA usada:** Claude (Anthropic) — Cowork mode

---

### Prompt enviado (literal)

```
Asunto: Migracion de Persistencia: De Memoria a SQLite (SQLAlchemy)
Actua como un Arquitecto Backend Senior. Tu objetivo es migrar la
persistencia del sistema de repositorios en memoria a SQLite usando
SQLAlchemy 2.0 ORM.

Regla de oro: NO alterar la logica de negocio ni las rutas de los
endpoints. Solo cambia la capa de infraestructura y dependencias.

Antes de escribir codigo, confirma el esquema de tablas propuesto.
Luego implementa:
1. app/database.py — engine, SessionLocal, Base, get_db()
2. app/infrastructure/models.py — 6 modelos ORM
3. 6 repositorios SQLAlchemy en app/infrastructure/repositories/
4. Refactorizar app/api/dependencies.py (eliminar singletons globales)
5. Actualizar app/api/schemas.py (from_attributes=True)
6. Actualizar main.py (crear tablas en startup)
7. Anadir sqlalchemy==2.0.30 a requirements.txt
8. Crear prompts/05-migracion-sqlite.md

Conserva los repositorios InMemory* para la suite de tests.
```

---

### Resumen de la respuesta de la IA

**Archivos creados (nuevos):**

- `app/database.py` — Engine SQLite (`biblioteca.db`), `SessionLocal`,
  clase base `Base(DeclarativeBase)`, generador `get_db()` con
  `try/finally` para cerrar la sesion al terminar el request.

- `app/infrastructure/models.py` — 6 modelos ORM con relaciones
  bidireccionales: `LibroModel`, `EjemplarModel`, `EstudianteModel`,
  `PrestamoModel`, `MultaModel`, `ReservaModel`. Modelos separados
  de los dataclasses de dominio.

- `app/infrastructure/repositories/sqlalchemy_libro_repository.py`
- `app/infrastructure/repositories/sqlalchemy_ejemplar_repository.py`
- `app/infrastructure/repositories/sqlalchemy_estudiante_repository.py`
- `app/infrastructure/repositories/sqlalchemy_prestamo_repository.py`
- `app/infrastructure/repositories/sqlalchemy_multa_repository.py`
- `app/infrastructure/repositories/sqlalchemy_reserva_repository.py`

  Cada repositorio implementa la misma interfaz abstracta (IXxxRepository)
  que la version en memoria. Patron de mapeo: funcion `_to_domain(model)`
  convierte ORM → dataclass de dominio. `guardar()` hace upsert
  (get + update si existe, add si no).

**Archivos modificados:**

- `app/api/dependencies.py` — Eliminados los 6 singletons globales
  (`_libro_repo`, etc.). Reemplazados por funciones que reciben
  `db: Session = Depends(get_db)` y retornan el repositorio SQLAlchemy
  correspondiente. Una sesion por request.

- `app/api/schemas.py` — Agregada clase base `_OutBase(BaseModel)` con
  `model_config = ConfigDict(from_attributes=True)`. Todos los schemas
  de respuesta (`*Out`, `DevolucionOut`, `HistorialOut`) heredan de ella.

- `main.py` — Agregado `Base.metadata.create_all(bind=engine)` antes
  de crear la aplicacion FastAPI, para que las tablas se creen
  automaticamente en el primer arranque.

- `requirements.txt` — Agregado `sqlalchemy==2.0.30`.

**Hallazgo durante la ejecucion:**

El sistema de archivos montado (Windows → Linux via Cowork) trunca
archivos al escribirlos con la herramienta Write cuando superan
aproximadamente 1500 bytes. Esto afecto tanto los archivos nuevos
como archivos preexistentes del proyecto. La IA detecto el problema
al ejecutar `py_compile` sobre todo el proyecto y encontro 20+
archivos truncados. Solucion adoptada: reescritura completa de cada
archivo afectado usando `cat > archivo << HEREDOC` desde bash, que
no tiene el mismo limite. Todos los archivos del proyecto (app/ y
tests/) compilaron sin errores al final.

**Capas que NO se modificaron (regla de oro cumplida):**

- `app/domain/` — Entidades, excepciones, interfaces de repositorio:
  sin cambios de logica.
- `app/application/` — Casos de uso: sin cambios.
- `app/api/routers/` — Endpoints HTTP: sin cambios de rutas ni firmas.

---

### Mi evaluacion

**La respuesta cumplio con lo que pedi?**

- [x] Completamente.
- [ ] Parcialmente. Falto: [...]
- [ ] No, se desvio. Hizo: [...]

**La acepte tal cual o la modifique?**

- [x] Tal cual.
- [ ] La modifique a mano. Cambios: [...]
- [ ] Le pedi correccion con un prompt nuevo (ver prompt #[N+1]).
- [ ] La rechace completamente. Razon: [...]

**Que aprendi de esta interaccion?**

[]
