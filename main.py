#!/usr/bin/env python3
"""Sound Hz Emitter - Aplicacion principal"""

import sys
import os
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

def verificar_dependencias():
    """Verifica que las dependencias esten disponibles"""
    faltantes = []
    
    try:
        import PySide6
        print("PySide6: OK")
    except ImportError:
        print("PySide6: NO DISPONIBLE")
        faltantes.append("PySide6")
        return False, faltantes
    
    try:
        import numpy
        print("NumPy: OK")
    except ImportError:
        print("NumPy: No disponible (funcionalidad limitada)")
        faltantes.append("numpy")
    
    try:
        import sounddevice
        print("SoundDevice: OK")
    except ImportError:
        print("SoundDevice: No disponible (audio simulado)")
        faltantes.append("sounddevice")
    
    return True, faltantes

def main():
    print("=== Sound Hz Emitter v2.0 ===")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("Error: Se requiere Python 3.8 o superior")
        return 1
    
    # Verificar dependencias
    deps_ok, faltantes = verificar_dependencias()
    
    if not deps_ok:
        print("\nError: PySide6 es requerido")
        print("Instala con: pip install PySide6")
        return 1
    
    # Crear aplicacion Qt
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        app = QApplication(sys.argv)
        app.setApplicationName("Sound Hz Emitter")
        app.setStyle('Fusion')
        
        # Crear directorios si no existen
        for d in ['config', 'ui']:
            os.makedirs(d, exist_ok=True)
            init_path = Path(d) / '__init__.py'
            if not init_path.exists():
                init_path.write_text('# Paquete Python\n', encoding='utf-8')
        
        # Cargar ventana principal
        try:
            from ui.ventana_principal import VentanaPrincipal
            ventana = VentanaPrincipal()
            
            # Mostrar advertencia si faltan dependencias
            if faltantes:
                from PySide6.QtWidgets import QMessageBox
                deps_texto = ", ".join(faltantes)
                QMessageBox.information(
                    ventana, "Dependencias", 
                    f"Dependencias opcionales no encontradas: {deps_texto}\n"
                    f"La aplicacion funcionara en modo basico.\n\n"
                    f"Para funcionalidad completa instala:\n"
                    f"pip install {' '.join(faltantes)}"
                )
            
            ventana.show()
            return app.exec()
            
        except ImportError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None, "Error", 
                f"No se pudo cargar la interfaz: {e}\n\n"
                f"Verifica que el archivo ui/ventana_principal.py exista."
            )
            return 1
    
    except ImportError:
        print("\nError: PySide6 no esta instalado")
        print("Instala con: pip install PySide6")
        return 1

if __name__ == "__main__":
    sys.exit(main())
