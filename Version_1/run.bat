@echo off
REM Script para ejecutar la API Biblioteca UCaldas v1 en Windows

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo API Biblioteca UCaldas - Versión 1
echo ===============================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en PATH
    echo Por favor, instala Python 3.9+ desde https://www.python.org
    exit /b 1
)

echo [OK] Python encontrado
python --version

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo.
    echo [*] Creando entorno virtual...
    python -m venv venv
    echo [OK] Entorno virtual creado
) else (
    echo [OK] Entorno virtual ya existe
)

REM Activar entorno virtual
echo.
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado

REM Instalar dependencias
echo.
echo [*] Instalando dependencias...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias
    exit /b 1
)
echo [OK] Dependencias instaladas

REM Iniciar servidor
echo.
echo ===============================================
echo [*] Iniciando servidor en http://localhost:8000
echo.
echo Documentación:
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo Presiona Ctrl+C para detener el servidor
echo ===============================================
echo.

python main.py

pause
