from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QStatusBar
from ui.components.frequency_control import FrequencyControl
from ui.components.timer_control import TimerControl
from ui.components.spectrum_widget import SpectrumWidget
from core.audio_service import AudioService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Hz Emitter")
        self.setGeometry(100, 100, 800, 600)
        
        # Configurar barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema listo")
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Servicio de audio (Modelo)
        self.audio_service = AudioService()
        self.audio_service.enable_spectrum_updates()
        
        # Componentes de UI (Vistas)
        self.frequency_control = FrequencyControl(self.audio_service)
        layout.addWidget(self.frequency_control)
        
        self.timer_control = TimerControl(self.audio_service)
        layout.addWidget(self.timer_control)
        
        self.spectrum_widget = SpectrumWidget()
        layout.addWidget(self.spectrum_widget, 1)  # Mayor espacio para el espectro
        
        # Conectar señal de espectro
        self.audio_service.spectrum_updated.connect(self.spectrum_widget.update_spectrum)
        
        # Manejar cierre de aplicación
        self.app = QApplication.instance()
        # Compatibilidad con diferentes versiones de PySide6
        if hasattr(self.app, 'aboutToQuit'):
            self.app.aboutToQuit.connect(self.cleanup)
        else:
            # Alternativa para versiones recientes
            self.app.lastWindowClosed.connect(self.cleanup)
    
    def cleanup(self):
        self.audio_service.stop_all_tones()
        self.status_bar.showMessage("Aplicación finalizada")