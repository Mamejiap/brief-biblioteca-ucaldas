"""
Tests de integracion - flujos end-to-end via TestClient de FastAPI.
"""
import pytest
from fastapi.testclient import TestClient

from main import app
from app.api import dependencies
from app.infrastructure.repositories.in_memory_libro_repository import (
    InMemoryLibroRepository, InMemoryEjemplarRepository
)
from app.infrastructure.repositories.in_memory_estudiante_repository import (
    InMemoryEstudianteRepository
)
from app.infrastructure.repositories.in_memory_prestamo_repository import (
    InMemoryPrestamoRepository
)
from app.infrastructure.repositories.in_memory_multa_repository import (
    InMemoryMultaRepository
)
from app.infrastructure.repositories.in_memory_reserva_repository import (
    InMemoryReservaRepository
)


@pytest.fixture(autouse=True)
def reset_repos():
    """Reinicia los repositorios en memoria antes de cada test."""
    dependencies._libro_repo = InMemoryLibroRepository()
    dependencies._ejemplar_repo = InMemoryEjemplarRepository()
    dependencies._estudiante_repo = InMemoryEstudianteRepository()
    dependencies._prestamo_repo = InMemoryPrestamoRepository()
    dependencies._multa_repo = InMemoryMultaRepository()
    dependencies._reserva_repo = InMemoryReservaRepository()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def datos_base(client):
    client.post("/api/estudiantes", json={"id": "EST-PRE-01", "nombre": "Ana Lopez",
        "programa": "Ing. Sistemas", "semestre": 5, "tipo": "pregrado"})
    client.post("/api/estudiantes", json={"id": "EST-POS-01", "nombre": "Carlos Rios",
        "programa": "Maestria", "semestre": 2, "tipo": "posgrado"})
    client.post("/api/libros", json={"id": "LIB-001", "titulo": "Ingenieria del Software",
        "autor": "Pressman", "sala": "General", "alta_demanda": False})
    client.post("/api/libros", json={"id": "LIB-002", "titulo": "Clean Code",
        "autor": "Martin", "sala": "Reserva", "alta_demanda": True})
    for i in range(1, 7):
        client.post("/api/libros/LIB-001/ejemplares", json={"id": f"EJ-001-{i:02d}"})
    client.post("/api/libros/LIB-002/ejemplares", json={"id": "EJ-002-01"})


class TestHealthCheck:
    def test_root_devuelve_200(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestLibros:
    def test_crear_libro(self, client):
        r = client.post("/api/libros", json={"id": "LIB-X", "titulo": "Test",
            "autor": "Autor", "sala": "A", "alta_demanda": False})
        assert r.status_code == 201
        assert r.json()["plazo_dias"] == 15

    def test_libro_alta_demanda_plazo_3(self, client):
        r = client.post("/api/libros", json={"id": "LIB-AD", "titulo": "AD",
            "autor": "X", "sala": "R", "alta_demanda": True})
        assert r.status_code == 201
        assert r.json()["plazo_dias"] == 3

    def test_crear_libro_duplicado_da_400(self, client, datos_base):
        r = client.post("/api/libros", json={"id": "LIB-001", "titulo": "X",
            "autor": "Y", "sala": "Z", "alta_demanda": False})
        assert r.status_code == 400

    def test_libro_inexistente_da_404(self, client):
        r = client.get("/api/libros/NO-EXISTE")
        assert r.status_code == 404


class TestEstudiantes:
    def test_crear_estudiante(self, client):
        r = client.post("/api/estudiantes", json={"id": "EST-1", "nombre": "X",
            "programa": "P", "semestre": 1, "tipo": "pregrado"})
        assert r.status_code == 201
        assert r.json()["limite_prestamos"] == 3

    def test_posgrado_limite_5(self, client):
        r = client.post("/api/estudiantes", json={"id": "EST-2", "nombre": "Y",
            "programa": "P", "semestre": 1, "tipo": "posgrado"})
        assert r.status_code == 201
        assert r.json()["limite_prestamos"] == 5

    def test_estudiante_inexistente_da_404(self, client):
        r = client.get("/api/estudiantes/NO-EXISTE")
        assert r.status_code == 404


class TestCrearPrestamo:
    def test_prestamo_exitoso(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"
        })
        assert r.status_code == 201
        assert r.json()["estado"] == "activo"

    def test_rn1_cuarto_prestamo_pregrado_da_409(self, client, datos_base):
        for i in range(1, 4):
            client.post("/api/prestamos", json={
                "estudiante_id": "EST-PRE-01", "ejemplar_id": f"EJ-001-{i:02d}"
            })
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-04"
        })
        assert r.status_code == 409
        assert r.json()["error"] == "limite_prestamos_alcanzado"
        assert r.json()["limite"] == 3

    def test_rn2_sexto_prestamo_posgrado_da_409(self, client, datos_base):
        for i in range(1, 6):
            client.post("/api/prestamos", json={
                "estudiante_id": "EST-POS-01", "ejemplar_id": f"EJ-001-{i:02d}"
            })
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-001-06"
        })
        assert r.status_code == 409
        assert r.json()["error"] == "limite_prestamos_alcanzado"
        assert r.json()["limite"] == 5

    def test_rn5_ejemplar_ya_prestado_da_409(self, client, datos_base):
        client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"
        })
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-001-01"
        })
        assert r.status_code == 409
        assert r.json()["error"] == "ejemplar_no_disponible"

    def test_rn6_plazo_libro_normal_15_dias(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"
        })
        assert r.status_code == 201
        from datetime import date, timedelta
        esperada = (date.today() + timedelta(days=15)).isoformat()
        assert r.json()["fecha_devolucion_esperada"] == esperada

    def test_rn6_plazo_alta_demanda_3_dias(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-002-01"
        })
        assert r.status_code == 201
        from datetime import date, timedelta
        esperada = (date.today() + timedelta(days=3)).isoformat()
        assert r.json()["fecha_devolucion_esperada"] == esperada

    def test_estudiante_inexistente_da_404(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "NO-EXISTE", "ejemplar_id": "EJ-001-01"
        })
        assert r.status_code == 404

    def test_body_vacio_da_422(self, client):
        r = client.post("/api/prestamos", json={})
        assert r.status_code == 422


class TestDevolucion:
    def test_rn8_devolucion_sin_retraso(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"
        })
        pid = r.json()["id"]
        r2 = client.put(f"/api/prestamos/{pid}/devolucion")
        assert r2.status_code == 200
        assert r2.json()["dias_retraso"] == 0
        assert r2.json()["multa"] is None

    def test_devolucion_libera_ejemplar(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"
        })
        pid = r.json()["id"]
        client.put(f"/api/prestamos/{pid}/devolucion")
        r2 = client.post("/api/prestamos", json={
            "estudiante_id": "EST-POS-01", "ejemplar_id": "EJ-001-01"
        })
        assert r2.status_code == 201


class TestReservas:
    def test_rn7_renovacion_bloqueada_por_reserva(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"
        })
        pid = r.json()["id"]
        client.post("/api/reservas", json={
            "estudiante_id": "EST-POS-01", "libro_id": "LIB-001"
        })
        r2 = client.put(f"/api/prestamos/{pid}/renovar")
        assert r2.status_code == 409
        assert r2.json()["error"] == "renovacion_bloqueada_por_reserva"

    def test_renovacion_exitosa_sin_lista_de_espera(self, client, datos_base):
        r = client.post("/api/prestamos", json={
            "estudiante_id": "EST-PRE-01", "ejemplar_id": "EJ-001-01"
        })
        pid = r.json()["id"]
        r2 = client.put(f"/api/prestamos/{pid}/renovar")
        assert r2.status_code == 200

    def test_cancelar_reserva(self, client, datos_base):
        r = client.post("/api/reservas", json={
            "estudiante_id": "EST-POS-01", "libro_id": "LIB-001"
        })
        rid = r.json()["id"]
        assert r.status_code == 201
        r2 = client.delete(f"/api/reservas/{rid}")
        assert r2.status_code == 204
