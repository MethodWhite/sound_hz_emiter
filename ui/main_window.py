import sys
import os
import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGroupBox, QLabel, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QIcon
from .controls import (
    FrequencyControl, AmplitudeControl, WaveformSelector,
    PlaybackControl, VisualizationWidget, TimerControl, FrequencyListControl
)
from services.audio_service import AudioService
from utils.constants import DEFAULT_FREQUENCY, DEFAULT_AMPLITUDE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Sound Emitter")
        self.setMinimumSize(1000, 800)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.audio_service = AudioService()
        self.audio_service.playbackStateChanged.connect(self.handle_playback_state)
        self.audio_service.errorOccurred.connect(self.handle_error)
        self.audio_service.timerUpdated.connect(self.timer_control.update_timer)
        
        self.setup_ui()
        self.setup_connections()
        
        # Set default values
        self.frequency_control.set_value(DEFAULT_FREQUENCY)
        self.amplitude_control.set_value(DEFAULT_AMPLITUDE)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Control section
        control_group = QGroupBox("Audio Controls")
        control_layout = QVBoxLayout()
        
        # Frequency control
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequency:"))
        self.frequency_control = FrequencyControl()
        freq_layout.addWidget(self.frequency_control)
        control_layout.addLayout(freq_layout)
        
        # Amplitude control
        amp_layout = QHBoxLayout()
        amp_layout.addWidget(QLabel("Amplitude:"))
        self.amplitude_control = AmplitudeControl()
        amp_layout.addWidget(self.amplitude_control)
        control_layout.addLayout(amp_layout)
        
        # Waveform selection
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("Waveform:"))
        self.waveform_selector = WaveformSelector()
        wave_layout.addWidget(self.waveform_selector)
        control_layout.addLayout(wave_layout)
        
        # Timer control
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(QLabel("Duration:"))
        self.timer_control = TimerControl()
        timer_layout.addWidget(self.timer_control)
        control_layout.addLayout(timer_layout)
        
        # Playback controls
        self.playback_control = PlaybackControl()
        control_layout.addWidget(self.playback_control)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Additional frequencies
        self.freq_list_control = FrequencyListControl()
        main_layout.addWidget(self.freq_list_control)
        
        # Visualization
        vis_group = QGroupBox("Waveform Visualization")
        vis_layout = QVBoxLayout()
        self.visualization_widget = VisualizationWidget()
        vis_layout.addWidget(self.visualization_widget)
        vis_group.setLayout(vis_layout)
        main_layout.addWidget(vis_group, 1)  # Expandir espacio
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Configurar servicio de audio
        self.audio_service.setup_visualization(self.visualization_widget.update_waveform)
    
    def setup_connections(self):
        # Connect controls to audio service
        self.frequency_control.valueChanged.connect(self.audio_service.set_frequency)
        self.amplitude_control.valueChanged.connect(self.audio_service.set_amplitude)
        self.waveform_selector.currentIndexChanged.connect(
            lambda idx: self.audio_service.set_waveform(idx))
        
        # Playback controls
        self.playback_control.playClicked.connect(self.start_playback)
        self.playback_control.stopClicked.connect(self.audio_service.stop_playback)
        
        # Timer control
        self.timer_control.valueChanged.connect(self.timer_control.update_timer)
        
        # Frequency list control
        self.freq_list_control.addFrequency.connect(self.audio_service.add_frequency)
        self.freq_list_control.removeFrequency.connect(self.audio_service.remove_frequency)
    
    def start_playback(self):
        duration = self.timer_control.get_duration()
        self.audio_service.start_playback(duration)
    
    def handle_playback_state(self, is_playing):
        self.playback_control.set_playing(is_playing)
        self.statusBar().showMessage("Playing" if is_playing else "Stopped")
    
    def handle_error(self, message):
        QMessageBox.critical(self, "Audio Error", message)
        self.statusBar().showMessage(f"Error: {message}")
        logger.error(message)
    
    def closeEvent(self, event):
        self.audio_service.stop_playback()
        event.accept()