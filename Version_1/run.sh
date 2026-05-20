#!/bin/bash

# Script para ejecutar la API Biblioteca UCaldas v1 en macOS/Linux

set -e

echo ""
echo "==============================================="
echo "API Biblioteca UCaldas - Versión 1"
echo "==============================================="
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado"
    echo "Por favor, instala Python 3.9+ desde https://www.python.org"
    exit 1
fi

echo "[OK] Python encontrado"
python3 --version

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo ""
    echo "[*] Creando entorno virtual..."
    python3 -m venv venv
    echo "[OK] Entorno virtual creado"
else
    echo "[OK] Entorno virtual ya existe"
fi

# Activar entorno virtual
echo ""
echo "[*] Activando entorno virtual..."
source venv/bin/activate
echo "[OK] Entorno virtual activado"

# Instalar dependencias
echo ""
echo "[*] Instalando dependencias..."
pip install -q -r requirements.txt
echo "[OK] Dependencias instaladas"

# Iniciar servidor
echo ""
echo "==============================================="
echo "[*] Iniciando servidor en http://localhost:8000"
echo ""
echo "Documentación:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo "==============================================="
echo ""

python3 main.py
