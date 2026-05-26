# Diseño de Base de Datos SQLite - Version_1

## 📋 Resumen del Diseño

La base de datos para la **Version_1** está diseñada con **máxima simplicidad** para integración directa con FastAPI. Usa **3 tablas principales** con relaciones simples:

```
ESTUDIANTES (ID, Código, Nombre, Email, Carrera)
        ↓ (1:N)
PRESTAMOS ← (N:1) → LIBROS (ID, Título, Autor, ISBN, Cantidad)
```

---

## 📊 Esquema de Tablas

### 1. **ESTUDIANTES** - Registra los datos de los estudiantes

| Campo | Tipo | Restricción | Descripción |
|-------|------|------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `codigo_est` | TEXT | UNIQUE | Código del estudiante (EST-001, EST-002, ...) |
| `nombre` | TEXT | NOT NULL | Nombre completo |
| `email` | TEXT | NOT NULL | Correo institucional |
| `carrera` | TEXT | NOT NULL | Carrera/Programa |
| `fecha_registro` | DATETIME | DEFAULT NOW | Fecha de registro |

**Ejemplo:**
```sql
INSERT INTO estudiantes VALUES (1, 'EST-001', 'Juan Pérez', 'juan.perez@ucaldas.edu.co', 'Ingeniería de Sistemas', '2026-05-20');
```

---

### 2. **LIBROS** - Registra los libros con control de disponibilidad

| Campo | Tipo | Restricción | Descripción |
|-------|------|------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único |
| `titulo` | TEXT | NOT NULL | Título del libro |
| `autor` | TEXT | NOT NULL | Autor del libro |
| `isbn` | TEXT | UNIQUE | ISBN único |
| `cantidad_disponible` | INTEGER | NOT NULL | Copias disponibles (se actualiza con préstamos) |
| `cantidad_total` | INTEGER | NOT NULL | Total de copias en la biblioteca |
| `fecha_creacion` | DATETIME | DEFAULT NOW | Fecha de ingreso |

**Ejemplo:**
```sql
INSERT INTO libros VALUES (1, 'Clean Code', 'Robert C. Martin', '978-0132350884', 3, 5, '2026-05-20');
```

**Nota:** `cantidad_disponible` se decrementa cuando se crea un préstamo y se incrementa cuando se devuelve.

---

### 3. **PRESTAMOS** - Registra las transacciones de préstamo/devolución

| Campo | Tipo | Restricción | Descripción |
|-------|------|------------|-------------|
| `id` | INTEGER | PK, AUTO | Identificador único del préstamo |
| `estudiante_id` | INTEGER | FK → estudiantes | ID del estudiante |
| `libro_id` | INTEGER | FK → libros | ID del libro |
| `fecha_prestamo` | DATETIME | DEFAULT NOW | Cuándo se prestó |
| `fecha_vencimiento` | DATETIME | NOT NULL | Cuándo debe devolverse |
| `fecha_devolucion` | DATETIME | NULLABLE | Cuándo se devolvió (NULL si está vigente) |
| `estado` | TEXT | CHECK | Estado: `activo`, `vencido`, `devuelto` |

**Ejemplo:**
```sql
INSERT INTO prestamos 
VALUES (1, 1, 1, '2026-05-20 10:00', '2026-06-03 10:00', NULL, 'activo');
```

---

## 🔍 Índices para Optimización

Se crean 4 índices para acelerar las queries más comunes:

```sql
idx_prestamos_estudiante  -- Para filtrar por estudiante
idx_prestamos_libro       -- Para filtrar por libro
idx_prestamos_estado      -- Para consultar vigentes/devueltos
idx_estudiantes_codigo    -- Para búsquedas por código EST-xxx
```

---

## 🌱 Datos Iniciales (SEED)

### Estudiantes
```
EST-001 | Juan Pérez          | juan.perez@ucaldas.edu.co        | Ingeniería de Sistemas
EST-002 | María García        | maria.garcia@ucaldas.edu.co      | Ingeniería de Sistemas
EST-003 | Carlos López        | carlos.lopez@ucaldas.edu.co      | Administración de Empresas
```

### Libros
```
Clean Code                    | Robert C. Martin | 978-0132350884 | 3/5 disponibles
Design Patterns              | Gang of Four     | 978-0201633610 | 2/3 disponibles
The Pragmatic Programmer     | Hunt & Thomas    | 978-0135957059 | 4/4 disponibles
```

### Préstamos
Sin datos iniciales (se generan al usar la API).

---

## 🚀 Cómo Usar

### 1. Inicializar la BD automáticamente

```python
from db_setup import init_db

# Crea BD, tablas e inserta datos iniciales
init_db()
```

### 2. Conectarse y ejecutar queries

**Opción A: Con context manager (recomendado)**
```python
from db_setup import get_db

with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
```

**Opción B: Usar helpers predefinidos**
```python
from db_setup import get_all_libros, get_prestamos_vigentes

libros = get_all_libros()
vigentes = get_prestamos_vigentes()
```

### 3. Ejecutar ejemplos

```bash
python db_example.py
```

Mostrará 5 ejemplos completos:
- ✓ Operaciones CRUD
- ✓ Crear préstamo + decrementar disponibles
- ✓ Consultar vigentes
- ✓ Registrar devolución
- ✓ Estadísticas

---

## 💾 Ubicación de Archivos

```
Version_1/
├── database.sql      ← Script SQL (CREATE + INSERT)
├── db_setup.py       ← Funciones de inicialización
├── db_example.py     ← Ejemplos de uso
├── main.py           ← (Próximamente: integración con FastAPI)
└── biblioteca.db     ← BD SQLite (se genera automáticamente)
```

---

## 🔄 Flujo de Operaciones en la API

### Crear Préstamo
```
1. Validar estudiante existe
2. Validar libro existe
3. Verificar cantidad_disponible > 0
4. INSERT INTO prestamos (...)
5. UPDATE libros SET cantidad_disponible = cantidad_disponible - 1
```

### Registrar Devolución
```
1. Validar préstamo existe
2. UPDATE prestamos SET fecha_devolucion = NOW(), estado = 'devuelto'
3. UPDATE libros SET cantidad_disponible = cantidad_disponible + 1
```

### Consultar Vigentes
```
1. SELECT * FROM prestamos WHERE estado IN ('activo', 'vencido')
2. JOIN con estudiantes y libros para enriquecer datos
```

---

## ⚙️ Características de Diseño

### ✅ Simplicidad
- Solo 3 tablas (sin tablas de auditoría, estados, etc.)
- Foreign keys simples con CASCADE
- Sin vistas ni procedimientos almacenados

### ✅ Integridad
- Restricciones CHECK en estados
- UNIQUE en códigos e ISBNs
- Foreign keys con CASCADE DELETE

### ✅ Performance
- 4 índices estratégicos
- Queries optimizadas para casos de uso comunes
- Row factory para acceso por nombre de columna

### ✅ Flexibilidad
- Fácil de adaptar a Version_2 (con migraciones)
- Estructura preparada para agregar validaciones
- sin dependencias externas (solo sqlite3 estándar de Python)

---

## 📝 Notas Importantes

1. **Sin tabla de "ejemplares"** → Se simplificó usando `cantidad_disponible` en libros
2. **Sin tabla de "multas"** → Para versiones futuras
3. **Sin tabla de "usuarios" (admins)** → Version_1 es de solo lectura para estudiantes
4. **Timestamps en ISO format** → Compatible con JSON y FastAPI/Pydantic
5. **Row factory activo** → Las queries retornan diccionarios, no tuplas

---

## 🔗 Próximo Paso

Integrar esta BD con `main.py` (FastAPI):
- Reemplazar datos en memoria con consultas SQL
- Usar context managers para conexiones seguras
- Mantener la misma interfaz de endpoints
