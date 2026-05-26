-- ============================================================
-- DATABASE SCHEMA - API Biblioteca UCaldas v1 (SQLite)
-- ============================================================
-- Diseño simple y directo para Version_1 de la API
-- ============================================================

-- Tabla de Estudiantes
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_est TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL,
    carrera TEXT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Libros (cantidad_disponible se actualiza con cada préstamo/devolución)
CREATE TABLE IF NOT EXISTS libros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    cantidad_disponible INTEGER NOT NULL,
    cantidad_total INTEGER NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Préstamos
CREATE TABLE IF NOT EXISTS prestamos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL,
    libro_id INTEGER NOT NULL,
    fecha_prestamo DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATETIME NOT NULL,
    fecha_devolucion DATETIME,
    estado TEXT NOT NULL CHECK(estado IN ('activo', 'vencido', 'devuelto')),
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id) ON DELETE CASCADE,
    FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE CASCADE
);

-- ============================================================
-- ÍNDICES (para optimizar queries frecuentes)
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_prestamos_estudiante ON prestamos(estudiante_id);
CREATE INDEX IF NOT EXISTS idx_prestamos_libro ON prestamos(libro_id);
CREATE INDEX IF NOT EXISTS idx_prestamos_estado ON prestamos(estado);
CREATE INDEX IF NOT EXISTS idx_estudiantes_codigo ON estudiantes(codigo_est);

-- ============================================================
-- DATOS INICIALES (SEED)
-- ============================================================

-- Estudiantes de prueba
INSERT OR IGNORE INTO estudiantes (codigo_est, nombre, email, carrera) VALUES
('EST-001', 'Juan Pérez', 'juan.perez@ucaldas.edu.co', 'Ingeniería de Sistemas'),
('EST-002', 'María García', 'maria.garcia@ucaldas.edu.co', 'Ingeniería de Sistemas'),
('EST-003', 'Carlos López', 'carlos.lopez@ucaldas.edu.co', 'Administración de Empresas');

-- Libros de prueba (cantidad_disponible = cantidad_total inicialmente)
INSERT OR IGNORE INTO libros (titulo, autor, isbn, cantidad_disponible, cantidad_total) VALUES
('Clean Code', 'Robert C. Martin', '978-0132350884', 3, 5),
('Design Patterns', 'Gang of Four', '978-0201633610', 2, 3),
('The Pragmatic Programmer', 'Hunt & Thomas', '978-0135957059', 4, 4);

-- Préstamos de ejemplo (opcional - comentar si no se desea)
-- INSERT OR IGNORE INTO prestamos (estudiante_id, libro_id, fecha_prestamo, fecha_vencimiento, estado)
-- VALUES (1, 1, datetime('now'), datetime('now', '+14 days'), 'activo');
