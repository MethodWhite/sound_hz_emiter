import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from ui.main_window import MainWindow
import importlib.metadata

def apply_dark_theme(app):
    # Crear una paleta de colores oscura
    dark_palette = QPalette()
    
    # Colores base
    dark_palette.setColor(QPalette.Window, QColor(45, 45, 48))
    dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 48))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Text, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 48))
    dark_palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(0, 122, 204))
    dark_palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
    dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # Colores deshabilitados
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    
    app.setPalette(dark_palette)
    app.setStyle("Fusion")

def main():
    # Verificar versión de PySide6
    try:
        pyside_version = importlib.metadata.version('PySide6')
        print(f"Using PySide6 version: {pyside_version}")
    except importlib.metadata.PackageNotFoundError:
        print("PySide6 not installed!")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    
    # Aplicar tema oscuro personalizado
    apply_dark_theme(app)
    
    # Crear y mostrar ventana principal
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()