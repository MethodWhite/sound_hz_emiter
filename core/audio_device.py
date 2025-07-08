from PySide6.QtCore import QObject, Signal, Slot
from core.audio_engine import AudioEngine
from core.waveform_generators import WaveformType
import numpy as np
import logging

logger = logging.getLogger(__name__)

class AudioService(QObject):
    playbackStateChanged = Signal(bool)
    errorOccurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = AudioEngine()
        self.visualization_callback = None
        
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
    
    @Slot(int)
    def set_device(self, device_index):
        try:
            self.engine.set_device(device_index)
        except Exception as e:
            error_msg = f"Device error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot()
    def start_playback(self):
        try:
            if self.engine.start_playback():
                self.playbackStateChanged.emit(True)
            else:
                self.errorOccurred.emit("Failed to start playback")
        except Exception as e:
            error_msg = f"Playback start error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot()
    def stop_playback(self):
        try:
            self.engine.stop_playback()
            self.playbackStateChanged.emit(False)
        except Exception as e:
            error_msg = f"Playback stop error: {str(e)}"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    def get_available_devices(self):
        return self.engine.device_manager.get_device_list()
    
    def setup_visualization(self, callback):
        self.visualization_callback = callback
        self.engine.set_visualization_callback(self._process_visualization_data)
    
    def _process_visualization_data(self, samples):
        if self.visualization_callback and len(samples) > 0:
            # Downsample para mejor rendimiento
            step = max(1, len(samples) // 1000)
            self.visualization_callback(samples[::step])