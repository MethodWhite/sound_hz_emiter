from PySide6.QtCore import QObject, Signal, Slot, QTimer
from core.audio_engine import AudioEngine
from core.waveform_generators import WaveformType
import logging
import time

logger = logging.getLogger(__name__)

class AudioService(QObject):
    playbackStateChanged = Signal(bool)
    errorOccurred = Signal(str)
    timerUpdated = Signal(int)  # Señal para actualizar el temporizador
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = AudioEngine()
        self.visualization_callback = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer_duration = 0
        self.timer_remaining = 0
    
    @Slot(float)
    def set_frequency(self, frequency):
        try:
            self.engine.set_frequency(frequency)
        except Exception as e:
            error_msg = f"Frequency error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(float)
    def set_amplitude(self, amplitude):
        try:
            self.engine.set_amplitude(amplitude)
        except Exception as e:
            error_msg = f"Amplitude error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(int)
    def set_waveform(self, waveform_type_index):
        try:
            wave_type = WaveformType(waveform_type_index)
            self.engine.set_waveform(wave_type)
        except Exception as e:
            error_msg = f"Waveform error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot()
    def start_playback(self, duration=0):
        try:
            self.engine.start_playback()
            self.playbackStateChanged.emit(True)
            
            # Configurar temporizador si se especificó una duración
            if duration > 0:
                self.timer_duration = duration
                self.timer_remaining = duration
                self.timer.start(1000)  # Actualizar cada segundo
        except Exception as e:
            error_msg = f"Playback start error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot()
    def stop_playback(self):
        try:
            self.engine.stop_playback()
            self.playbackStateChanged.emit(False)
            self.timer.stop()
        except Exception as e:
            error_msg = f"Playback stop error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    def setup_visualization(self, callback):
        self.visualization_callback = callback
        self.engine.set_visualization_callback(self._process_visualization_data)
    
    def _process_visualization_data(self, samples):
        if self.visualization_callback and len(samples) > 0:
            # Downsample para mejor rendimiento
            step = max(1, len(samples) // 1000)
            self.visualization_callback(samples[::step])
    
    @Slot()
    def update_timer(self):
        if self.timer_remaining > 0:
            self.timer_remaining -= 1
            self.timerUpdated.emit(self.timer_remaining)
        else:
            self.stop_playback()
    
    @Slot(float)
    def add_frequency(self, frequency):
        try:
            self.engine.add_frequency(frequency)
        except Exception as e:
            error_msg = f"Add frequency error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(float)
    def remove_frequency(self, frequency):
        try:
            self.engine.remove_frequency(frequency)
        except Exception as e:
            error_msg = f"Remove frequency error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot()
    def clear_frequencies(self):
        try:
            self.engine.clear_frequencies()
        except Exception as e:
            error_msg = f"Clear frequencies error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)