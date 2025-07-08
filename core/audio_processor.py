import numpy as np
import sounddevice as sd
from PySide6.QtCore import QObject, Signal

class AudioProcessor(QObject):
    audio_processed = Signal(np.ndarray)
    playback_finished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sample_rate = 44100
        self.duration = 1.0
        self.frequency = 440.0
        self.stream = None
        
    def generate_tone(self):
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), False)
        return np.sin(2 * np.pi * self.frequency * t)
    
    def play_tone(self):
        tone = self.generate_tone()
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=lambda *args: None
        )
        self.stream.start()
        self.stream.write(tone)
        self.playback_finished.emit()
        
    def stop_playback(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
    def analyze_audio(self, audio_data):
        spectrum = np.abs(np.fft.fft(audio_data)[:len(audio_data)//2])
        self.audio_processed.emit(spectrum)
