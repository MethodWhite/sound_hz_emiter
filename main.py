import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Configuración de paths
sys.path.append(str(Path(__file__).parent))

from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Solo crea UNA instancia de MainWindow
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()