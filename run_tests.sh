#!/bin/bash

export BASE_SIN_IA="http://localhost:8000"

echo "======================================================================"
echo "PREPARACION: Crear libros y ejemplares"
echo "======================================================================"

# Libro normal (plazo 15 dias)
echo -e "\n[1/2] Creando libro normal..."
curl -s -X POST $BASE_SIN_IA/libros \
  -H "Content-Type: application/json" \
  -d '{
    "id": "LIB-001",
    "titulo": "Ingenieria del Software",
    "autor": "Pressman",
    "sala": "Sala General",
    "altaDemanda": false
  }' | jq . || echo "Error creando LIB-001"

# Libro de alta demanda (plazo 3 dias)
echo -e "\n[2/2] Creando libro alta demanda..."
curl -s -X POST $BASE_SIN_IA/libros \
  -H "Content-Type: application/json" \
  -d '{
    "id": "LIB-002",
    "titulo": "Clean Code",
    "autor": "Martin",
    "sala": "Sala de Reserva",
    "altaDemanda": true
  }' | jq . || echo "Error creando LIB-002"

echo -e "\n======================================================================"
echo "PREPARACION: Crear ejemplares"
echo "======================================================================"

# Ejemplares del libro normal (EJ-001-01 a EJ-001-06)
for i in 01 02 03 04 05 06; do
  echo "[${i}] Creando EJ-001-${i}..."
  curl -s -X POST $BASE_SIN_IA/libros/LIB-001/ejemplares \
    -H "Content-Type: application/json" \
    -d "{\"id\": \"EJ-001-$i\"}" | jq . || echo "Error creando EJ-001-${i}"
done

# Ejemplar del libro de alta demanda
echo "[01] Creando EJ-002-01..."
curl -s -X POST $BASE_SIN_IA/libros/LIB-002/ejemplares \
  -H "Content-Type: application/json" \
  -d '{"id": "EJ-002-01"}' | jq . || echo "Error creando EJ-002-01"

echo -e "\n======================================================================"
echo "PREPARACION: Crear estudiantes"
echo "======================================================================"

# Estudiante de pregrado
echo -e "\n[1/2] Creando estudiante pregrado..."
curl -s -X POST $BASE_SIN_IA/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EST-PRE-01",
    "nombre": "Ana Lopez",
    "programa": "Ingenieria de Sistemas",
    "semestre": 5,
    "tipo": "pregrado"
  }' | jq . || echo "Error creando EST-PRE-01"

# Estudiante de posgrado
echo -e "\n[2/2] Creando estudiante posgrado..."
curl -s -X POST $BASE_SIN_IA/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "EST-POS-01",
    "nombre": "Carlos Rios",
    "programa": "Maestria en Software",
    "semestre": 2,
    "tipo": "posgrado"
  }' | jq . || echo "Error creando EST-POS-01"

echo -e "\n======================================================================"
echo "PRUEBA RN2-B: Sexto prestamo posgrado (debe fallar con 409)"
echo "======================================================================"

echo -e "\nPreparando: Crear 5 prestamos exitosos para el estudiante posgrado..."
for i in 01 02 03 04 05; do
  curl -s -X POST $BASE_SIN_IA/prestamos \
    -H "Content-Type: application/json" \
    -d "{\"estudianteId\": \"EST-POS-01\", \"ejemplarId\": \"EJ-001-0$i\"}" | jq . || echo "Error prestamo $i"
done

echo -e "\nEjecutando RN2-B: Intentar sexto prestamo (debe ser 409)..."
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-POS-01", "ejemplarId": "EJ-001-06"}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real: $status"
echo "Body real:"
echo "$body" | jq . 2>/dev/null || echo "$body"

if [ "$status" != "409" ]; then
  echo "⚠️  RESULTADO: HTTP $status (esperado 409) - RN2 probablemente NO implementada"
else
  echo "✅ RESULTADO: HTTP 409 - RN2 implementada correctamente"
fi

echo -e "\n======================================================================"
echo "PRUEBA RN5-B: Ejemplar ya prestado (debe fallar con 409)"
echo "======================================================================"

echo -e "\nPreparando: Crear prestamo para EJ-002-01 con estudiante posgrado..."
curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-POS-01", "ejemplarId": "EJ-002-01"}' | jq . || echo "Error prestamo EJ-002-01"

echo -e "\nEjecutando RN5-B: Intentar prestar el mismo ejemplar a otro estudiante..."
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-002-01"}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real: $status"
echo "Body real:"
echo "$body" | jq . 2>/dev/null || echo "$body"

if [ "$status" != "409" ]; then
  echo "⚠️  RESULTADO: HTTP $status (esperado 409) - RN5 probablemente NO implementada"
else
  echo "✅ RESULTADO: HTTP 409 - RN5 implementada correctamente"
fi

echo -e "\n======================================================================"
echo "PRUEBA RN6-A: Plazo libro normal (debe ser fecha + 15 dias)"
echo "======================================================================"

echo -e "\nEjecutando RN6-A: Crear prestamo de libro normal..."
response=$(curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-001-01"}')

fechaDevolucion=$(echo "$response" | jq -r '.fechaDevolucion // .plazo // "NO_ENCONTRADO"' 2>/dev/null)
httpStatus=$(echo "$response" | jq -r '.id // "200"' 2>/dev/null)

echo "HTTP: 201 (si se creó)"
echo "Body real:"
echo "$response" | jq . 2>/dev/null || echo "$response"
echo -e "\nFecha devolución extraida: $fechaDevolucion"
echo "Hoy: $(date +%Y-%m-%d)"
echo "Hoy + 15 dias (esperado): $(date -d '+15 days' +%Y-%m-%d 2>/dev/null || date -v +15d +%Y-%m-%d 2>/dev/null || echo 'NO_CALCULABLE')"

echo -e "\n======================================================================"
echo "PRUEBA RN6-B: Plazo libro alta demanda (debe ser fecha + 3 dias)"
echo "======================================================================"

echo -e "\nEjecutando RN6-B: Crear prestamo de libro de alta demanda..."
response=$(curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "EST-PRE-01", "ejemplarId": "EJ-002-01"}')

fechaDevolucion=$(echo "$response" | jq -r '.fechaDevolucion // .plazo // "NO_ENCONTRADO"' 2>/dev/null)
httpStatus=$(echo "$response" | jq -r '.id // "200"' 2>/dev/null)

echo "HTTP: (201 si se creó, 409 si EJ-002-01 ya está prestado)"
echo "Body real:"
echo "$response" | jq . 2>/dev/null || echo "$response"
echo -e "\nFecha devolución extraida: $fechaDevolucion"
echo "Hoy: $(date +%Y-%m-%d)"
echo "Hoy + 3 dias (esperado): $(date -d '+3 days' +%Y-%m-%d 2>/dev/null || date -v +3d +%Y-%m-%d 2>/dev/null || echo 'NO_CALCULABLE')"

echo -e "\n======================================================================"
echo "FIN DE PRUEBAS"
echo "======================================================================"
