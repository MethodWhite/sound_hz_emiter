import numpy as np
from enum import Enum

class WaveformType(Enum):
    SINE = 0
    SQUARE = 1
    SAWTOOTH = 2
    TRIANGLE = 3
    WHITE_NOISE = 4

class WaveformGenerator:
    @staticmethod
    def generate_samples(wave_type, frequency, amplitude, sample_rate, duration):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        if wave_type == WaveformType.SINE:
            return amplitude * np.sin(2 * np.pi * frequency * t)
        
        elif wave_type == WaveformType.SQUARE:
            return amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        
        elif wave_type == WaveformType.SAWTOOTH:
            return amplitude * 2 * (t * frequency - np.floor(t * frequency + 0.5))
        
        elif wave_type == WaveformType.TRIANGLE:
            return amplitude * (2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5)) - 1))
        
        elif wave_type == WaveformType.WHITE_NOISE:
            return amplitude * np.random.uniform(-1, 1, len(t))
        
        else:
            raise ValueError(f"Unsupported waveform type: {wave_type}")