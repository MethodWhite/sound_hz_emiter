"""
Hilo de audio mejorado con generación real de tonos y ruidos
"""

from PySide6.QtCore import QThread, QMutex, Signal, QTimer
import numpy as np
import time
import threading

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("SoundDevice no disponible - Usando modo simulado")

class AudioThread(QThread):
    """Hilo de audio con generación real de sonidos"""
    
    stats_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.tones = {}
        self.running = False
        self.sample_rate = 44100
        self.buffer_size = 512
        self.master_volume = 0.5
        self.audio_stream = None
        
        # Para estadísticas
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        
        # Buffer de audio
        self.current_buffer = np.zeros((self.buffer_size, 2), dtype=np.float32)
        
        # Generadores de ruido
        self.noise_generators = {
            'white_noise': self._generate_white_noise,
            'pink_noise': self._generate_pink_noise,
            'brown_noise': self._generate_brown_noise
        }
        
        # Estado para ruido rosa y marrón
        self.pink_noise_state = np.zeros(7)
        self.brown_noise_state = 0.0
    
    def start_audio(self):
        """Inicia el sistema de audio"""
        try:
            if SOUNDDEVICE_AVAILABLE:
                # Configurar stream de audio real
                def audio_callback(outdata, frames, time, status):
                    if status:
                        print(f"Audio status: {status}")
                    
                    self.mutex.lock()
                    try:
                        # Generar buffer de audio
                        buffer = self._generate_audio_buffer(frames)
                        outdata[:] = buffer
                    finally:
                        self.mutex.unlock()
                
                self.audio_stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=2,
                    callback=audio_callback,
                    blocksize=self.buffer_size,
                    dtype='float32'
                )
                
                self.audio_stream.start()
                print("🔊 Stream de audio real iniciado")
            else:
                print("🔊 Modo simulado - SoundDevice no disponible")
            
            self.running = True
            self.stats_timer.start(100)  # Actualizar estadísticas cada 100ms
            self.start()  # Iniciar el hilo
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando audio: {e}")
            return False
    
    def stop_audio(self):
        """Detiene el sistema de audio"""
        self.running = False
        self.stats_timer.stop()
        
        if self.audio_stream:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
                print("🔇 Stream de audio detenido")
            except Exception as e:
                print(f"Error deteniendo stream: {e}")
        
        self.tones.clear()
        self.wait()  # Esperar a que termine el hilo
        print("🔇 Audio thread detenido")
    
    def add_tone(self, tone_id, frequency, volume, wave_type, active, panning):
        """Agrega o actualiza un tono"""
        self.mutex.lock()
        try:
            self.tones[tone_id] = {
                'frequency': frequency,
                'volume': volume,
                'wave_type': wave_type.lower(),
                'active': active,
                'panning': panning,
                'phase': 0.0,
                'time': 0.0
            }
            print(f"♪ Tono {tone_id}: {frequency}Hz, {wave_type}, vol:{volume:.2f}, pan:{panning:.2f}")
        finally:
            self.mutex.unlock()
    
    def remove_tone(self, tone_id):
        """Elimina un tono"""
        self.mutex.lock()
        try:
            if tone_id in self.tones:
                del self.tones[tone_id]
                print(f"🗑️ Tono {tone_id} eliminado")
        finally:
            self.mutex.unlock()
    
    def clear_tone_audio(self, tone_id):
        """Limpia el audio de un tono específico (para cambios de tipo)"""
        self.mutex.lock()
        try:
            if tone_id in self.tones:
                self.tones[tone_id]['phase'] = 0.0
                self.tones[tone_id]['time'] = 0.0
        finally:
            self.mutex.unlock()
    
    def set_tone_active(self, tone_id, active):
        """Activa/desactiva un tono"""
        self.mutex.lock()
        try:
            if tone_id in self.tones:
                self.tones[tone_id]['active'] = active
        finally:
            self.mutex.unlock()
    
    def set_master_volume(self, volume):
        """Establece el volumen maestro"""
        self.master_volume = max(0.0, min(1.0, volume))
    
    def _generate_audio_buffer(self, frames):
        """Genera el buffer de audio mezclando todos los tonos activos"""
        buffer = np.zeros((frames, 2), dtype=np.float32)
        
        if not self.tones:
            return buffer
        
        time_step = 1.0 / self.sample_rate
        
        for tone_id, tone in self.tones.items():
            if not tone['active']:
                continue
            
            # Generar muestras para este tono
            tone_buffer = self._generate_tone_buffer(tone, frames, time_step)
            
            # Aplicar panning
            left_volume = (1.0 - max(0, tone['panning'])) * tone['volume']
            right_volume = (1.0 + min(0, tone['panning'])) * tone['volume']
            
            buffer[:, 0] += tone_buffer * left_volume  # Canal izquierdo
            buffer[:, 1] += tone_buffer * right_volume  # Canal derecho
        
        # Aplicar volumen maestro y limitar amplitud
        buffer *= self.master_volume
        buffer = np.clip(buffer, -0.95, 0.95)
        
        return buffer
    
    def _generate_tone_buffer(self, tone, frames, time_step):
        """Genera buffer para un tono específico"""
        wave_type = tone['wave_type']
        frequency = tone['frequency']
        
        # Generar array de tiempo
        t = np.arange(frames) * time_step + tone['time']
        
        if wave_type in self.noise_generators:
            # Generar ruido
            samples = self.noise_generators[wave_type](frames)
        else:
            # Generar formas de onda tradicionales
            if wave_type == 'seno':
                samples = np.sin(2 * np.pi * frequency * t)
            elif wave_type == 'cuadrada':
                samples = np.sign(np.sin(2 * np.pi * frequency * t))
            elif wave_type == 'triángulo':
                samples = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
            elif wave_type == 'sierra':
                samples = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            else:
                # Tipo desconocido, usar seno por defecto
                samples = np.sin(2 * np.pi * frequency * t)
        
        # Actualizar tiempo para continuidad
        tone['time'] += frames * time_step
        
        return samples.astype(np.float32)
    
    def _generate_white_noise(self, frames):
        """Genera ruido blanco"""
        return np.random.normal(0, 0.3, frames)
    
    def _generate_pink_noise(self, frames):
        """Genera ruido rosa usando filtro IIR"""
        output = np.zeros(frames)
        
        for i in range(frames):
            white = np.random.normal(0, 1)
            
            # Filtro IIR para ruido rosa
            self.pink_noise_state[0] = 0.99886 * self.pink_noise_state[0] + white * 0.0555179
            self.pink_noise_state[1] = 0.99332 * self.pink_noise_state[1] + white * 0.0750759
            self.pink_noise_state[2] = 0.96900 * self.pink_noise_state[2] + white * 0.1538520
            self.pink_noise_state[3] = 0.86650 * self.pink_noise_state[3] + white * 0.3104856
            self.pink_noise_state[4] = 0.55000 * self.pink_noise_state[4] + white * 0.5329522
            self.pink_noise_state[5] = -0.7616 * self.pink_noise_state[5] - white * 0.0168980
            
            output[i] = (self.pink_noise_state[0] + self.pink_noise_state[1] + 
                        self.pink_noise_state[2] + self.pink_noise_state[3] + 
                        self.pink_noise_state[4] + self.pink_noise_state[5] + 
                        self.pink_noise_state[6] + white * 0.5362) * 0.11
            
            self.pink_noise_state[6] = white * 0.115926
        
        return output * 0.3
    
    def _generate_brown_noise(self, frames):
        """Genera ruido marrón (Browniano)"""
        output = np.zeros(frames)
        
        for i in range(frames):
            white = np.random.normal(0, 1)
            self.brown_noise_state += white * 0.02
            self.brown_noise_state *= 0.996  # Evitar deriva
            output[i] = self.brown_noise_state
        
        return output * 0.3
    
    def update_stats(self):
        """Actualiza estadísticas en tiempo real"""
        self.mutex.lock()
        try:
            active_tones = [t for t in self.tones.values() if t['active']]
            
            stats = {
                'timestamp': time.time(),
                'active_tones': len(active_tones),
                'total_tones': len(self.tones),
                'master_volume': self.master_volume,
                'sample_rate': self.sample_rate,
                'buffer_size': self.buffer_size,
                'cpu_load': self._estimate_cpu_load(),
                'frequency_spectrum': self._get_frequency_spectrum(active_tones)
            }
            
            self.stats_updated.emit(stats)
        finally:
            self.mutex.unlock()
    
    def _estimate_cpu_load(self):
        """Estimación simple de carga de CPU"""
        # Estimación basada en número de tonos activos
        active_count = sum(1 for t in self.tones.values() if t['active'])
        return min(100, active_count * 5)  # 5% por tono aproximadamente
    
    def _get_frequency_spectrum(self, active_tones):
        """Obtiene el espectro de frecuencias de los tonos activos"""
        spectrum = {}
        for tone in active_tones:
            freq = tone['frequency']
            wave_type = tone['wave_type']
            if wave_type not in ['white_noise', 'pink_noise', 'brown_noise']:
                if freq in spectrum:
                    spectrum[freq] += tone['volume']
                else:
                    spectrum[freq] = tone['volume']
        return spectrum
    
    def run(self):
        """Loop principal del hilo"""
        while self.running:
            time.sleep(0.01)  # 10ms sleep
