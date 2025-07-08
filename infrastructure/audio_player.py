import pyaudio
import numpy as np
import threading
import time
import queue
from core.ports import AudioPlayer
from core.domain import WaveType
from typing import Dict, Tuple

class PyAudioPlayer(AudioPlayer):
    SAMPLE_RATE = 44100
    CHUNK_SIZE = 1024
    MAX_FREQUENCIES = 16  # Límite para prevenir sobrecarga
    
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.lock = threading.Lock()
        self.active_streams = {}
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.worker_thread.start()
        
        # Precalcular formas de onda comunes
        self.precalculated_waves = self._precalculate_waves()
    
    def _precalculate_waves(self) -> Dict[Tuple[WaveType, float], np.ndarray]:
        """Precalcula buffers para frecuencias comunes"""
        waves = {}
        common_freqs = [50, 100, 200, 400, 800, 1000, 2000, 4000, 8000]
        
        for freq in common_freqs:
            for wave_type in WaveType:
                if wave_type == WaveType.SILENCE:
                    continue
                
                t = np.linspace(0, 0.1, int(self.SAMPLE_RATE * 0.1), False)
                wave = self._generate_single_wave(wave_type, freq, t)
                waves[(wave_type, freq)] = wave.astype(np.float32)
        
        return waves
    
    def _generate_single_wave(self, wave_type: WaveType, frequency: float, t: np.ndarray) -> np.ndarray:
        """Genera una sola forma de onda"""
        if wave_type == WaveType.SINE:
            return 0.5 * np.sin(2 * np.pi * frequency * t)
        elif wave_type == WaveType.SQUARE:
            return 0.5 * np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == WaveType.TRIANGULAR:
            phase = t * frequency - np.floor(t * frequency)
            return 0.5 * (1 - 2 * np.abs(2 * phase - 1))
        elif wave_type == WaveType.SAWTOOTH:
            return 0.5 * 2 * (t * frequency - np.floor(0.5 + t * frequency))
        elif wave_type == WaveType.PULSE:
            return 0.5 * (np.mod(t * frequency, 1) < 0.1).astype(float)
        elif wave_type == WaveType.WHITE_NOISE:
            return 0.1 * np.random.randn(len(t))
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
            return 0.1 * pink / np.max(np.abs(pink))
        elif wave_type == WaveType.BROWNIAN_NOISE:
            brown = np.cumsum(np.random.randn(len(t)) * 0.1)
            return 0.1 * brown / np.max(np.abs(brown))
        else:  # SILENCE
            return np.zeros_like(t)
    
    def _generate_wave(self, wave_type: WaveType, frequency: float) -> np.ndarray:
        """Genera o recupera una forma de onda, optimizado"""
        if wave_type == WaveType.SILENCE:
            return np.zeros(int(self.SAMPLE_RATE * 0.1), dtype=np.float32)
        
        # Intenta usar forma de onda precalculada
        key = (wave_type, round(frequency))
        if key in self.precalculated_waves:
            return self.precalculated_waves[key]
        
        # Genera nueva si no está precalculada
        t = np.linspace(0, 0.1, int(self.SAMPLE_RATE * 0.1), False)
        wave = self._generate_single_wave(wave_type, frequency, t)
        return wave.astype(np.float32)
    
    def _audio_worker(self):
        """Worker thread que maneja todo el audio"""
        stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.SAMPLE_RATE,
            output=True,
            frames_per_buffer=self.CHUNK_SIZE
        )
        
        try:
            while not self.stop_event.is_set():
                # Mezclar todas las frecuencias activas
                mixed_wave = np.zeros(int(self.SAMPLE_RATE * 0.1), dtype=np.float32)
                active_count = 0
                
                with self.lock:
                    for freq_id, (wave_type, frequency) in list(self.active_streams.items()):
                        wave = self._generate_wave(wave_type, frequency)
                        if len(wave) > len(mixed_wave):
                            mixed_wave = np.zeros(len(wave), dtype=np.float32)
                        mixed_wave[:len(wave)] += wave
                        active_count += 1
                
                # Normalizar si hay múltiples frecuencias
                if active_count > 1:
                    mixed_wave = np.clip(mixed_wave / active_count, -1.0, 1.0)
                
                # Reproducir el audio mezclado
                if active_count > 0:
                    stream.write(mixed_wave.tobytes())
                else:
                    time.sleep(0.01)  # Esperar si no hay audio
                    
        finally:
            stream.stop_stream()
            stream.close()
    
    def play_frequency(self, freq_id: int, wave_type: WaveType, frequency: float):
        with self.lock:
            if len(self.active_streams) >= self.MAX_FREQUENCIES:
                print(f"Advertencia: Límite de {self.MAX_FREQUENCIES} frecuencias alcanzado")
                return
                
            self.active_streams[freq_id] = (wave_type, frequency)
    
    def pause_frequency(self, freq_id: int):
        self.stop_frequency(freq_id)
    
    def stop_frequency(self, freq_id: int):
        with self.lock:
            if freq_id in self.active_streams:
                del self.active_streams[freq_id]
    
    def stop_all(self):
        with self.lock:
            self.active_streams.clear()