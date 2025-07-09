import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui.main_window import MainWindow

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )

def check_python_version():
    if sys.version_info < (3, 13):
        logging.warning("Se recomienda Python 3.13 o superior")
    elif sys.version_info >= (3, 14):
        logging.warning("Python 3.14 no está oficialmente soportado aún")

def main():
    check_python_version()
    setup_logging()
    logger = logging.getLogger('main')
    logger.info("Iniciando aplicación")
    
    try:
        app = QApplication(sys.argv)
        
        # Configurar fuente global
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("Error crítico en la aplicación")
        sys.exit(1)

if __name__ == "__main__":
    main()