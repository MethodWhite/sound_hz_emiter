import pyaudio
import numpy as np
import threading
import time
from core.ports import AudioPlayer
from core.domain import WaveType
from typing import Dict

class PyAudioPlayer(AudioPlayer):
    SAMPLE_RATE = 44100
    CHUNK_SIZE = 1024
    
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.streams: Dict[int, any] = {}
        self.lock = threading.Lock()
        self.stop_flags = {}
        self.threads = {}
    
    def _generate_wave(self, wave_type: WaveType, frequency: float, duration: float):
        t = np.linspace(0, duration, int(self.SAMPLE_RATE * duration), False)
        
        if wave_type == WaveType.SINE:
            wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        elif wave_type == WaveType.SQUARE:
            wave = 0.5 * np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == WaveType.TRIANGULAR:
            phase = t * frequency - np.floor(t * frequency)
            wave = 0.5 * (1 - 2 * np.abs(2 * phase - 1))
        elif wave_type == WaveType.SAWTOOTH:
            wave = 0.5 * 2 * (t * frequency - np.floor(0.5 + t * frequency))
        elif wave_type == WaveType.PULSE:
            wave = 0.5 * (np.mod(t * frequency, 1) < 0.1).astype(float)
        elif wave_type == WaveType.WHITE_NOISE:
            wave = 0.1 * np.random.randn(len(t))
        elif wave_type == WaveType.PINK_NOISE:
            white = np.random.randn(len(t))
            pink = np.zeros_like(white)
            b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
            a = [1, -2.494956002, 2.017265875, -0.522189400]
            for i in range(len(white)):
                pink[i] = (a[0] * white[i] + 
                          a[1] * white[i-1] + 
                          a[2] * white[i-2] + 
                          a[3] * white[i-3] - 
                          b[1] * pink[i-1] - 
                          b[2] * pink[i-2] - 
                          b[3] * pink[i-3])
            wave = 0.1 * pink / np.max(np.abs(pink))
        elif wave_type == WaveType.BROWNIAN_NOISE:
            brown = np.cumsum(np.random.randn(len(t)) * 0.1)
            wave = 0.1 * brown / np.max(np.abs(brown))
        else:  # SILENCE
            wave = np.zeros_like(t)
        
        return wave.astype(np.float32)
    
    def _audio_thread(self, freq_id: int, wave_type: WaveType, frequency: float):
        stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.SAMPLE_RATE,
            output=True,
            frames_per_buffer=self.CHUNK_SIZE
        )
        
        try:
            while not self.stop_flags.get(freq_id, False):
                wave = self._generate_wave(wave_type, frequency, 0.1)
                stream.write(wave.tobytes())
        finally:
            stream.stop_stream()
            stream.close()
            with self.lock:
                if freq_id in self.streams:
                    del self.streams[freq_id]
                if freq_id in self.stop_flags:
                    del self.stop_flags[freq_id]
    
    def play_frequency(self, freq_id: int, wave_type: WaveType, frequency: float):
        if freq_id in self.streams:
            return
        
        with self.lock:
            self.stop_flags[freq_id] = False
            thread = threading.Thread(
                target=self._audio_thread, 
                args=(freq_id, wave_type, frequency),
                daemon=True
            )
            self.threads[freq_id] = thread
            thread.start()
            self.streams[freq_id] = True
    
    def pause_frequency(self, freq_id: int):
        self.stop_frequency(freq_id)
    
    def stop_frequency(self, freq_id: int):
        with self.lock:
            if freq_id in self.stop_flags:
                self.stop_flags[freq_id] = True
    
    def stop_all(self):
        with self.lock:
            for freq_id in list(self.streams.keys()):
                self.stop_flags[freq_id] = True
            self.streams = {}