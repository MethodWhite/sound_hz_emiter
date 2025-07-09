from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QStatusBar, QSplitter
from PySide6.QtCore import Qt  # Importar Qt
from ui.components.frequency_control import FrequencyControl
from ui.components.timer_control import TimerControl
from ui.components.spectrum_widget import SpectrumWidget
from core.audio_service import AudioService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Hz Emitter - Generador de Frecuencias Avanzado")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # Configurar barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #e0e0e0; color: #333;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema listo. Añade frecuencias y ajusta los parámetros.")
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter para dividir controles y espectro
        splitter = QSplitter(Qt.Orientation.Vertical)  # Qt ahora está definido
        
        # Panel superior: Controles
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)
        
        # Servicio de audio (Modelo)
        self.audio_service = AudioService()
        self.audio_service.enable_spectrum_updates()
        
        # Componentes de UI (Vistas)
        self.frequency_control = FrequencyControl(self.audio_service)
        controls_layout.addWidget(self.frequency_control)
        
        self.timer_control = TimerControl(self.audio_service)
        controls_layout.addWidget(self.timer_control)
        
        splitter.addWidget(controls_panel)
        
        # Panel inferior: Espectro
        self.spectrum_widget = SpectrumWidget()
        splitter.addWidget(self.spectrum_widget)
        
        # Configurar proporciones del splitter
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
        # Conectar señal de espectro
        self.audio_service.spectrum_updated.connect(self.spectrum_widget.update_spectrum)
        
        # Manejar cierre de aplicación
        self.app = QApplication.instance()
        if hasattr(self.app, 'aboutToQuit'):
            self.app.aboutToQuit.connect(self.cleanup)
        else:
            self.app.lastWindowClosed.connect(self.cleanup)
    
    def cleanup(self):
        self.audio_service.stop_all_tones()
        self.status_bar.showMessage("Aplicación finalizada. Todos los sonidos detenidos.")