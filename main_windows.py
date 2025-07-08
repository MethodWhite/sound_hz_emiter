import numpy as np
from PySide6.QtWidgets import QMainWindow, QMessageBox
from ui.ui_main_window import Ui_MainWindow
from core.audio_processor import AudioProcessor
from core.hardware_detector import HardwareDetector
from utils.audio_utils import AudioVisualizer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.audio_processor = AudioProcessor()
        
        # Configurar UI
        self.waveform_fig, self.waveform_ax, self.waveform_canvas = AudioVisualizer.create_waveform_plot(self.ui.waveformPlot)
        self.spectrum_fig, self.spectrum_ax, self.spectrum_canvas = AudioVisualizer.create_spectrum_plot(self.ui.spectrumPlot)
        
        self.ui.frequencySpinBox.setRange(20, 20000)
        self.ui.frequencySpinBox.setValue(440.0)
        self.ui.durationSpinBox.setRange(0.1, 10.0)
        self.ui.durationSpinBox.setValue(1.0)
        
        # Conectar señales
        self.ui.playButton.clicked.connect(self.play_tone)
        self.ui.stopButton.clicked.connect(self.stop_playback)
        self.audio_processor.audio_processed.connect(self.update_spectrum)
        self.audio_processor.playback_finished.connect(self.playback_completed)
        
        # Configurar hardware (solo CPU)
        self.ui.deviceComboBox.addItem("CPU", {"name": "CPU", "type": "CPU"})

    def play_tone(self):
        try:
            frequency = self.ui.frequencySpinBox.value()
            duration = self.ui.durationSpinBox.value()
            
            self.audio_processor.frequency = frequency
            self.audio_processor.duration = duration
            
            tone = self.audio_processor.generate_tone()
            AudioVisualizer.update_waveform_plot(
                self.waveform_ax, 
                self.waveform_canvas, 
                tone, 
                self.audio_processor.sample_rate
            )
            
            self.audio_processor.analyze_audio(tone)
            self.audio_processor.play_tone()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al reproducir tono:\n{str(e)}")

    def stop_playback(self):
        self.audio_processor.stop_playback()

    def update_spectrum(self, spectrum):
        AudioVisualizer.update_spectrum_plot(
            self.spectrum_ax,
            self.spectrum_canvas,
            spectrum,
            self.audio_processor.sample_rate
        )

    def playback_completed(self):
        self.statusBar().showMessage("Reproducción completada", 3000)
