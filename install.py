#!/usr/bin/env python3
"""
Instalador automatico para Sound Hz Emitter v2.0
Instala todas las dependencias necesarias
"""

import subprocess
import sys
import os

def mostrar_banner():
    print("=" * 50)
    print("  INSTALADOR SOUND HZ EMITTER v2.0")
    print("=" * 50)
    print()

def instalar_dependencia(nombre_paquete, descripcion, obligatorio=False):
    """Instala una dependencia especifica"""
    print(f"Instalando {nombre_paquete} - {descripcion}")
    
    try:
        # Intentar instalacion
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", nombre_paquete],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if resultado.returncode == 0:
            print(f"  -> {nombre_paquete} instalado correctamente")
            return True
        else:
            print(f"  -> Error instalando {nombre_paquete}: {resultado.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  -> Timeout instalando {nombre_paquete}")
        return False
    except Exception as e:
        print(f"  -> Excepcion instalando {nombre_paquete}: {e}")
        return False

def verificar_instalacion():
    """Verifica que las dependencias esten instaladas"""
    print("\nVerificando instalacion...")
    
    dependencias = [
        ("PySide6", "Interfaz grafica"),
        ("numpy", "Calculos matematicos"),
        ("sounddevice", "Audio en tiempo real"),
        ("scipy", "Procesamiento de senales"),
    ]
    
    instaladas = 0
    
    for paquete, descripcion in dependencias:
        try:
            __import__(paquete)
            print(f"  {paquete}: OK")
            instaladas += 1
        except ImportError:
            print(f"  {paquete}: NO DISPONIBLE")
    
    return instaladas, len(dependencias)

def main():
    """Funcion principal del instalador"""
    mostrar_banner()
    
    print("Este instalador configurara Sound Hz Emitter v2.0")
    print("Se instalaran las siguientes dependencias:")
    print("  - PySide6 (OBLIGATORIO): Interfaz grafica")
    print("  - numpy (RECOMENDADO): Calculos matematicos")
    print("  - sounddevice (RECOMENDADO): Audio real")
    print("  - scipy (OPCIONAL): Procesamiento avanzado")
    print()
    
    continuar = input("¿Continuar con la instalacion? (s/n): ").lower()
    if continuar not in ['s', 'si', 'y', 'yes', '']:
        print("Instalacion cancelada")
        return
    
    print("\nIniciando instalacion...")
    print("-" * 30)
    
    # Lista de dependencias a instalar
    dependencias = [
        ("PySide6", "Interfaz grafica (OBLIGATORIO)", True),
        ("numpy", "Calculos matematicos", False),
        ("sounddevice", "Audio en tiempo real", False),
        ("scipy", "Procesamiento de senales", False),
    ]
    
    instalaciones_exitosas = 0
    
    for paquete, descripcion, obligatorio in dependencias:
        exito = instalar_dependencia(paquete, descripcion, obligatorio)
        if exito:
            instalaciones_exitosas += 1
        elif obligatorio:
            print(f"\nERROR: {paquete} es obligatorio y no se pudo instalar")
            print("La aplicacion no funcionara sin esta dependencia")
            return
    
    # Verificar instalacion
    instaladas, total = verificar_instalacion()
    
    print("\n" + "=" * 50)
    print("  RESUMEN DE INSTALACION")
    print("=" * 50)
    
    if instaladas >= 1:  # Al menos PySide6
        print(f"EXITO: {instaladas}/{total} dependencias instaladas")
        print()
        print("Sound Hz Emitter esta listo para usar!")
        print()
        print("Para ejecutar la aplicacion:")
        print("  python main.py")
        print()
        
        if instaladas < total:
            print("NOTA: Algunas dependencias opcionales no se instalaron.")
            print("La aplicacion funcionara en modo basico.")
            print("Para funcionalidad completa, instala manualmente:")
            print("  pip install numpy sounddevice scipy")
    else:
        print("ERROR: No se pudieron instalar las dependencias criticas")
        print("Intenta instalar manualmente:")
        print("  pip install PySide6")
    
    print()
    input("Presiona Enter para finalizar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstalacion interrumpida por el usuario")
    except Exception as e:
        print(f"\n\nError inesperado: {e}")
