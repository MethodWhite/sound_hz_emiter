import pyaudio
import numpy as np
import threading
import time
from core.ports import AudioPlayer
from core.domain import WaveType
from typing import Dict, Tuple
from .gpu_detector import GPUDetector

# Backend de GPU seleccionado al importar
GPU_BACKEND = GPUDetector.select_gpu_backend()

# Implementación para OpenCL
if GPU_BACKEND == "opencl":
    import pyopencl as cl
    import pyopencl.array as cl_array

    class GPUWaveGenerator:
        def __init__(self, sample_rate):
            self.sample_rate = sample_rate
            self.ctx = cl.create_some_context()
            self.queue = cl.CommandQueue(self.ctx)
            self.program = self._build_program()
            
        def _build_program(self):
            source = """
            #define M_PI 3.14159265358979323846f
            
            __kernel void generate_sine(__global float *output, float frequency, int num_samples) {
                int idx = get_global_id(0);
                if (idx < num_samples) {
                    float t = idx / %(sample_rate)f;
                    output[idx] = 0.5 * sin(2 * M_PI * frequency * t);
                }
            }
            
            __kernel void generate_square(__global float *output, float frequency, int num_samples) {
                int idx = get_global_id(0);
                if (idx < num_samples) {
                    float t = idx / %(sample_rate)f;
                    output[idx] = (sin(2 * M_PI * frequency * t) > 0) ? 0.5 : -0.5;
                }
            }
            
            __kernel void generate_triangle(__global float *output, float frequency, int num_samples) {
                int idx = get_global_id(0);
                if (idx < num_samples) {
                    float t = idx / %(sample_rate)f;
                    float phase = fmod(t * frequency, 1.0f);
                    output[idx] = 0.5 * (1.0 - 4.0 * fabs(phase - 0.5));
                }
            }
            
            __kernel void generate_sawtooth(__global float *output, float frequency, int num_samples) {
                int idx = get_global_id(0);
                if (idx < num_samples) {
                    float t = idx / %(sample_rate)f;
                    float phase = fmod(t * frequency, 1.0f);
                    output[idx] = 0.5 * 2.0 * (phase - 0.5);
                }
            }
            
            __kernel void generate_pulse(__global float *output, float frequency, int num_samples) {
                int idx = get_global_id(0);
                if (idx < num_samples) {
                    float t = idx / %(sample_rate)f;
                    float phase = fmod(t * frequency, 1.0f);
                    output[idx] = (phase < 0.1) ? 0.5 : 0.0;
                }
            }
            """ % {'sample_rate': float(self.sample_rate)}
            
            return cl.Program(self.ctx, source).build()
        
        def generate_wave(self, wave_type, frequency, duration):
            num_samples = int(self.sample_rate * duration)
            output = np.zeros(num_samples, dtype=np.float32)
            output_cl = cl_array.zeros(self.queue, num_samples, dtype=np.float32)
            
            # Seleccionar kernel basado en el tipo de onda
            if wave_type == WaveType.SINE:
                kernel = self.program.generate_sine
            elif wave_type == WaveType.SQUARE:
                kernel = self.program.generate_square
            elif wave_type == WaveType.TRIANGULAR:
                kernel = self.program.generate_triangle
            elif wave_type == WaveType.SAWTOOTH:
                kernel = self.program.generate_sawtooth
            elif wave_type == WaveType.PULSE:
                kernel = self.program.generate_pulse
            else:
                # Para ruidos y silencio, usamos CPU
                return self._generate_cpu_wave(wave_type, frequency, duration)
            
            # Ejecutar kernel
            kernel(self.queue, (num_samples,), None, 
                  output_cl.data, np.float32(frequency), np.int32(num_samples))
            
            # Copiar resultado
            output_cl.get(self.queue, output)
            return output
        
        def _generate_cpu_wave(self, wave_type, frequency, duration):
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            if wave_type == WaveType.WHITE_NOISE:
                return 0.1 * np.random.randn(len(t))
            elif wave_type == WaveType.PINK_NOISE:
                white = np.random.randn(len(t))
                pink = np.zeros_like(white)
                b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
                a = [1, -2.494956002, 2.017265875, -0.522189400]
                for i in range(len(white)):
                    if i < 3:
                        pink[i] = white[i]
                    else:
                        pink[i] = (a[0]*white[i] + a[1]*white[i-1] + a[2]*white[i-2] + a[3]*white[i-3] 
                                   - b[1]*pink[i-1] - b[2]*pink[i-2] - b[3]*pink[i-3])
                return 0.1 * pink / np.max(np.abs(pink))
            elif wave_type == WaveType.BROWNIAN_NOISE:
                brown = np.cumsum(np.random.randn(len(t)) * 0.1)
                return 0.1 * brown / np.max(np.abs(brown))
            else:  # SILENCE
                return np.zeros_like(t)

# Implementación de CPU como fallback
else:
    class GPUWaveGenerator:
        def __init__(self, sample_rate):
            self.sample_rate = sample_rate
            
        def generate_wave(self, wave_type, frequency, duration):
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            
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
                    if i < 3:
                        pink[i] = white[i]
                    else:
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
            else:
                return np.zeros_like(t)

class PyAudioPlayer(AudioPlayer):
    SAMPLE_RATE = 44100
    CHUNK_SIZE = 1024
    MAX_FREQUENCIES = 16
    
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.lock = threading.Lock()
        self.active_streams = {}
        self.stop_event = threading.Event()
        self.wave_generator = GPUWaveGenerator(self.SAMPLE_RATE)
        
        # Iniciar worker de audio
        self.worker_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.worker_thread.start()
        
        # Buffer para mezcla
        self.buffer_duration = 0.1  # 100ms
        self.buffer_size = int(self.SAMPLE_RATE * self.buffer_duration)
        
    def _audio_worker(self):
        stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.SAMPLE_RATE,
            output=True,
            frames_per_buffer=self.CHUNK_SIZE
        )
        
        try:
            while not self.stop_event.is_set():
                start_time = time.time()
                
                # Crear buffer de mezcla
                mixed_buffer = np.zeros(self.buffer_size, dtype=np.float32)
                active_count = 0
                
                with self.lock:
                    active_streams = self.active_streams.copy()
                
                # Generar y mezclar ondas
                for (wave_type, frequency) in active_streams.values():
                    if wave_type == WaveType.SILENCE or frequency <= 0:
                        continue
                    
                    wave = self.wave_generator.generate_wave(
                        wave_type, frequency, self.buffer_duration
                    )
                    
                    # Ajustar tamaño si es necesario
                    if len(wave) > len(mixed_buffer):
                        mixed_buffer = np.zeros(len(wave), dtype=np.float32)
                    
                    mixed_buffer[:len(wave)] += wave
                    active_count += 1
                
                # Normalizar si hay múltiples frecuencias
                if active_count > 1:
                    mixed_buffer = np.clip(mixed_buffer / active_count, -1.0, 1.0)
                
                # Reproducir si hay audio
                if active_count > 0:
                    stream.write(mixed_buffer.astype(np.float32).tobytes())
                
                # Control de timing
                elapsed = time.time() - start_time
                sleep_time = max(0, self.buffer_duration - elapsed)
                time.sleep(sleep_time)
                
        except Exception as e:
            print(f"Error en worker de audio: {e}")
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