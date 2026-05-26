#!/bin/bash

export BASE_SIN_IA="http://localhost:8000"

echo "======================================================================"
echo "PRUEBAS RN3 A VAL-5 — VERSIÓN SIN IA"
echo "======================================================================"
echo "BASE_SIN_IA=$BASE_SIN_IA"
echo "Fecha actual: $(date +%Y-%m-%d\ %H:%M:%S)"
echo ""

# Variables globales para guardar IDs
PRESTAMO_ID=""
ESTUDIANTE_ID=1  # Juan Pérez (pregrado)
LIBRO_ID=3        # Pragmatic Programmer (disponible: 3)

echo "======================================================================"
echo "RN3: Préstamo vencido bloquea nuevos préstamos"
echo "======================================================================"
echo ""
echo "Estrategia: Intentar crear prestamo con fecha pasada (Opción A)"
echo "Si la API acepta el parámetro fechaPrestamo, se creará prestamo vencido"
echo "Si la API ignora el parámetro, se registrará como limitación técnica"
echo ""

echo "[RN3-PREP] Intentar crear prestamo con fecha pasada (2025-01-01)..."
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d "{\"estudiante_id\": $ESTUDIANTE_ID, \"libro_id\": $LIBRO_ID, \"dias_prestamo\": 14, \"fechaPrestamo\": \"2025-01-01\"}")

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP: $status"
echo "Body:"
echo "$body" | jq . 2>/dev/null || echo "$body"

# Intentar extraer ID del prestamo
PRESTAMO_ID=$(echo "$body" | jq -r '.id // empty' 2>/dev/null)

if [ -z "$PRESTAMO_ID" ]; then
  echo "❌ No se pudo crear prestamo vencido. La API probablemente ignora fechaPrestamo"
  echo "    o no acepta el parámetro. Impacto: RN3, RN4-A, RN4-B, RN8 no son validables."
  PRESTAMO_ID=""
else
  echo "✅ Préstamo creado con ID: $PRESTAMO_ID"
  
  # Verificar si la fecha vencimiento es realmente en el pasado
  fecha_vencimiento=$(echo "$body" | jq -r '.fecha_vencimiento // empty' 2>/dev/null)
  echo "   Fecha vencimiento: $fecha_vencimiento"
  
  if [[ "$fecha_vencimiento" == "2025-"* ]]; then
    echo "   ✅ Fecha es en el pasado (2025) - préstamo está vencido"
    ESTADO_VENCIDO=true
  else
    echo "   ❌ Fecha NO es en el pasado - API ignoró el parámetro fechaPrestamo"
    ESTADO_VENCIDO=false
  fi
fi

echo ""
echo "======================================================================"
echo "RN3: Intentar crear nuevo préstamo cuando hay uno vencido"
echo "======================================================================"

if [ -z "$PRESTAMO_ID" ] || [ "$ESTADO_VENCIDO" = false ]; then
  echo "⚠️  Saltando RN3 porque no se pudo crear un préstamo realmente vencido"
  RN3_HTTP="N/A"
  RN3_BODY_UTIL="N/A"
else
  echo "Ejecutando RN3: crear nuevo préstamo cuando hay uno vencido..."
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
    -H "Content-Type: application/json" \
    -d "{\"estudiante_id\": $ESTUDIANTE_ID, \"libro_id\": 1, \"dias_prestamo\": 14}")
  
  body=$(echo "$response" | sed '$d')
  status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')
  
  echo "HTTP real: $status"
  echo "Body real:"
  echo "$body" | jq . 2>/dev/null || echo "$body"
  
  RN3_HTTP="$status"
  if echo "$body" | grep -q "vencido\|pendiente"; then
    RN3_BODY_UTIL="Si"
  else
    RN3_BODY_UTIL="No"
  fi
fi

echo ""
echo "======================================================================"
echo "RN4-A: Devolución con retraso genera multa"
echo "======================================================================"

if [ -z "$PRESTAMO_ID" ] || [ "$ESTADO_VENCIDO" = false ]; then
  echo "⚠️  Saltando RN4-A porque no hay préstamo vencido disponible"
  RN4A_HTTP="N/A"
  RN4A_BODY_UTIL="N/A"
  MULTA=""
else
  echo "Registrando devolución del préstamo vencido ID=$PRESTAMO_ID..."
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_SIN_IA/prestamos/$PRESTAMO_ID/devolver" \
    -H "Content-Type: application/json" \
    -d '{}')
  
  body=$(echo "$response" | sed '$d')
  status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')
  
  echo "HTTP real: $status"
  echo "Body real:"
  echo "$body" | jq . 2>/dev/null || echo "$body"
  
  RN4A_HTTP="$status"
  
  # Extraer multa si existe
  MULTA=$(echo "$body" | jq -r '.multa // empty' 2>/dev/null)
  
  if [ -n "$MULTA" ] && [ "$MULTA" -gt 0 ]; then
    echo "✅ Multa generada: $MULTA"
    RN4A_BODY_UTIL="Si"
  else
    echo "❌ No se generó multa o es 0"
    RN4A_BODY_UTIL="No"
  fi
fi

echo ""
echo "======================================================================"
echo "RN4-B: Intento de préstamo con multa pendiente (debe fallar 409)"
echo "======================================================================"

if [ -z "$MULTA" ] || [ "$MULTA" -eq 0 ]; then
  echo "⚠️  Saltando RN4-B porque no hay multa pendiente"
  RN4B_HTTP="N/A"
  RN4B_BODY_UTIL="N/A"
else
  echo "Intentando crear nuevo préstamo con multa pendiente..."
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
    -H "Content-Type: application/json" \
    -d "{\"estudiante_id\": $ESTUDIANTE_ID, \"libro_id\": 2, \"dias_prestamo\": 14}")
  
  body=$(echo "$response" | sed '$d')
  status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')
  
  echo "HTTP real: $status"
  echo "Body real:"
  echo "$body" | jq . 2>/dev/null || echo "$body"
  
  RN4B_HTTP="$status"
  if echo "$body" | grep -q "multa\|deuda"; then
    RN4B_BODY_UTIL="Si"
  else
    RN4B_BODY_UTIL="No"
  fi
fi

echo ""
echo "======================================================================"
echo "RN8: Cálculo de multa por devolución tardía (N x 2000)"
echo "======================================================================"

if [ -z "$MULTA" ] || [ "$MULTA" -eq 0 ]; then
  echo "⚠️  Saltando RN8 porque no hay multa disponible para verificar cálculo"
  RN8_HTTP="N/A"
  RN8_BODY_UTIL="N/A"
else
  echo "Multa generada: $MULTA pesos"
  echo "Verificando si se cumple la fórmula: N días x 2000 pesos/día"
  
  # Calcular días entre 2025-01-01 y hoy
  fecha_vencido="2025-01-01"
  fecha_hoy=$(date +%Y-%m-%d)
  
  # Contar días (aproximadamente)
  dias_retraso=$(( ($(date -d "$fecha_hoy" +%s) - $(date -d "$fecha_vencido" +%s)) / 86400 ))
  multa_esperada=$(( dias_retraso * 2000 ))
  
  echo "Días de retraso (aprox): $dias_retraso"
  echo "Multa esperada: $multa_esperada pesos"
  echo "Multa real: $MULTA pesos"
  
  if [ "$MULTA" -eq "$multa_esperada" ]; then
    echo "✅ Cálculo correcto"
    RN8_HTTP="✓"
    RN8_BODY_UTIL="Si"
  else
    echo "❌ Cálculo no coincide"
    RN8_HTTP="Discrepancia"
    RN8_BODY_UTIL="No"
  fi
fi

echo ""
echo "======================================================================"
echo "RN7: Renovación denegada si hay lista de espera"
echo "======================================================================"

if [ -z "$PRESTAMO_ID" ]; then
  echo "⚠️  No hay préstamo disponible para probar renovación"
  RN7_HTTP="N/A"
  RN7_BODY_UTIL="N/A"
else
  echo "Intentando renovar préstamo ID=$PRESTAMO_ID..."
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X PUT "$BASE_SIN_IA/prestamos/$PRESTAMO_ID/renovar" \
    -H "Content-Type: application/json" \
    -d '{}' 2>&1)
  
  body=$(echo "$response" | sed '$d')
  status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')
  
  echo "HTTP real: $status"
  echo "Body real:"
  echo "$body" | jq . 2>/dev/null || echo "$body"
  
  if echo "$status" | grep -q "404\|405\|Not Found\|Method Not Allowed"; then
    echo "⚠️  Endpoint /renovar no existe o no está implementado"
    RN7_HTTP="404/405"
    RN7_BODY_UTIL="Si"
  else
    RN7_HTTP="$status"
    if echo "$body" | grep -q "espera\|lista\|reserva"; then
      RN7_BODY_UTIL="Si"
    else
      RN7_BODY_UTIL="No"
    fi
  fi
fi

echo ""
echo "======================================================================"
echo "PRUEBAS DE VALIDACIÓN VAL-1 A VAL-5"
echo "======================================================================"

echo ""
echo "VAL-1: Body vacío"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real: $status"
echo "Body real:"
echo "$body" | jq . 2>/dev/null || echo "$body"
VAL1_HTTP="$status"
[ "$status" = "422" ] || [ "$status" = "400" ] && VAL1_BODY_UTIL="Si" || VAL1_BODY_UTIL="No"

echo ""
echo "VAL-2: Estudiante inexistente"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 999, "libro_id": 1, "dias_prestamo": 14}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real: $status"
echo "Body real:"
echo "$body" | jq . 2>/dev/null || echo "$body"
VAL2_HTTP="$status"
[ "$status" = "404" ] && VAL2_BODY_UTIL="Si" || VAL2_BODY_UTIL="No"

echo ""
echo "VAL-3: Ejemplar/Libro inexistente"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": 1, "libro_id": 999, "dias_prestamo": 14}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real: $status"
echo "Body real:"
echo "$body" | jq . 2>/dev/null || echo "$body"
VAL3_HTTP="$status"
[ "$status" = "404" ] && VAL3_BODY_UTIL="Si" || VAL3_BODY_UTIL="No"

echo ""
echo "VAL-4: Tipo de dato incorrecto (IDs como strings cuando deberían ser int)"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_SIN_IA/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudiante_id": "abc", "libro_id": true, "dias_prestamo": 14}')

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real: $status"
echo "Body real:"
echo "$body" | jq . 2>/dev/null || echo "$body"
VAL4_HTTP="$status"
[ "$status" = "422" ] || [ "$status" = "400" ] && VAL4_BODY_UTIL="Si" || VAL4_BODY_UTIL="No"

echo ""
echo "VAL-5: Consultar historial de estudiante inexistente"
echo "⚠️  Nota: API v1 probablemente no tiene endpoint /estudiantes/{id}/historial"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET $BASE_SIN_IA/estudiantes/999/historial)

body=$(echo "$response" | sed '$d')
status=$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')

echo "HTTP real: $status"
echo "Body real:"
echo "$body" | head -50
VAL5_HTTP="$status"
[ "$status" = "404" ] && VAL5_BODY_UTIL="Si" || VAL5_BODY_UTIL="No"

echo ""
echo "======================================================================"
echo "RESUMEN DE RESULTADOS"
echo "======================================================================"
echo ""
echo "RN3:   HTTP=$RN3_HTTP        BODY_UTIL=$RN3_BODY_UTIL"
echo "RN4-A: HTTP=$RN4A_HTTP       BODY_UTIL=$RN4A_BODY_UTIL"
echo "RN4-B: HTTP=$RN4B_HTTP       BODY_UTIL=$RN4B_BODY_UTIL"
echo "RN8:   HTTP=$RN8_HTTP        BODY_UTIL=$RN8_BODY_UTIL"
echo "RN7:   HTTP=$RN7_HTTP        BODY_UTIL=$RN7_BODY_UTIL"
echo "VAL-1: HTTP=$VAL1_HTTP       BODY_UTIL=$VAL1_BODY_UTIL"
echo "VAL-2: HTTP=$VAL2_HTTP       BODY_UTIL=$VAL2_BODY_UTIL"
echo "VAL-3: HTTP=$VAL3_HTTP       BODY_UTIL=$VAL3_BODY_UTIL"
echo "VAL-4: HTTP=$VAL4_HTTP       BODY_UTIL=$VAL4_BODY_UTIL"
echo "VAL-5: HTTP=$VAL5_HTTP       BODY_UTIL=$VAL5_BODY_UTIL"
echo ""
echo "======================================================================"
echo "FIN DE PRUEBAS"
echo "======================================================================"
