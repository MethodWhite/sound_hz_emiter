from PySide6.QtCore import QObject, Signal
import numpy as np
import sounddevice as sd

class AudioService(QObject):
    def __init__(self):
        super().__init__()
        self.sample_rate = 44100
        self.streams = {}
        self.waveforms = {}
        self.states = {}  # Track play/pause/stop states
        
    def play_frequency(self, freq_id, frequency, volume=0.5):
        if freq_id in self.streams:
            self.stop_frequency(freq_id)
        
        # Generate tone
        duration = 1.0  # seconds
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = volume * np.sin(2 * np.pi * frequency * t)
        tone = tone.astype(np.float32)
        
        # Store waveform and create stream
        self.waveforms[freq_id] = tone
        self.streams[freq_id] = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=lambda *args: self.callback(*args, freq_id=freq_id)
        )
        self.streams[freq_id].start()
        self.states[freq_id] = 'playing'
        
    def pause_frequency(self, freq_id):
        if freq_id in self.streams and self.states.get(freq_id) == 'playing':
            sd.stop(self.streams[freq_id])
            self.states[freq_id] = 'paused'
            
    def stop_frequency(self, freq_id):
        if freq_id in self.streams:
            sd.stop(self.streams[freq_id])
            self.streams[freq_id].close()
            del self.streams[freq_id]
            del self.waveforms[freq_id]
            self.states[freq_id] = 'stopped'
            
    def set_volume(self, freq_id, volume):
        if freq_id in self.waveforms:
            self.waveforms[freq_id] = volume * self.waveforms[freq_id]
            
    def callback(self, outdata, frames, time, status, freq_id):
        if status:
            print(status)
            
        if freq_id in self.waveforms:
            tone = self.waveforms[freq_id]
            chunksize = min(len(tone), frames)
            outdata[:chunksize] = tone[:chunksize].reshape(-1, 1)
            self.waveforms[freq_id] = tone[chunksize:]
        else:
            outdata.fill(0)
            
    def stop_all(self):
        for freq_id in list(self.streams.keys()):
            self.stop_frequency(freq_id)