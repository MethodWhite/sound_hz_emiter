import numpy as np
import sounddevice as sd
import logging
from scipy import signal  # Importar todo el módulo signal
import random

class AudioEngine:
    def __init__(self, sample_rate=44100, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.stream = None
        self.active_tones = {}  # {id: (freq, vol, wave_type, panning)}
        self.current_buffer = np.zeros((buffer_size, 2), dtype=np.float32)  # Estéreo
        self.logger = logging.getLogger('core.audio_engine')
        self.pink_noise_state = None
        self.brown_noise_state = 0.0
        
    def start_stream(self):
        if self.stream is None or not self.stream.active:
            try:
                self.stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    blocksize=self.buffer_size,
                    channels=2,  # Estéreo
                    dtype='float32',
                    callback=self._audio_callback
                )
                self.stream.start()
            except sd.PortAudioError as e:
                self.logger.error(f"Error al iniciar stream de audio: {str(e)}")
                try:
                    self.logger.info("Intentando con buffer size por defecto...")
                    self.stream = sd.OutputStream(
                        samplerate=self.sample_rate,
                        channels=2,
                        dtype='float32',
                        callback=self._audio_callback
                    )
                    self.stream.start()
                except Exception as fallback_e:
                    self.logger.critical(f"Error crítico de audio: {str(fallback_e)}")
                    raise
    
    def stop_stream(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream = None
    
    def add_tone(self, tone_id, frequency, volume, wave_type="Seno", panning=0.0):
        self.active_tones[tone_id] = (frequency, volume, wave_type, panning)
    
    def remove_tone(self, tone_id):
        if tone_id in self.active_tones:
            del self.active_tones[tone_id]
    
    def update_tone(self, tone_id, frequency, volume, wave_type="Seno", panning=0.0):
        self.active_tones[tone_id] = (frequency, volume, wave_type, panning)
    
    def stop_all_tones(self):
        self.active_tones.clear()
    
    def _audio_callback(self, outdata, frames, time, status):
        if status:
            self.logger.error(f"Error en callback de audio: {status}")
        
        try:
            mixed_wave = self._generate_mixed_wave(frames)
            outdata[:] = mixed_wave
            self.current_buffer = mixed_wave
        except Exception as e:
            self.logger.error(f"Error en generación de audio: {str(e)}")
            outdata.fill(0)
    
    def _generate_mixed_wave(self, n_frames):
        t = np.linspace(0, n_frames / self.sample_rate, n_frames, endpoint=False)
        mixed_wave = np.zeros((n_frames, 2), dtype=np.float32)  # Estéreo
        
        for tone_id, (freq, vol, wave_type, panning) in self.active_tones.items():
            if vol > 0:  # Solo generar si el volumen es mayor que 0
                # Generar onda mono según el tipo
                if wave_type == "Seno":
                    wave = vol * np.sin(2 * np.pi * freq * t)
                elif wave_type == "Cuadrada":
                    wave = vol * signal.square(2 * np.pi * freq * t)  # Usar signal.square
                elif wave_type == "Triangular":
                    wave = vol * signal.sawtooth(2 * np.pi * freq * t, width=0.5)  # Usar signal.sawtooth
                elif wave_type == "Diente de Sierra":
                    wave = vol * signal.sawtooth(2 * np.pi * freq * t)  # Usar signal.sawtooth
                elif wave_type == "Ruido Blanco":
                    wave = vol * np.random.uniform(-1, 1, n_frames)
                elif wave_type == "Ruido Rosa":
                    wave = vol * self._generate_pink_noise(n_frames)
                elif wave_type == "Ruido Marrón":
                    wave = vol * self._generate_brown_noise(n_frames)
                else:
                    wave = vol * np.sin(2 * np.pi * freq * t)  # Default: seno
                
                # Aplicar panning (0 = centro, -1 = izquierda, 1 = derecha)
                left_gain = np.sqrt(0.5 * (1 - panning))
                right_gain = np.sqrt(0.5 * (1 + panning))
                
                mixed_wave[:, 0] += wave * left_gain
                mixed_wave[:, 1] += wave * right_gain
        
        # Normalizar para evitar clipping
        max_val = np.max(np.abs(mixed_wave)) 
        if max_val > 1.0:
            mixed_wave /= max_val
        
        return mixed_wave
    
    def _generate_pink_noise(self, n_frames):
        # Implementación eficiente de ruido rosa
        if self.pink_noise_state is None:
            self.pink_noise_state = np.zeros(7)
        
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        
        pink = np.zeros(n_frames)
        white = np.random.randn(n_frames)
        
        for i in range(n_frames):
            white_val = white[i]
            self.pink_noise_state[0] = b[0] * white_val + a[0] * self.pink_noise_state[0]
            self.pink_noise_state[1] = b[1] * white_val + a[1] * self.pink_noise_state[1] + self.pink_noise_state[0]
            self.pink_noise_state[2] = b[2] * white_val + a[2] * self.pink_noise_state[2] + self.pink_noise_state[1]
            self.pink_noise_state[3] = b[3] * white_val + a[3] * self.pink_noise_state[3] + self.pink_noise_state[2]
            pink[i] = self.pink_noise_state[3]
        
        # Normalizar y ajustar ganancia
        pink = pink / np.max(np.abs(pink)) * 0.5
        return pink
    
    def _generate_brown_noise(self, n_frames):
        # Ruido marrón (Brownian) - integración de ruido blanco
        white = np.random.uniform(-1, 1, n_frames)
        brown = np.zeros(n_frames)
        
        for i in range(n_frames):
            self.brown_noise_state += 0.02 * white[i]
            # Filtro de fugas para evitar saturación
            self.brown_noise_state *= 0.99
            brown[i] = self.brown_noise_state
        
        # Normalizar
        brown = brown / (np.max(np.abs(brown)) + 1e-9) * 0.5
        return brown
    
    def calculate_spectrum(self, data=None, channel=0):
        if data is None:
            data = self.current_buffer[:, channel]  # Usar canal izquierdo por defecto
        
        if len(data) == 0:
            return np.array([]), np.array([])
        
        fft_data = np.fft.rfft(data)
        magnitudes = np.abs(fft_data) / len(fft_data)
        freqs = np.fft.rfftfreq(len(data), 1.0 / self.sample_rate)
        return freqs, magnitudes