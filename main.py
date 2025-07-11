#!/usr/bin/env python3
"""
Sound Hz Emitter v2.0 - Clean Code Edition
Aplicación principal refactorizada
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica que las dependencias estén disponibles"""
    missing = []
    
    try:
        import PySide6
        print("✅ PySide6: OK")
    except ImportError:
        print("❌ PySide6: NO DISPONIBLE")
        missing.append("PySide6")
        return False, missing
    
    try:
        import numpy
        print("✅ NumPy: OK")
    except ImportError:
        print("⚠️  NumPy: No disponible (funcionalidad limitada)")
        missing.append("numpy")
    
    try:
        import sounddevice
        print("✅ SoundDevice: OK")
    except ImportError:
        print("⚠️  SoundDevice: No disponible (audio simulado)")
        missing.append("sounddevice")
    
    return True, missing

def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    directories = [
        'ui',
        'ui/components',
        'ui/styles', 
        'ui/audio',
        'ui/utils',
        'config'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        init_file = Path(directory) / '__init__.py'
        if not init_file.exists():
            init_file.write_text('"""Paquete Python"""', encoding='utf-8')

def show_dependency_warning(main_window, missing_deps):
    """Muestra advertencia sobre dependencias faltantes"""
    if not missing_deps:
        return
        
    from PySide6.QtWidgets import QMessageBox
    
    deps_text = ", ".join(missing_deps)
    message = (
        f"Dependencias opcionales no encontradas: {deps_text}\n\n"
        f"La aplicación funcionará en modo básico.\n\n"
        f"Para funcionalidad completa instala:\n"
        f"pip install {' '.join(missing_deps)}"
    )
    
    QMessageBox.information(main_window, "Dependencias Opcionales", message)

def main():
    """Función principal de la aplicación"""
    print("🔊 === Sound Hz Emitter v2.0 - Clean Code Edition ===")
    
    # Verificar versión de Python
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return 1
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Verificar dependencias
    deps_ok, missing_deps = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Error: PySide6 es requerido para ejecutar la aplicación")
        print("   Instala con: pip install PySide6")
        return 1
    
    # Crear estructura de directorios
    try:
        create_directory_structure()
        print("✅ Estructura de directorios verificada")
    except Exception as e:
        print(f"⚠️  Advertencia creando directorios: {e}")
    
    # Inicializar aplicación Qt
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QDir
        from PySide6.QtGui import QIcon
        
        # Configurar aplicación
        app = QApplication(sys.argv)
        app.setApplicationName("Sound Hz Emitter")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("MethodWhite")
        app.setStyle('Fusion')
        
        # Configurar directorio de trabajo
        QDir.setCurrent(str(Path(__file__).parent))
        
        print("✅ Aplicación Qt inicializada")
        
        # Cargar ventana principal
        try:
            # Import dinámico para mejor manejo de errores
            from ui.main_window import MainWindow
            
            print("✅ Módulos de UI cargados")
            
            # Crear y mostrar ventana principal
            main_window = MainWindow()
            
            # Mostrar advertencia sobre dependencias opcionales
            show_dependency_warning(main_window, missing_deps)
            
            # Configurar ventana
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
            
            print("🚀 Aplicación iniciada correctamente")
            print("   Para cerrar: Ctrl+C en terminal o cerrar ventana")
            
            # Ejecutar loop principal
            return app.exec()
            
        except ImportError as e:
            from PySide6.QtWidgets import QMessageBox, QWidget
            
            error_msg = (
                f"No se pudo cargar la interfaz principal:\n\n"
                f"Error: {e}\n\n"
                f"Verifica que existan los archivos:\n"
                f"- ui/main_window.py\n"
                f"- ui/components/\n"
                f"- ui/styles/\n"
                f"- ui/audio/"
            )
            
            print(f"❌ {error_msg}")
            
            # Mostrar diálogo de error
            widget = QWidget()
            QMessageBox.critical(widget, "Error de Carga", error_msg)
            return 1
            
        except Exception as e:
            print(f"❌ Error inesperado cargando UI: {e}")
            return 1
    
    except ImportError as e:
        print(f"\n❌ Error importando PySide6: {e}")
        print("   Instala con: pip install PySide6")
        return 1
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

def show_help():
    """Muestra información de ayuda"""
    help_text = """
🔊 Sound Hz Emitter v2.0 - Clean Code Edition

INSTALACIÓN:
    pip install PySide6 numpy sounddevice

EJECUCIÓN:
    python main.py

CARACTERÍSTICAS:
    ✅ Generación de tonos múltiples simultáneos
    ✅ Control de frecuencia, volumen y panning
    ✅ Tipos de onda: seno, cuadrada, triángulo, sierra
    ✅ Temporizador y modo Pomodoro
    ✅ Temas claro y oscuro
    ✅ Interfaz limpia y moderna

REPOSITORIO:
    https://github.com/MethodWhite/sound_hz_emiter
    """
    print(help_text)

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
            sys.exit(0)
        elif sys.argv[1] in ['--version', '-v']:
            print("Sound Hz Emitter v2.0 - Clean Code Edition")
            sys.exit(0)
    
    # Ejecutar aplicación principal
    try:
        exit_code = main()
        print(f"\n👋 Aplicación cerrada (código: {exit_code})")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Aplicación interrumpida por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        sys.exit(1)
