import numpy as np
import pytest
from core.audio_engine import AudioEngine
import time

class TestAudioEngine:
    @pytest.fixture
    def engine(self):
        return AudioEngine(sample_rate=44100, buffer_size=1024)
    
    def test_initial_state(self, engine):
        assert len(engine.active_tones) == 0
        assert engine.stream is None
    
    def test_add_tone(self, engine):
        engine.add_tone(1, 440, 0.5, "Seno", 0.0)
        assert 1 in engine.active_tones
        assert engine.active_tones[1] == (440, 0.5, "Seno", 0.0)
    
    def test_remove_tone(self, engine):
        engine.add_tone(1, 440, 0.5, "Seno", 0.0)
        engine.remove_tone(1)
        assert 1 not in engine.active_tones
    
    def test_update_tone(self, engine):
        engine.add_tone(1, 440, 0.5, "Seno", 0.0)
        engine.update_tone(1, 880, 0.8, "Cuadrada", -0.5)
        assert engine.active_tones[1] == (880, 0.8, "Cuadrada", -0.5)
    
    def test_stop_all_tones(self, engine):
        engine.add_tone(1, 440, 0.5, "Seno", 0.0)
        engine.add_tone(2, 880, 0.3, "Triangular", 0.5)
        engine.stop_all_tones()
        assert len(engine.active_tones) == 0
    
    def test_wave_generation(self, engine):
        engine.add_tone(1, 440, 0.5, "Seno", 0.0)
        wave = engine._generate_mixed_wave(1024)
        assert wave.dtype == np.float32
        assert wave.shape == (1024, 2)
        assert np.max(wave) <= 1.0
        assert np.min(wave) >= -1.0
    
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
    
    def test_multiple_tones(self, engine):
        engine.add_tone(1, 440, 0.3, "Seno", -0.5)
        engine.add_tone(2, 880, 0.3, "Cuadrada", 0.5)
        engine.add_tone(3, 0, 0.2, "Ruido Blanco", 0.0)
        
        wave = engine._generate_mixed_wave(1024)
        assert wave.shape == (1024, 2)
        assert np.max(np.abs(wave)) <= 1.0
    
    def test_pink_noise(self, engine):
        engine.add_tone(1, 0, 0.5, "Ruido Rosa", 0.0)
        wave = engine._generate_mixed_wave(1024)
        assert wave.shape == (1024, 2)
        assert np.max(np.abs(wave)) <= 1.0
    
    def test_brown_noise(self, engine):
        engine.add_tone(1, 0, 0.5, "Ruido Marrón", 0.0)
        wave = engine._generate_mixed_wave(1024)
        assert wave.shape == (1024, 2)
        assert np.max(np.abs(wave)) <= 1.0
    
    def test_panning(self, engine):
        engine.add_tone(1, 440, 0.5, "Seno", -1.0)  # Todo izquierda
        wave = engine._generate_mixed_wave(1024)
        assert np.max(np.abs(wave[:, 1])) < 0.01  # Canal derecho casi silencioso
        
        engine.update_tone(1, 440, 0.5, "Seno", 1.0)  # Todo derecha
        wave = engine._generate_mixed_wave(1024)
        assert np.max(np.abs(wave[:, 0])) < 0.01  # Canal izquierdo casi silencioso
        
        engine.update_tone(1, 440, 0.5, "Seno", 0.0)  # Centro
        wave = engine._generate_mixed_wave(1024)
        assert np.allclose(wave[:, 0], wave[:, 1], atol=0.01)  # Canales similares

if __name__ == "__main__":
    pytest.main(["-v", "test_audio.py"])