"""
db_setup.py - Inicialización y setup de la Base de Datos SQLite
Versión 1 - API Biblioteca UCaldas

Propósito: Centralizar la lógica de inicialización de la BD
uso: from db_setup import init_db; init_db()
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

# Ubicación de la BD (en el mismo directorio que este archivo)
DB_PATH = Path(__file__).parent / "biblioteca.db"
SCHEMA_PATH = Path(__file__).parent / "database.sql"


def init_db():
    """
    Inicializa la base de datos SQLite.
    - Crea las tablas si no existen
    - Carga los datos iniciales (seed)
    - Retorna True si se creó nueva, False si ya existía
    """
    db_exists = DB_PATH.exists()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Leer y ejecutar el script SQL
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                sql_script = f.read()
                cursor.executescript(sql_script)

            conn.commit()

            if not db_exists:
                print(f"✓ Base de datos creada en: {DB_PATH}")
                print("✓ Tablas e índices creados")
                print("✓ Datos iniciales cargados")
                return True
            else:
                print(f"✓ Base de datos existente: {DB_PATH}")
                return False

    except sqlite3.Error as e:
        print(f"✗ Error al inicializar BD: {e}")
        raise
    except FileNotFoundError as e:
        print(f"✗ Archivo {SCHEMA_PATH} no encontrado: {e}")
        raise


@contextmanager
def get_db():
    """
    Context manager para manejar conexiones a la BD de forma segura.

    Uso:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM libros")
            libros = cursor.fetchall()
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    try:
        yield conn
    finally:
        conn.close()


def get_connection():
    """
    Obtiene una conexión directa a la BD (sin context manager).
    Nota: Es preferible usar get_db() para evitar memory leaks.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# HELPERS - Funciones útiles para acceso a datos
# ============================================================

def get_all_estudiantes():
    """Obtiene todos los estudiantes"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudiantes ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]


def get_all_libros():
    """Obtiene todos los libros"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM libros ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]


def get_all_prestamos():
    """Obtiene todos los préstamos"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prestamos ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]


def get_prestamos_vigentes():
    """Obtiene préstamos activos o vencidos (no devueltos)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, e.nombre, e.codigo_est, l.titulo
            FROM prestamos p
            JOIN estudiantes e ON p.estudiante_id = e.id
            JOIN libros l ON p.libro_id = l.id
            WHERE p.estado IN ('activo', 'vencido')
            ORDER BY p.fecha_vencimiento
        """)
        return [dict(row) for row in cursor.fetchall()]


def reset_db():
    """
    Elimina la base de datos y la reinicializa.
    ADVERTENCIA: Esta operación es destructiva.
    """
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"✓ Base de datos eliminada: {DB_PATH}")

    init_db()
    print("✓ Base de datos reinicializada")


if __name__ == "__main__":
    # Script de prueba: inicializar BD
    print("\n" + "=" * 50)
    print("Inicializando Base de Datos...")
    print("=" * 50)

    init_db()

    print("\nEstudiantes:")
    for est in get_all_estudiantes():
        print(f"  - {est['codigo_est']}: {est['nombre']}")

    print("\nLibros:")
    for lib in get_all_libros():
        print(f"  - {lib['titulo']} ({lib['cantidad_disponible']}/{lib['cantidad_total']})")

    print("\n" + "=" * 50)
    print("✓ Setup completado\n")
