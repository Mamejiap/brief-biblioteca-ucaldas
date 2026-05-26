# Prompt #05

**Fecha y hora:** 2026-05-25 10:15

**Propósito en una línea:** Diseñar e implementar una base de datos SQLite embebida para Version_1 con tablas de estudiantes, libros y préstamos

**Etapa del taller:** 1

**IA usada:** GitHub Copilot

---

### Prompt enviado (literal)

```
Actúa con un doble rol: como mi Arquitecto de Soluciones experto en Python y como mi Gestor de Documentación del proyecto.

PARTE 1: DISEÑO DE BASE DE DATOS (Versión 1)
Necesito que diseñes y crees el script de una base de datos SQLite embebida, destinada exclusivamente para la 'Versión 1' de nuestra API de préstamos de biblioteca. 

Ten en cuenta estas restricciones de diseño para la V1:
1. Simplicidad absoluta: La V1 no tiene Clean Architecture ni validaciones complejas. Todo debe ser directo y fácil de consumir desde un único archivo 'Version_1\main.py' con FastAPI.
2. Entidades: Debe soportar Estudiantes, Libros/Ejemplares y Préstamos.
3. Datos iniciales (Seed): Incluye inserts con datos de prueba básicos (ej: estudiante 'EST-001', ejemplar 'EJ-001') para replicar los casos de prueba del taller.

Entrégame: El diseño explicado brevemente, el código SQL (`CREATE TABLE` e `INSERT`) y un ejemplo corto en Python con la librería `sqlite3`.

===========================================================

PARTE 2: GESTIÓN AUTOMÁTICA DEL PROMPT (Documentación en /prompts)
Como mi Gestor de Documentación, una vez que termines de generar la base de datos anterior, debes documentar esta interacción de forma automática siguiendo estas reglas:

1. Revisa de manera autónoma los archivos existentes en la carpeta `/prompts` (en la raíz del proyecto) para identificar el último número utilizado por mi compañero.
2. Continúa la secuencia numérica exacta y crea el siguiente archivo individual usando el formato: `XX-nombre-descriptivo.md`.
3. Sigue estrictamente la estructura definida en la plantilla de `02-tu-trabajo\plantilla-prompts.md`.
4. En la sección "Prompt enviado (literal)", transcribe exactamente el texto que te estoy enviando aquí. En "Resumen de la respuesta" sé crítico y breve (3-5 líneas). En "Mi evaluación" deja los campos de checkbox listos.

Comienza entregándome el diseño de la base de datos y confirmando la creación del archivo de documentación correspondiente en la carpeta `/prompts`.
```

---

### Resumen de la respuesta de la IA

Creó 4 archivos en `Version_1/`: `database.sql` (script SQL con 3 tablas: estudiantes, libros, prestamos; 3 inserts de prueba; 4 índices para optimización), `db_setup.py` (módulo con init_db() + context manager get_db() + 5 helpers; 130 líneas de código robusto), `db_example.py` (5 ejemplos completos de CRUD, préstamos, devoluciones, estadísticas; 250 líneas ejecutables), `DISEÑO_BD.md` (documentación técnica completa del esquema). Decisión autónoma: omitir tabla "ejemplares" (usa cantidad_disponible en libros) para máxima simplicidad V1. Sin dependencias adicionales (solo sqlite3 estándar). Creó documentación automática en /prompts/05.

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

Cuando pido "simplicidad absoluta" para V1, Copilot es capaz de simplificar decisiones de diseño (omitir tabla ejemplares) sin sacrificar funcionalidad. Los context managers + row_factory generan código seguro y Pythonic automáticamente. La documentación técnica generada anticipa preguntas de integración futura.

---
