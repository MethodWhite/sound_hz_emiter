@echo off
title Sound Hz Emitter v2.0
color 0B

echo.
echo ================================================
echo            SOUND HZ EMITTER v2.0
echo        Generador de Frecuencias de Sonido
echo ================================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Iniciando Sound Hz Emitter...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: No se pudo ejecutar la aplicacion
    echo ================================================
    echo.
    echo Posibles soluciones:
    echo 1. Instalar dependencias: python install.py
    echo 2. Instalar PySide6: pip install PySide6
    echo 3. Verificar que todos los archivos esten presentes
    echo.
    pause
) else (
    echo.
    echo Aplicacion cerrada correctamente.
)
