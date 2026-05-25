#!/usr/bin/env python3
"""
ejecutar_pruebas_taller.py
Suite de validacion de reglas de negocio — Version_2 Biblioteca UCaldas

Prerequisito: servidor FastAPI corriendo en http://localhost:3001
    cd Version_2
    uvicorn main:app --reload --port 3001

Uso:
    python tests/ejecutar_pruebas_taller.py

Dependencia:
    pip install requests
"""
import sys
from datetime import date, timedelta

try:
    import requests
except ImportError:
    print("ERROR: La libreria 'requests' no esta instalada.")
    print("       Ejecuta: pip install requests")
    sys.exit(1)

BASE = "http://localhost:3001"

# ── Colores ANSI ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ── Contadores globales ───────────────────────────────────────────────────────
_passed = 0
_failed = 0


def ok(label: str, detail: str = "") -> None:
    global _passed
    _passed += 1
    suffix = f"  {CYAN}({detail}){RESET}" if detail else ""
    print(f"  {GREEN}PASO{RESET} ✅  {label}{suffix}")


def fail(label: str, reason: str) -> None:
    global _failed
    _failed += 1
    print(f"  {RED}FALLO{RESET} ❌  {label}")
    print(f"         {RED}Razon: {reason}{RESET}")


def seccion(titulo: str) -> None:
    print(f"\n{BOLD}{YELLOW}{'─' * 62}{RESET}")
    print(f"{BOLD}{YELLOW}  {titulo}{RESET}")
    print(f"{BOLD}{YELLOW}{'─' * 62}{RESET}")


# ── Helpers HTTP ─────────────────────────────────────────────────────────────

def post(path: str, body: dict) -> requests.Response:
    return requests.post(f"{BASE}{path}", json=body, timeout=5)


def put(path: str) -> requests.Response:
    return requests.put(f"{BASE}{path}", timeout=5)


def get(path: str) -> requests.Response:
    return requests.get(f"{BASE}{path}", timeout=5)


def devolver(prestamo_id: str) -> requests.Response:
    """Registra la devolucion de un prestamo activo (limpieza entre fases)."""
    return put(f"/api/prestamos/{prestamo_id}/devolucion")


# ─────────────────────────────────────────────────────────────────────────────
# PASO 0 — Health check
# ─────────────────────────────────────────────────────────────────────────────

def paso0_health() -> bool:
    seccion("PASO 0 — Verificacion del servidor")
    try:
        r = get("/")
        if r.status_code == 200 and r.json().get("status") == "ok":
            ok("Servidor responde correctamente",
               f"version={r.json().get('version')}")
            return True
        fail("Servidor no responde con status=ok",
             f"HTTP {r.status_code} — {r.text[:80]}")
        return False
    except requests.exceptions.ConnectionError:
        fail("No se puede conectar al servidor",
             "Asegurate de que 'uvicorn main:app --reload --port 3001' este corriendo")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# FASE 1 — Carga de datos de prueba
# ─────────────────────────────────────────────────────────────────────────────

def fase1_carga() -> bool:
    seccion("FASE 1 — Carga de datos de prueba (1.1 y 1.2)")
    todo_ok = True

    # 1.1 Estudiantes
    for payload, etiqueta in [
        (
            {"id": "EST-PRE-01", "nombre": "Ana Lopez",
             "programa": "Ingenieria de Sistemas", "semestre": 5,
             "tipo": "pregrado"},
            "EST-PRE-01 (pregrado, limite=3)",
        ),
        (
            {"id": "EST-POS-01", "nombre": "Carlos Rios",
             "programa": "Maestria en Software", "semestre": 2,
             "tipo": "posgrado"},
            "EST-POS-01 (posgrado, limite=5)",
        ),
    ]:
        r = post("/api/estudiantes", payload)
        if r.status_code == 201:
            ok(f"Crear estudiante {etiqueta}",
               f"limite_prestamos={r.json().get('limite_prestamos')}")
        elif r.status_code == 400 and "ya existe" in r.text.lower():
            ok(f"Estudiante {etiqueta}", "ya existia — datos validos")
        else:
            fail(f"Crear estudiante {etiqueta}",
                 f"HTTP {r.status_code} — {r.text[:80]}")
            todo_ok = False

    # 1.2 Libros
    for payload, etiqueta in [
        (
            {"id": "LIB-001", "titulo": "Ingenieria del Software",
             "autor": "Pressman", "sala": "Sala General",
             "alta_demanda": False},
            "LIB-001 normal (plazo 15 dias)",
        ),
        (
            {"id": "LIB-002", "titulo": "Clean Code",
             "autor": "Martin", "sala": "Sala de Reserva",
             "alta_demanda": True},
            "LIB-002 alta demanda (plazo 3 dias)",
        ),
    ]:
        r = post("/api/libros", payload)
        if r.status_code == 201:
            ok(f"Crear libro {etiqueta}",
               f"plazo_dias={r.json().get('plazo_dias')}")
        elif r.status_code == 400 and "ya existe" in r.text.lower():
            ok(f"Libro {etiqueta}", "ya existia — datos validos")
        else:
            fail(f"Crear libro {etiqueta}",
                 f"HTTP {r.status_code} — {r.text[:80]}")
            todo_ok = False

    # 1.3 Ejemplares de LIB-001 (6 piezas)
    creados = 0
    for i in range(1, 7):
        ej_id = f"EJ-001-{i:02d}"
        r = post("/api/libros/LIB-001/ejemplares", {"id": ej_id})
        if r.status_code == 201:
            creados += 1
        elif r.status_code == 400 and "ya existe" in r.text.lower():
            creados += 1
        else:
            fail(f"Crear ejemplar {ej_id}",
                 f"HTTP {r.status_code} — {r.text[:80]}")
            todo_ok = False
    if creados == 6:
        ok("Crear 6 ejemplares de LIB-001 (EJ-001-01 a EJ-001-06)",
           f"{creados}/6 disponibles")

    # 1.4 Ejemplar de LIB-002 (1 pieza)
    r = post("/api/libros/LIB-002/ejemplares", {"id": "EJ-002-01"})
    if r.status_code == 201:
        ok("Crear ejemplar EJ-002-01 para LIB-002")
    elif r.status_code == 400 and "ya existe" in r.text.lower():
        ok("Ejemplar EJ-002-01", "ya existia — datos validos")
    else:
        fail("Crear ejemplar EJ-002-01",
             f"HTTP {r.status_code} — {r.text[:80]}")
        todo_ok = False

    return todo_ok


# ─────────────────────────────────────────────────────────────────────────────
# RN1 — Pregrado: maximo 3 prestamos simultaneos
# ─────────────────────────────────────────────────────────────────────────────

def rn1_pregrado_max_3():
    seccion("RN1 — Pregrado: maximo 3 prestamos simultaneos")
    ids_creados = []

    # RN1-A: los tres primeros deben funcionar
    todos_201 = True
    for ej in ["EJ-001-01", "EJ-001-02", "EJ-001-03"]:
        r = post("/api/prestamos",
                 {"estudiante_id": "EST-PRE-01", "ejemplar_id": ej})
        if r.status_code == 201:
            ids_creados.append(r.json()["id"])
        else:
            fail(f"RN1-A: Prestamo de {ej} para pregrado",
                 f"HTTP {r.status_code} esperaba 201 — {r.text[:80]}")
            todos_201 = False
    if todos_201:
        ok("RN1-A: 3 prestamos simultaneos creados para pregrado", "201 x 3")

    # RN1-B: el cuarto debe fallar
    r = post("/api/prestamos",
             {"estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-04"})
    if r.status_code == 409:
        body = r.json()
        ok("RN1-B: 4to prestamo pregrado rechazado",
           f"409 error={body.get('error')} limite={body.get('limite')} "
           f"actuales={body.get('actuales')}")
    else:
        fail("RN1-B: 4to prestamo pregrado",
             f"HTTP {r.status_code} esperaba 409 — {r.text[:80]}")

    # Limpieza: devolver los 3 prestamos activos
    for pid in ids_creados:
        devolver(pid)


# ─────────────────────────────────────────────────────────────────────────────
# RN2 — Posgrado: maximo 5 prestamos simultaneos
# ─────────────────────────────────────────────────────────────────────────────

def rn2_posgrado_max_5():
    seccion("RN2 — Posgrado: maximo 5 prestamos simultaneos")
    ids_creados = []

    # RN2-A: los cinco primeros deben funcionar
    todos_201 = True
    for ej in ["EJ-001-01", "EJ-001-02", "EJ-001-03", "EJ-001-04", "EJ-001-05"]:
        r = post("/api/prestamos",
                 {"estudiante_id": "EST-POS-01", "ejemplar_id": ej})
        if r.status_code == 201:
            ids_creados.append(r.json()["id"])
        else:
            fail(f"RN2-A: Prestamo de {ej} para posgrado",
                 f"HTTP {r.status_code} esperaba 201 — {r.text[:80]}")
            todos_201 = False
    if todos_201:
        ok("RN2-A: 5 prestamos simultaneos creados para posgrado", "201 x 5")

    # RN2-B: el sexto debe fallar
    r = post("/api/prestamos",
             {"estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-001-06"})
    if r.status_code == 409:
        body = r.json()
        ok("RN2-B: 6to prestamo posgrado rechazado",
           f"409 error={body.get('error')} limite={body.get('limite')} "
           f"actuales={body.get('actuales')}")
    else:
        fail("RN2-B: 6to prestamo posgrado",
             f"HTTP {r.status_code} esperaba 409 — {r.text[:80]}")

    # Limpieza
    for pid in ids_creados:
        devolver(pid)


# ─────────────────────────────────────────────────────────────────────────────
# RN5 — Ejemplar ya prestado no puede prestarse de nuevo
# ─────────────────────────────────────────────────────────────────────────────

def rn5_ejemplar_ya_prestado():
    seccion("RN5 — Ejemplar ya prestado no puede prestarse de nuevo")

    # RN5-A: primer prestamo del ejemplar debe funcionar
    r = post("/api/prestamos",
             {"estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-002-01"})
    if r.status_code != 201:
        fail("RN5-A: Primer prestamo de EJ-002-01",
             f"HTTP {r.status_code} esperaba 201 — {r.text[:80]}")
        return
    prestamo_id = r.json()["id"]
    ok("RN5-A: Primer prestamo de EJ-002-01 creado", "201 Created")

    # RN5-B: segundo prestamo del mismo ejemplar debe fallar
    r = post("/api/prestamos",
             {"estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-002-01"})
    if r.status_code == 409:
        ok("RN5-B: Segundo prestamo de EJ-002-01 rechazado",
           f"409 error={r.json().get('error')}")
    else:
        fail("RN5-B: Segundo prestamo de EJ-002-01",
             f"HTTP {r.status_code} esperaba 409 — {r.text[:80]}")

    # Limpieza
    devolver(prestamo_id)


# ─────────────────────────────────────────────────────────────────────────────
# RN6 — Plazo segun tipo de libro (15 dias / 3 dias)
# ─────────────────────────────────────────────────────────────────────────────

def rn6_plazos():
    seccion("RN6 — Plazo de prestamo segun tipo de libro")
    hoy = date.today()
    ids_para_devolver = []

    # RN6-A: libro normal → plazo 15 dias
    r = post("/api/prestamos",
             {"estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"})
    if r.status_code == 201:
        ids_para_devolver.append(r.json()["id"])
        fecha_esperada = (hoy + timedelta(days=15)).isoformat()
        fecha_real     = r.json().get("fecha_devolucion_esperada", "")
        if fecha_real == fecha_esperada:
            ok("RN6-A: Plazo libro normal = 15 dias",
               f"fecha_devolucion_esperada={fecha_real}")
        else:
            fail("RN6-A: Plazo libro normal",
                 f"esperaba {fecha_esperada}, obtuvo {fecha_real}")
    else:
        fail("RN6-A: Crear prestamo de libro normal",
             f"HTTP {r.status_code} — {r.text[:80]}")

    # RN6-B: libro alta demanda → plazo 3 dias
    r = post("/api/prestamos",
             {"estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-002-01"})
    if r.status_code == 201:
        ids_para_devolver.append(r.json()["id"])
        fecha_esperada = (hoy + timedelta(days=3)).isoformat()
        fecha_real     = r.json().get("fecha_devolucion_esperada", "")
        if fecha_real == fecha_esperada:
            ok("RN6-B: Plazo libro alta demanda = 3 dias",
               f"fecha_devolucion_esperada={fecha_real}")
        else:
            fail("RN6-B: Plazo libro alta demanda",
                 f"esperaba {fecha_esperada}, obtuvo {fecha_real}")
    else:
        fail("RN6-B: Crear prestamo de libro alta demanda",
             f"HTTP {r.status_code} — {r.text[:80]}")

    # Limpieza
    for pid in ids_para_devolver:
        devolver(pid)


# ─────────────────────────────────────────────────────────────────────────────
# RN3 — Prestamo vencido bloquea nuevos prestamos
# (inyectamos fecha_prestamo pasada — Opcion A disponible en Version_2)
# ─────────────────────────────────────────────────────────────────────────────

def rn3_vencido_bloquea() -> str | None:
    seccion("RN3 — Prestamo vencido bloquea nuevos prestamos")

    # Crear prestamo con fecha antigua → quedara vencido
    r = post("/api/prestamos", {
        "estudiante_id": "EST-PRE-01",
        "ejemplar_id":   "EJ-001-01",
        "fecha_prestamo": "2025-01-01",
    })
    if r.status_code != 201:
        fail("RN3-setup: Crear prestamo vencido con fecha_prestamo=2025-01-01",
             f"HTTP {r.status_code} — {r.text[:80]}")
        return None

    prestamo_vencido_id = r.json()["id"]
    fecha_dev = r.json().get("fecha_devolucion_esperada", "")
    ok("RN3-setup: Prestamo con fecha_prestamo=2025-01-01 creado",
       f"fecha_devolucion_esperada={fecha_dev} (ya vencida)")

    # Intentar otro prestamo para el mismo estudiante (debe fallar)
    r = post("/api/prestamos",
             {"estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-02"})
    if r.status_code == 409:
        ok("RN3: Nuevo prestamo bloqueado por vencido pendiente",
           f"409 error={r.json().get('error')}")
    else:
        fail("RN3: Prestamo con vencido pendiente",
             f"HTTP {r.status_code} esperaba 409 — {r.text[:80]}")

    # Retornamos el ID para que RN4 lo use (la devolucion genera la multa)
    return prestamo_vencido_id


# ─────────────────────────────────────────────────────────────────────────────
# RN4 — Multa pendiente bloquea nuevos prestamos
# (usa la multa generada al devolver el prestamo vencido de RN3)
# ─────────────────────────────────────────────────────────────────────────────

def rn4_multa_bloquea(prestamo_vencido_id: str | None):
    seccion("RN4 — Multa pendiente bloquea nuevos prestamos")

    if not prestamo_vencido_id:
        fail("RN4: Omitido", "RN3 no genero prestamo vencido — revisar RN3")
        return

    # Devolver el prestamo vencido → genera multa automaticamente
    r = devolver(prestamo_vencido_id)
    if r.status_code == 200:
        dias   = r.json().get("dias_retraso", 0)
        multa  = r.json().get("multa")
        monto  = multa.get("monto", 0) if multa else 0
        if multa and monto > 0:
            ok("RN4-setup: Devolucion tardia genero multa",
               f"{dias} dias de retraso → ${monto:,} COP pendiente")
        else:
            fail("RN4-setup: Devolucion tardia no genero multa",
                 f"dias_retraso={dias}, multa={multa}")
            return
    else:
        fail("RN4-setup: Registrar devolucion",
             f"HTTP {r.status_code} — {r.text[:80]}")
        return

    # Intentar nuevo prestamo con multa pendiente (debe fallar)
    r = post("/api/prestamos",
             {"estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"})
    if r.status_code == 409:
        body = r.json()
        ok("RN4: Nuevo prestamo bloqueado por multa pendiente",
           f"409 error={body.get('error')} "
           f"monto_total=${body.get('monto_total', '?')}")
    else:
        fail("RN4: Prestamo con multa pendiente",
             f"HTTP {r.status_code} esperaba 409 — {r.text[:80]}")


# ─────────────────────────────────────────────────────────────────────────────
# RN8 — Calculo de multa por devolucion tardia (2.000 COP / dia)
# ─────────────────────────────────────────────────────────────────────────────

def rn8_calculo_multa():
    seccion("RN8 — Calculo de multa por devolucion tardia")

    # Simular retraso de exactamente 5 dias:
    # LIB-001 tiene plazo 15 dias → fecha_prestamo = hoy - 20 dias
    # → fecha_devolucion_esperada = hoy - 5 dias → retraso = 5 dias
    hoy = date.today()
    fecha_prestamo_simulada = (hoy - timedelta(days=20)).isoformat()

    r = post("/api/prestamos", {
        "estudiante_id": "EST-POS-01",
        "ejemplar_id":   "EJ-001-01",
        "fecha_prestamo": fecha_prestamo_simulada,
    })
    if r.status_code != 201:
        fail("RN8-setup: Crear prestamo con retraso de 5 dias",
             f"HTTP {r.status_code} — {r.text[:80]}")
        return

    prestamo_id = r.json()["id"]
    fecha_dev_esp = r.json().get("fecha_devolucion_esperada", "")
    ok("RN8-setup: Prestamo con 5 dias de retraso creado",
       f"fecha_devolucion_esperada={fecha_dev_esp}")

    # Registrar devolucion hoy → debe calcular 5 dias y multa de 10.000
    r = devolver(prestamo_id)
    if r.status_code == 200:
        dias_real  = r.json().get("dias_retraso", -1)
        multa      = r.json().get("multa")
        monto_real = multa.get("monto", 0) if multa else 0
        monto_esp  = 5 * 2_000

        if dias_real == 5 and monto_real == monto_esp:
            ok("RN8: Multa calculada correctamente",
               f"5 dias x $2.000 = ${monto_real:,} COP")
        else:
            fail("RN8: Calculo de multa incorrecto",
                 f"dias_retraso={dias_real} (esperaba 5), "
                 f"monto=${monto_real} (esperaba ${monto_esp})")
    else:
        fail("RN8: Registrar devolucion",
             f"HTTP {r.status_code} — {r.text[:80]}")


# ─────────────────────────────────────────────────────────────────────────────
# VAL — Validaciones de entradas invalidas
# ─────────────────────────────────────────────────────────────────────────────

def val_validaciones():
    seccion("VAL — Validaciones de entradas invalidas")

    # VAL-1: body vacio → FastAPI/Pydantic retorna 422 (no 400)
    r = post("/api/prestamos", {})
    if r.status_code in (400, 422):
        ok("VAL-1: Body vacio rechazado",
           f"HTTP {r.status_code} {'(FastAPI/Pydantic standard)' if r.status_code == 422 else ''}")
    else:
        fail("VAL-1: Body vacio",
             f"HTTP {r.status_code} esperaba 422 — {r.text[:60]}")

    # VAL-2: estudiante inexistente → 404
    r = post("/api/prestamos",
             {"estudiante_id": "NO-EXISTE-999", "ejemplar_id": "EJ-001-01"})
    if r.status_code == 404:
        ok("VAL-2: Estudiante inexistente → 404",
           r.json().get("error", ""))
    else:
        fail("VAL-2: Estudiante inexistente",
             f"HTTP {r.status_code} esperaba 404 — {r.text[:60]}")

    # VAL-3: ejemplar inexistente → 404
    # Nota: el orden de validacion en CrearPrestamo es estudiante → ejemplar,
    # por lo que EjemplarNoEncontrado se lanza antes del check de multa.
    r = post("/api/prestamos",
             {"estudiante_id": "EST-POS-01", "ejemplar_id": "NO-EXISTE-999"})
    if r.status_code == 404:
        ok("VAL-3: Ejemplar inexistente → 404",
           r.json().get("error", ""))
    else:
        fail("VAL-3: Ejemplar inexistente",
             f"HTTP {r.status_code} esperaba 404 — {r.text[:60]}")

    # VAL-5: historial de estudiante inexistente → 404
    r = get("/api/estudiantes/NO-EXISTE-999/historial")
    if r.status_code == 404:
        ok("VAL-5: Historial de estudiante inexistente → 404",
           r.json().get("error", ""))
    else:
        fail("VAL-5: Historial inexistente",
             f"HTTP {r.status_code} esperaba 404 — {r.text[:60]}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{BOLD}{'=' * 62}{RESET}")
    print(f"{BOLD}  Suite de Validacion — Biblioteca UCaldas Version_2{RESET}")
    print(f"{BOLD}  Objetivo: {BASE}{RESET}")
    print(f"{BOLD}{'=' * 62}{RESET}")

    # Paso 0: conectividad
    if not paso0_health():
        print(f"\n{RED}Servidor no disponible. Abortando.{RESET}")
        sys.exit(1)

    # Fase 1: datos de prueba
    fase1_carga()

    # Fase 2: reglas de negocio
    # IMPORTANTE: el orden importa porque los tests comparten la BD.
    # Cada funcion limpia sus prestamos al terminar.
    rn1_pregrado_max_3()
    rn2_posgrado_max_5()
    rn5_ejemplar_ya_prestado()
    rn6_plazos()
    prestamo_vencido_id = rn3_vencido_bloquea()   # devolucion genera multa para RN4
    rn4_multa_bloquea(prestamo_vencido_id)
    rn8_calculo_multa()
    val_validaciones()

    # Resumen final
    total = _passed + _failed
    print(f"\n{BOLD}{'=' * 62}{RESET}")
    print(f"{BOLD}  RESUMEN FINAL{RESET}")
    print(f"{BOLD}{'=' * 62}{RESET}")
    print(f"  Verificaciones totales : {total}")
    print(f"  {GREEN}Pasaron  : {_passed}{RESET}")
    print(f"  {RED}Fallaron : {_failed}{RESET}")
    if _failed == 0:
        print(f"\n  {GREEN}{BOLD}Todas las reglas de negocio validadas correctamente.{RESET}")
    else:
        print(f"\n  {RED}{BOLD}Hay {_failed} verificacion(es) fallidas. Revisar arriba.{RESET}")
    print(f"{BOLD}{'=' * 62}{RESET}\n")

    sys.exit(0 if _failed == 0 else 1)


if __name__ == "__main__":
    main()
