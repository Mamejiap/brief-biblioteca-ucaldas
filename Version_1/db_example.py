"""
db_example.py - Ejemplos de uso de la Base de Datos SQLite
Versión 1 - API Biblioteca UCaldas

Propósito: Mostrar cómo consumir la BD desde Python
Uso: python db_example.py
"""

from db_setup import (
    init_db,
    get_db,
    get_all_estudiantes,
    get_all_libros,
    get_all_prestamos,
    get_prestamos_vigentes,
)
from datetime import datetime, timedelta


def ejemplo_1_operaciones_basicas():
    """Ejemplo 1: Operaciones CRUD básicas"""
    print("\n" + "=" * 60)
    print("EJEMPLO 1: Operaciones CRUD Básicas")
    print("=" * 60)

    # CREATE: Insertar un nuevo estudiante
    print("\n[CREATE] Insertando nuevo estudiante...")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO estudiantes (codigo_est, nombre, email, carrera) VALUES (?, ?, ?, ?)",
            ("EST-004", "Diana Rodríguez", "diana.rodriguez@ucaldas.edu.co", "Ingeniería Industrial"),
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        print(f"✓ Estudiante creado con ID: {nuevo_id}")

    # READ: Obtener todos los estudiantes
    print("\n[READ] Obteniendo todos los estudiantes...")
    estudiantes = get_all_estudiantes()
    for est in estudiantes:
        print(f"  ID {est['id']}: {est['codigo_est']} - {est['nombre']}")

    # UPDATE: Actualizar un estudiante
    print("\n[UPDATE] Actualizando email de EST-001...")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE estudiantes SET email = ? WHERE codigo_est = ?",
            ("juan.p@ucaldas.edu.co", "EST-001"),
        )
        conn.commit()
        print(f"✓ Registros actualizados: {cursor.rowcount}")

    # DELETE: Eliminar un estudiante (cascada automática)
    print("\n[DELETE] Eliminando EST-004...")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estudiantes WHERE codigo_est = ?", ("EST-004",))
        conn.commit()
        print(f"✓ Registros eliminados: {cursor.rowcount}")


def ejemplo_2_creacion_prestamo():
    """Ejemplo 2: Crear un préstamo y actualizar disponibilidad"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Crear un Préstamo")
    print("=" * 60)

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Verificar disponibilidad
        print("\n[PASO 1] Verificando disponibilidad del libro...")
        cursor.execute("SELECT * FROM libros WHERE id = 1")
        libro = cursor.fetchone()
        print(f"  Libro: {libro['titulo']}")
        print(f"  Disponibles: {libro['cantidad_disponible']}")

        if libro["cantidad_disponible"] > 0:
            # 2. Crear préstamo
            print("\n[PASO 2] Creando préstamo...")
            fecha_vencimiento = datetime.now() + timedelta(days=14)
            cursor.execute(
                """
                INSERT INTO prestamos 
                (estudiante_id, libro_id, fecha_vencimiento, estado) 
                VALUES (?, ?, ?, ?)
                """,
                (1, 1, fecha_vencimiento.isoformat(), "activo"),
            )

            # 3. Decrementar disponibles
            print("[PASO 3] Actualizando cantidad disponible...")
            cursor.execute(
                "UPDATE libros SET cantidad_disponible = cantidad_disponible - 1 WHERE id = ?",
                (1,),
            )

            conn.commit()

            prestamo_id = cursor.lastrowid
            print(f"✓ Préstamo creado con ID: {prestamo_id}")
            print(f"✓ Disponibles ahora: {libro['cantidad_disponible'] - 1}")
        else:
            print("✗ No hay ejemplares disponibles")


def ejemplo_3_consultar_vigentes():
    """Ejemplo 3: Consultar préstamos vigentes con detalles"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Consultar Préstamos Vigentes")
    print("=" * 60)

    print("\nPréstamos vigentes (activos o vencidos):")
    vigentes = get_prestamos_vigentes()

    if vigentes:
        for p in vigentes:
            print(f"\n  ID: {p['id']}")
            print(f"  Estudiante: {p['codigo_est']} - {p['nombre']}")
            print(f"  Libro: {p['titulo']}")
            print(f"  Prestado: {p['fecha_prestamo']}")
            print(f"  Vence: {p['fecha_vencimiento']}")
            print(f"  Estado: {p['estado']}")
    else:
        print("  (Ninguno)")


def ejemplo_4_registrar_devolucion():
    """Ejemplo 4: Registrar devolución de un préstamo"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Registrar Devolución")
    print("=" * 60)

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Obtener un préstamo vigente
        print("\n[PASO 1] Buscando préstamo vigente...")
        cursor.execute(
            "SELECT * FROM prestamos WHERE estado = 'activo' LIMIT 1"
        )
        prestamo = cursor.fetchone()

        if prestamo:
            prestamo_id = prestamo["id"]
            libro_id = prestamo["libro_id"]

            # 2. Actualizar préstamo
            print(f"\n[PASO 2] Registrando devolución del préstamo {prestamo_id}...")
            cursor.execute(
                """
                UPDATE prestamos 
                SET fecha_devolucion = ?, estado = 'devuelto'
                WHERE id = ?
                """,
                (datetime.now().isoformat(), prestamo_id),
            )

            # 3. Incrementar disponibles
            print("[PASO 3] Incrementando disponibles del libro...")
            cursor.execute(
                "UPDATE libros SET cantidad_disponible = cantidad_disponible + 1 WHERE id = ?",
                (libro_id,),
            )

            conn.commit()
            print(f"✓ Devolución registrada")
        else:
            print("No hay préstamos vigentes")


def ejemplo_5_estadisticas():
    """Ejemplo 5: Obtener estadísticas de la BD"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Estadísticas de la Biblioteca")
    print("=" * 60)

    with get_db() as conn:
        cursor = conn.cursor()

        # Estadísticas de estudiantes
        cursor.execute("SELECT COUNT(*) as total FROM estudiantes")
        total_est = cursor.fetchone()["total"]

        # Estadísticas de libros
        cursor.execute(
            "SELECT SUM(cantidad_disponible) as disponibles, SUM(cantidad_total) as total FROM libros"
        )
        stats_libros = cursor.fetchone()

        # Estadísticas de préstamos
        cursor.execute(
            "SELECT estado, COUNT(*) as cantidad FROM prestamos GROUP BY estado"
        )
        stats_prestamos = cursor.fetchall()

        print(f"\nEstudiantes registrados: {total_est}")
        print(f"Libros disponibles: {stats_libros['disponibles']}/{stats_libros['total']}")
        print(f"\nPréstamos por estado:")
        for s in stats_prestamos:
            print(f"  - {s['estado']}: {s['cantidad']}")


def main():
    """Ejecuta todos los ejemplos"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║ EJEMPLOS DE USO - Base de Datos SQLite v1             ║")
    print("║ API Biblioteca UCaldas                                ║")
    print("╚════════════════════════════════════════════════════════╝")

    # Inicializar BD
    print("\n[SETUP] Inicializando base de datos...")
    init_db()

    # Ejecutar ejemplos
    try:
        ejemplo_1_operaciones_basicas()
        ejemplo_2_creacion_prestamo()
        ejemplo_3_consultar_vigentes()
        ejemplo_4_registrar_devolucion()
        ejemplo_5_estadisticas()
    except Exception as e:
        print(f"\n✗ Error durante los ejemplos: {e}")
        raise

    print("\n" + "=" * 60)
    print("✓ Todos los ejemplos completados")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
