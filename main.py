import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
import importlib.metadata

def main():
    # Verificar versión de PySide6
    try:
        pyside_version = importlib.metadata.version('PySide6')
        print(f"Using PySide6 version: {pyside_version}")
    except importlib.metadata.PackageNotFoundError:
        print("PySide6 not installed!")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    
    # Crear y mostrar ventana principal
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()