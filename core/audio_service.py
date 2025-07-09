from PySide6.QtCore import QObject, Signal
import numpy as np
import sounddevice as sd

class AudioService(QObject):
    audio_updated = Signal(np.ndarray)  # For waveform display
    
    def __init__(self):
        super().__init__()
        self.sample_rate = 44100
        self.stream = None
        self.tones = {}  # {id: {'freq': float, 'vol': float, 'type': str, 'pan': float}}
        self.buffer_size = 1024
        self.start_stream()
        
    def start_stream(self):
        if self.stream is None:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,  # Stereo for panning
                callback=self.audio_callback
            )
            self.stream.start()
            
    def add_tone(self, tone_id, frequency, volume, wave_type="Sine", panning=0.0):
        self.tones[tone_id] = {
            'freq': frequency,
            'vol': volume,
            'type': wave_type,
            'pan': panning
        }
        
    def update_tone(self, tone_id, frequency=None, volume=None, 
                   wave_type=None, panning=None):
        if tone_id in self.tones:
            if frequency is not None:
                self.tones[tone_id]['freq'] = frequency
            if volume is not None:
                self.tones[tone_id]['vol'] = volume
            if wave_type is not None:
                self.tones[tone_id]['type'] = wave_type
            if panning is not None:
                self.tones[tone_id]['pan'] = panning
                
    def remove_tone(self, tone_id):
        if tone_id in self.tones:
            del self.tones[tone_id]
            
    def stop_all_tones(self):
        self.tones.clear()
        
    def generate_wave(self, tone, length):
        freq = tone['freq']
        vol = tone['vol']
        wave_type = tone['type']
        
        if wave_type == "Sine":
            return vol * np.sin(2 * np.pi * freq * np.arange(length)/self.sample_rate)
        elif wave_type == "Square":
            return vol * np.sign(np.sin(2 * np.pi * freq * np.arange(length)/self.sample_rate))
        elif wave_type == "Triangle":
            return vol * (2/np.pi) * np.arcsin(np.sin(2 * np.pi * freq * np.arange(length)/self.sample_rate))
        elif wave_type == "Sawtooth":
            return vol * (2/np.pi) * np.arctan(np.tan(np.pi * freq * np.arange(length)/self.sample_rate))
        elif wave_type == "White Noise":
            return vol * np.random.uniform(-1, 1, length)
        elif wave_type == "Pink Noise":
            # Simplified pink noise generation
            white = np.random.uniform(-1, 1, length)
            b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
            a = [1, -2.494956002, 2.017265875, -0.522189400]
            return vol * np.convolve(white, b, mode='same') / np.convolve(np.ones_like(white), a, mode='same')
        elif wave_type == "Brown Noise":
            white = np.random.uniform(-1, 1, length)
            return vol * np.cumsum(white) / np.max(np.abs(np.cumsum(white)))
        else:
            return np.zeros(length)
            
    def apply_panning(self, mono_signal, pan_value):
        """Convert mono to stereo with panning (-1 = left, 0 = center, 1 = right)"""
        left_gain = np.sqrt(0.5 * (1 - pan_value))
        right_gain = np.sqrt(0.5 * (1 + pan_value))
        return np.column_stack((left_gain * mono_signal, right_gain * mono_signal))
        
    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)
            
        if not self.tones:
            outdata.fill(0)
            self.audio_updated.emit(np.zeros(frames))
            return
            
        # Generate mixed signal
        mixed = np.zeros((frames, 2))  # Stereo
        
        for tone_id, tone in self.tones.items():
            mono_wave = self.generate_wave(tone, frames)
            stereo_wave = self.apply_panning(mono_wave, tone['pan'])
            mixed += stereo_wave
            
        # Clip to prevent overflow
        mixed = np.clip(mixed, -1, 1)
        outdata[:] = mixed
        
        # Emit left channel for visualization
        self.audio_updated.emit(mixed[:, 0])