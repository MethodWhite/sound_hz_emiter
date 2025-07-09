import numpy as np
import pytest
from core.audio_engine import AudioEngine

class TestAudioEngine:
    @pytest.fixture
    def engine(self):
        return AudioEngine(sample_rate=44100, buffer_size=1024)
    
    def test_initial_state(self, engine):
        assert len(engine.active_tones) == 0
        assert engine.stream is None
    
    def test_add_tone(self, engine):
        engine.add_tone(1, 440, 0.5)
        assert 1 in engine.active_tones
        assert engine.active_tones[1] == (440, 0.5)
    
    def test_remove_tone(self, engine):
        engine.add_tone(1, 440, 0.5)
        engine.remove_tone(1)
        assert 1 not in engine.active_tones
    
    def test_update_tone(self, engine):
        engine.add_tone(1, 440, 0.5)
        engine.update_tone(1, 880, 0.8)
        assert engine.active_tones[1] == (880, 0.8)
    
    def test_stop_all_tones(self, engine):
        engine.add_tone(1, 440, 0.5)
        engine.add_tone(2, 880, 0.3)
        engine.stop_all_tones()
        assert len(engine.active_tones) == 0
    
    def test_wave_generation(self, engine):
        engine.add_tone(1, 440, 0.5)
        wave = engine._generate_mixed_wave(1024)
        assert wave.dtype == np.float32
        assert len(wave) == 1024
        assert np.max(wave) <= 1.0
        assert np.min(wave) >= -1.0
    
    # Actualizar la prueba de espectro
    def test_spectrum_calculation(self, engine):
        # Crear una señal de prueba
        t = np.linspace(0, 1, 1024)
        test_signal = 0.5 * np.sin(2 * np.pi * 440 * t)
        freqs, mags = engine.calculate_spectrum(test_signal)
        
        assert len(freqs) > 0
        assert len(mags) > 0
        
        # Encontrar el pico más cercano a 440 Hz
        peak_idx = np.argmax(mags)
        peak_freq = freqs[peak_idx]
        assert abs(peak_freq - 440) <= 20  # Permitir margen de error
    
    def test_multitone_generation(self, engine):
        engine.add_tone(1, 440, 0.5)
        engine.add_tone(2, 880, 0.3)
        wave = engine._generate_mixed_wave(1024)
        
        # Verificar que no hay clipping
        assert np.max(np.abs(wave)) <= 1.0

if __name__ == "__main__":
    pytest.main(["-v", "test_audio.py"])