from PySide6.QtCore import QObject, Signal
import numpy as np

class AudioService(QObject):
    spectrum_updated = Signal(np.ndarray, np.ndarray)
    
    def __init__(self, sample_rate=44100, buffer_size=1024):
        super().__init__()
        from core.audio_engine import AudioEngine
        self.engine = AudioEngine(sample_rate, buffer_size)
        self.engine.start_stream()
    
    def add_tone(self, tone_id, frequency, volume):
        self.engine.add_tone(tone_id, frequency, volume)
    
    def update_tone(self, tone_id, frequency, volume):
        self.engine.update_tone(tone_id, frequency, volume)
    
    def remove_tone(self, tone_id):
        self.engine.remove_tone(tone_id)
    
    def stop_all_tones(self):
        self.engine.stop_all_tones()
    
    def get_spectrum_data(self):
        return self.engine.calculate_spectrum()
    
    def enable_spectrum_updates(self, interval=100):
        from PySide6.QtCore import QTimer
        self.spectrum_timer = QTimer()
        self.spectrum_timer.timeout.connect(self._update_spectrum)
        self.spectrum_timer.start(interval)
    
    def _update_spectrum(self):
        freqs, magnitudes = self.get_spectrum_data()
        self.spectrum_updated.emit(freqs, magnitudes)