#!/bin/bash

# Sound Hz Emitter v2.0 - Lanzador para Unix/Linux/macOS

clear
echo "================================================"
echo "            SOUND HZ EMITTER v2.0"
echo "        Generador de Frecuencias de Sonido"
echo "================================================"
echo ""

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Verificar Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no esta instalado"
    echo ""
    echo "Instala Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo "  Arch: sudo pacman -S python python-pip"
    echo ""
    read -p "Presiona Enter para continuar..."
    exit 1
fi

echo "Iniciando Sound Hz Emitter..."
echo ""

# Ejecutar aplicacion
if python3 main.py; then
    echo ""
    echo "Aplicacion cerrada correctamente."
else
    echo ""
    echo "================================================"
    echo "ERROR: No se pudo ejecutar la aplicacion"
    echo "================================================"
    echo ""
    echo "Posibles soluciones:"
    echo "1. Instalar dependencias: python3 install.py"
    echo "2. Instalar PySide6: pip3 install PySide6"
    echo "3. Verificar que todos los archivos esten presentes"
    echo ""
    read -p "Presiona Enter para continuar..."
fi
