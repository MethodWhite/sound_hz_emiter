import numpy as np
import time
import logging
from .waveform_generators import WaveformType, WaveformGenerator
import threading
import queue

logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self):
        self.sample_rate = 44100
        self.is_playing = False
        self.frequency = 440.0
        self.amplitude = 0.5
        self.wave_type = WaveformType.SINE
        self.audio_thread = None
        self.stop_event = threading.Event()
        self.visualization_callback = None
        self.audio_queue = queue.Queue()
        
    def _audio_thread_func(self):
        import sounddevice as sd
        try:
            stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            stream.start()
            
            while not self.stop_event.is_set():
                try:
                    # Obtener muestras de la cola (hasta 100ms de audio)
                    samples = self.audio_queue.get(timeout=0.1)
                    stream.write(samples)
                    
                    # Notificar visualización
                    if self.visualization_callback:
                        self.visualization_callback(samples)
                except queue.Empty:
                    continue
                    
            stream.stop()
            stream.close()
        except ImportError:
            logger.error("SoundDevice no está disponible. La reproducción de audio no funcionará.")
        except Exception as e:
            logger.error(f"Error en el hilo de audio: {str(e)}")
    
    def _generate_samples(self, duration):
        return WaveformGenerator.generate_samples(
            self.wave_type,
            self.frequency,
            self.amplitude,
            self.sample_rate,
            duration
        )
    
    def start_playback(self):
        if self.is_playing:
            return
            
        self.is_playing = True
        self.stop_event.clear()
        self.audio_thread = threading.Thread(target=self._audio_thread_func, daemon=True)
        self.audio_thread.start()
        
        # Iniciar generación de muestras en otro hilo
        threading.Thread(target=self._generate_audio_samples, daemon=True).start()
    
    def _generate_audio_samples(self):
        chunk_duration = 0.1  # 100ms por chunk
        while self.is_playing:
            samples = self._generate_samples(chunk_duration)
            self.audio_queue.put(samples)
            time.sleep(chunk_duration * 0.8)  # Dejar un pequeño margen
    
    def stop_playback(self):
        if not self.is_playing:
            return
            
        self.is_playing = False
        self.stop_event.set()
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
        
        # Limpiar cola
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def set_waveform(self, wave_type):
        self.wave_type = wave_type
    
    def set_frequency(self, frequency):
        self.frequency = frequency
    
    def set_amplitude(self, amplitude):
        self.amplitude = max(0.0, min(1.0, amplitude))
    
    def set_visualization_callback(self, callback):
        self.visualization_callback = callback