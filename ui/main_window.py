from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QStatusBar, QLabel, QToolButton, QScrollArea, 
                              QComboBox, QFrame, QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPalette, QColor, QFont

# Importaciones absolutas desde el paquete ui.components
from ui.components.timer_control import TimerControl
from ui.components.frequency_control import FrequencyControl
from core.audio_service import AudioService

class MainWindow(QMainWindow):
    theme_changed = Signal(bool)
    language_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initialized = True  # Bandera para evitar doble inicialización
        self.setWindowTitle("Sound Hz Emitter")
        self.setGeometry(100, 100, 900, 600)
        self.is_dark_theme = False
        self.current_language = "en"
        self.audio_service = AudioService()
        
        # Configuración de fuente
        self.app_font = QFont("Segoe UI", 9)
        self.app_font.setBold(True)
        
        # Diccionario de traducciones
        self.translations = {
            "en": {
                "title": "Sound Hz Emitter",
                "controls": "Frequency Controls",
                "timer": "Timer Control",
                "add_freq": "Add Frequency",
                "spectrum": "Real-time Spectrum"
            },
            "es": {
                "title": "Emisor de Hz",
                "controls": "Controles de Frecuencia",
                "timer": "Control de Tiempo",
                "add_freq": "Añadir Frecuencia",
                "spectrum": "Espectro en Tiempo Real"
            }
        }
        
        self.init_ui()
        self.apply_light_theme()
        self.update_language()

    def init_ui(self):
        # Widget central
        central_widget = QWidget()
        central_widget.setFont(self.app_font)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Título
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(self.title_label)

        # Selector de idioma
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        header_layout.addWidget(self.lang_combo)

        # Botón de tema
        self.theme_btn = QToolButton()
        self.theme_btn.setIcon(QIcon.fromTheme("weather-sunny"))
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn, alignment=Qt.AlignRight)
        main_layout.addWidget(header)

        # Control de temporizador
        self.timer_control = TimerControl(self.audio_service)
        main_layout.addWidget(self.timer_control)

        # Control de frecuencias con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)


        self.frequency_control = FrequencyControl(self.audio_service)
        scroll.setWidget(self.frequency_control)
        main_layout.addWidget(scroll, 1)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Conectar señales
        self.timer_control.timerStarted.connect(self.audio_service.start_all_tones)
        self.timer_control.timerStopped.connect(self.audio_service.stop_all_tones)
        self.theme_changed.connect(self.frequency_control.set_dark_theme)
        self.theme_changed.connect(self.timer_control.set_dark_theme)

    def change_language(self, index):
        self.current_language = self.lang_combo.itemData(index)
        self.update_language()
        self.language_changed.emit(self.current_language)

    def update_language(self):
        lang = self.translations[self.current_language]
        self.title_label.setText(lang["title"])
        self.frequency_control.update_language(lang["controls"], lang["add_freq"])
        self.timer_control.update_language(lang["timer"])

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.apply_dark_theme()
            self.theme_btn.setIcon(QIcon.fromTheme("weather-sunny"))
        else:
            self.apply_light_theme()
            self.theme_btn.setIcon(QIcon.fromTheme("weather-night"))
        self.theme_changed.emit(self.is_dark_theme)

    def apply_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        QApplication.instance().setPalette(palette)

        # Aplicar estilos específicos
        self.title_label.setStyleSheet("font-size: 16px; color: black;")
        self.frequency_control.set_light_theme()
        self.timer_control.set_light_theme()

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(100, 180, 255))
        palette.setColor(QPalette.Text, QColor(100, 180, 255))
        palette.setColor(QPalette.ButtonText, QColor(100, 180, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        QApplication.instance().setPalette(palette)

        # Aplicar estilos específicos
        self.title_label.setStyleSheet("font-size: 16px; color: white;")
        self.frequency_control.set_dark_theme()
        self.timer_control.set_dark_theme()