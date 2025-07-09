import numpy as np
import sounddevice as sd
import logging

class AudioEngine:
    def __init__(self, sample_rate=44100, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.stream = None
        self.active_tones = {}
        self.current_buffer = np.zeros(buffer_size, dtype=np.float32)
        self.logger = logging.getLogger('core.audio_engine')
        
    def start_stream(self):
        if self.stream is None or not self.stream.active:
            try:
                self.stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    blocksize=self.buffer_size,
                    channels=1,
                    dtype='float32',
                    callback=self._audio_callback
                )
                self.stream.start()
            except sd.PortAudioError as e:
                self.logger.error(f"Error al iniciar stream de audio: {str(e)}")
                # Intentar con un buffer size por defecto
                try:
                    self.logger.info("Intentando con buffer size por defecto...")
                    self.stream = sd.OutputStream(
                        samplerate=self.sample_rate,
                        channels=1,
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
    
    def add_tone(self, tone_id, frequency, volume):
        self.active_tones[tone_id] = (frequency, volume)
    
    def remove_tone(self, tone_id):
        if tone_id in self.active_tones:
            del self.active_tones[tone_id]
    
    def update_tone(self, tone_id, frequency, volume):
        self.active_tones[tone_id] = (frequency, volume)
    
    def stop_all_tones(self):
        self.active_tones.clear()
    
    def _audio_callback(self, outdata, frames, time, status):
        if status:
            self.logger.error(f"Error en callback de audio: {status}")
        
        try:
            mixed_wave = self._generate_mixed_wave(frames)
            outdata[:] = mixed_wave.reshape(-1, 1)
            self.current_buffer = mixed_wave
        except Exception as e:
            self.logger.error(f"Error en generación de audio: {str(e)}")
            outdata.fill(0)
    
    def _generate_mixed_wave(self, n_frames):
        t = np.linspace(0, n_frames / self.sample_rate, n_frames, endpoint=False)
        mixed_wave = np.zeros(n_frames, dtype=np.float32)
        
        for freq, vol in self.active_tones.values():
            if freq > 0 and vol > 0:
                wave = vol * np.sin(2 * np.pi * freq * t)
                mixed_wave += wave.astype(np.float32)
        
        # Normalizar para evitar clipping
        max_val = np.max(np.abs(mixed_wave)) if np.max(np.abs(mixed_wave)) > 0 else 1
        return mixed_wave / max_val
    
    def calculate_spectrum(self, data=None):
        if data is None:
            data = self.current_buffer
        
        if len(data) == 0:
            return np.array([]), np.array([])
        
        fft_data = np.fft.rfft(data)
        magnitudes = np.abs(fft_data) / len(fft_data)
        freqs = np.fft.rfftfreq(len(data), 1.0 / self.sample_rate)
        return freqs, magnitudes