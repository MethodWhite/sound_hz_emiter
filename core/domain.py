from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class WaveType(Enum):
    SINE = "Senoideal"
    SQUARE = "Cuadrada"
    TRIANGULAR = "Triangular"
    SAWTOOTH = "Diente de sierra"
    PULSE = "Pulsante"
    WHITE_NOISE = "Ruido Blanco"
    PINK_NOISE = "Ruido Rosa"
    BROWNIAN_NOISE = "Ruido Browniano"
    SILENCE = "Silencio"

@dataclass
class FrequencyConfig:
    id: int
    wave_type: WaveType
    frequency: float
    is_playing: bool = False
    is_paused: bool = False

class TimerState:
    def __init__(self):
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
    
    def start(self, hours: int, minutes: int, seconds: int):
        self.total_seconds = hours * 3600 + minutes * 60 + seconds
        self.remaining_seconds = self.total_seconds
        self.is_running = True
    
    def update(self):
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
        return self.remaining_seconds > 0
    
    def stop(self):
        self.is_running = False