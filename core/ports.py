from abc import ABC, abstractmethod
from typing import List
from .domain import FrequencyConfig, WaveType

class FrequencyRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[FrequencyConfig]:
        pass
    
    @abstractmethod
    def add(self, wave_type: WaveType, frequency: float) -> FrequencyConfig:
        pass
    
    @abstractmethod
    def update(self, config: FrequencyConfig):
        pass
    
    @abstractmethod
    def remove(self, freq_id: int):
        pass

class AudioPlayer(ABC):
    @abstractmethod
    def play_frequency(self, freq_id: int, wave_type: WaveType, frequency: float):
        pass
    
    @abstractmethod
    def pause_frequency(self, freq_id: int):
        pass
    
    @abstractmethod
    def stop_frequency(self, freq_id: int):
        pass
    
    @abstractmethod
    def stop_all(self):
        pass

class TimerService(ABC):
    @abstractmethod
    def start_timer(self, hours: int, minutes: int, seconds: int):
        pass
    
    @abstractmethod
    def stop_timer(self):
        pass
    
    @abstractmethod
    def get_remaining_time(self) -> str:
        pass