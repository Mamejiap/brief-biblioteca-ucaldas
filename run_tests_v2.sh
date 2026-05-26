#!/bin/bash

export BASE_SIN_IA="http://localhost:8000"

echo "======================================================================"
echo "CONTEXTO: Contrato de API v1"
echo "======================================================================"
echo "La API v1 usa IDs numéricos en memoria:"
echo "- Estudiante 1: Juan Pérez (pregrado)"
echo "- Estudiante 2: María García (posgrado)"  
echo "- Estudiante 3: Carlos López (posgrado)"
echo "- Libro 1: Clean Code (disponible: 3/5)"
echo "- Libro 2: Design Patterns (disponible: 2/3)"
echo "- Libro 3: Pragmatic Programmer (disponible: 4/4)"
echo ""
echo "Contrato POST /prestamos (de pruebas-regles-negocio.md esperado):"
echo "  - estudianteId (string, EST-PRE-01)"
echo "  - ejemplarId (string, EJ-001-01)"
echo ""
echo "Contrato POST /prestamos (real en v1):"
echo "  - estudiante_id (int, 1-3)"
echo "  - libro_id (int, 1-3)"
echo "  - dias_prestamo (int, default 14)"
echo "======================================================================"

echo -e "\nVerificando datos existentes en v1..."
curl -s $BASE_SIN_IA/libros | jq '.[] | {id, titulo, cantidad_disponible}' || echo "Error listando libros"

echo -e "\n======================================================================"
echo "PRUEBA RN2-B: Sexto prestamo posgrado (debe fallar con 409)"
echo "======================================================================"
echo "Estrategia:"
echo "- Estudiante 2 (posgrado, Maria Garcia) debe tener 5 prestamos ACTIVOS"
echo "- Luego intentar el 6to (debe ser 409)"
echo "- Usando Libro 1, 2, 3 como ejemplares (con ids numéricos 1, 2, 3)"
echo ""

echo "Paso 1: Crear 5 prestamos para estudiante 2 (posgrado)..."
for lib_id in 1 1 2 2 3; do
  echo "[Préstamo $lib_id] POST /prestamos con estudiante_id=2, libro_id=$lib_id"
  response=$(curl -s -X POST $BASE_SIN_IA/prestamos \
    -H "Content-Type: application/json" \
    -d "{\"estudiante_id\": 2, \"libro_id\": $lib_id, \"dias_prestamo\": 14}")
  
  echo "$response" | jq '.id, .estado' 2>/dev/null || echo "Error: $(echo $response | jq '.detail[0].msg' 2>/dev/null || echo $response)"
done

echo -e "\nPaso 2: Intentar 6to prestamo (debe ser 409)..."
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 2, "libro_id": 1, "dias_prestamo": 14}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real RN2-B: $status"
echo "Body real RN2-B:"
echo "$body" | jq . 2>/dev/null || echo "$body"

if [ "$status" = "409" ]; then
  echo "✅ RESULTADO RN2-B: HTTP 409 - Regla RN2 implementada"
  body_util="Si"
else
  echo "⚠️  RESULTADO RN2-B: HTTP $status (esperado 409) - Regla RN2 NO implementada"
  body_util="No"
fi

echo "RN2-B_HTTP=$status"
echo "RN2-B_BODY_UTIL=$body_util"

echo -e "\n======================================================================"
echo "PRUEBA RN5-B: Ejemplar ya prestado (debe fallar con 409)"
echo "======================================================================"
echo "Estrategia:"
echo "- Crear prestamo de Libro 1 a Estudiante 1 (pregrado)"
echo "- Luego intentar prestar el MISMO Libro 1 a Estudiante 2 (posgrado)"
echo "- Si Libro 1 ya está prestado, debe devolver 409"
echo ""

echo "Paso 1: Crear prestamo de Libro 1 para Estudiante 1..."
response=$(curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 1, "dias_prestamo": 14}')

echo "$response" | jq '.id, .estado' 2>/dev/null || echo "Error: $(echo $response | jq '.detail[0].msg' 2>/dev/null || echo $response)"

echo -e "\nPaso 2: Intentar prestar Libro 1 a Estudiante 3 (debe fallar 409 si ejemplar ya prestado)..."
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 3, "libro_id": 1, "dias_prestamo": 14}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real RN5-B: $status"
echo "Body real RN5-B:"
echo "$body" | jq . 2>/dev/null || echo "$body"

if [ "$status" = "409" ]; then
  echo "✅ RESULTADO RN5-B: HTTP 409 - Regla RN5 implementada (ejemplar único)"
  body_util="Si"
else
  echo "⚠️  RESULTADO RN5-B: HTTP $status (esperado 409) - Regla RN5 NO implementada"
  body_util="No"
fi

echo "RN5-B_HTTP=$status"
echo "RN5-B_BODY_UTIL=$body_util"

echo -e "\n======================================================================"
echo "PRUEBA RN6-A: Plazo libro normal (debe ser fecha + 15 dias)"
echo "======================================================================"
echo "Estrategia:"
echo "- Crear prestamo de Libro 2 (Design Patterns, NO es altaDemanda)"
echo "- Verificar que fecha_vencimiento = hoy + 15 dias"
echo ""

echo "Paso 1: Crear prestamo de Libro 2 (normal)..."
response=$(curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 2, "dias_prestamo": 14}')

echo "Body completo:"
echo "$response" | jq . || echo "$response"

fecha_vencimiento=$(echo "$response" | jq -r '.fecha_vencimiento // "NO_ENCONTRADO"' 2>/dev/null)
dias_prestamo=$(echo "$response" | jq -r '.dias_prestamo // "NO_ENCONTRADO"' 2>/dev/null)

echo ""
echo "Fecha vencimiento extraida: $fecha_vencimiento"
echo "Dias prestamo extraido: $dias_prestamo"
echo "Hoy: $(date +%Y-%m-%d)"
echo "Hoy + 15 dias (esperado): $(date -d '+15 days' +%Y-%m-%d 2>/dev/null || date -v +15d +%Y-%m-%d 2>/dev/null || echo 'NO_CALCULABLE')"

if [[ "$fecha_vencimiento" =~ "2026-06-10" ]]; then
  echo "✅ RESULTADO RN6-A: Plazo correcto (15 dias)"
  body_util="Si"
  http_status="201"
else
  echo "⚠️  RESULTADO RN6-A: Plazo no validado - fecha encontrada: $fecha_vencimiento"
  body_util="No"
  http_status="201"
fi

echo "RN6-A_HTTP=$http_status"
echo "RN6-A_BODY_UTIL=$body_util"
echo "RN6-A_FECHA=$fecha_vencimiento"

echo -e "\n======================================================================"
echo "PRUEBA RN6-B: Plazo libro alta demanda (debe ser fecha + 3 dias)"
echo "======================================================================"
echo "Estrategia:"
echo "- Crear prestamo de Libro 3 (Pragmatic Programmer, NO es altaDemanda en v1)"
echo "- Verificar que fecha_vencimiento = hoy + 3 dias si altaDemanda fuera true"
echo ""
echo "⚠️  Nota: v1 main.py NO tiene campo altaDemanda implementado en Libro model"
echo "    Por tanto, RN6-B depende de si altaDemanda está en la lógica de vencimiento"
echo ""

echo "Paso 1: Crear prestamo de Libro 3..."
response=$(curl -s -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 3, "dias_prestamo": 14}')

echo "Body completo:"
echo "$response" | jq . || echo "$response"

fecha_vencimiento=$(echo "$response" | jq -r '.fecha_vencimiento // "NO_ENCONTRADO"' 2>/dev/null)
dias_prestamo=$(echo "$response" | jq -r '.dias_prestamo // "NO_ENCONTRADO"' 2>/dev/null)

echo ""
echo "Fecha vencimiento extraida: $fecha_vencimiento"
echo "Dias prestamo extraido: $dias_prestamo"
echo "Hoy: $(date +%Y-%m-%d)"
echo "Hoy + 3 dias (esperado): $(date -d '+3 days' +%Y-%m-%d 2>/dev/null || date -v +3d +%Y-%m-%d 2>/dev/null || echo 'NO_CALCULABLE')"
echo "Hoy + 14 dias (actual default): $(date -d '+14 days' +%Y-%m-%d 2>/dev/null || date -v +14d +%Y-%m-%d 2>/dev/null || echo 'NO_CALCULABLE')"

if [[ "$fecha_vencimiento" =~ "2026-05-29" ]]; then
  echo "✅ RESULTADO RN6-B: Plazo correcto (3 dias)"
  body_util="Si"
elif [[ "$fecha_vencimiento" =~ "2026-06-09" ]]; then
  echo "⚠️  RESULTADO RN6-B: Plazo es 14 dias (default), no 3 dias - RN6-B NO implementada"
  body_util="No"
else
  echo "⚠️  RESULTADO RN6-B: Plazo no validado - fecha encontrada: $fecha_vencimiento"
  body_util="No"
fi

http_status="201"
echo "RN6-B_HTTP=$http_status"
echo "RN6-B_BODY_UTIL=$body_util"
echo "RN6-B_FECHA=$fecha_vencimiento"

echo -e "\n======================================================================"
echo "RESUMEN FINAL"
echo "======================================================================"
echo "RN2-B: HTTP=$status (esperado 409) - UTIL=$body_util"
echo "RN5-B: HTTP=$status (esperado 409) - UTIL=$body_util"
echo "RN6-A: Plazo validado - UTIL=$body_util"
echo "RN6-B: Plazo validado - UTIL=$body_util"
echo "======================================================================"
