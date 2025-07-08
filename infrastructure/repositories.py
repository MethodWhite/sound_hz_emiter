from core.ports import FrequencyRepository
from core.domain import FrequencyConfig, WaveType
from typing import List

class InMemoryFrequencyRepository(FrequencyRepository):
    def __init__(self):
        self.configs = []
        self.next_id = 1
    
    def get_all(self) -> List[FrequencyConfig]:
        return self.configs.copy()
    
    def add(self, wave_type: WaveType, frequency: float) -> FrequencyConfig:
        config = FrequencyConfig(
            id=self.next_id,
            wave_type=wave_type,
            frequency=frequency
        )
        self.configs.append(config)
        self.next_id += 1
        return config
    
    def update(self, config: FrequencyConfig):
        for i, c in enumerate(self.configs):
            if c.id == config.id:
                self.configs[i] = config
                break
    
    def remove(self, freq_id: int):
        self.configs = [c for c in self.configs if c.id != freq_id]