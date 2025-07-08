from .ports import FrequencyRepository, AudioPlayer, TimerService
from .domain import FrequencyConfig, WaveType
from typing import List

class FrequencyManager:
    def __init__(self, repo: FrequencyRepository, player: AudioPlayer):
        self.repo = repo
        self.player = player
    
    def add_frequency(self, wave_type: WaveType, frequency: float) -> FrequencyConfig:
        return self.repo.add(wave_type, frequency)
    
    def update_frequency(self, config: FrequencyConfig):
        self.repo.update(config)
        if config.is_playing:
            self.player.play_frequency(config.id, config.wave_type, config.frequency)
        elif config.is_paused:
            self.player.pause_frequency(config.id)
        else:
            self.player.stop_frequency(config.id)
    
    def remove_frequency(self, freq_id: int):
        self.player.stop_frequency(freq_id)
        self.repo.remove(freq_id)
    
    def get_all_frequencies(self) -> List[FrequencyConfig]:
        return self.repo.get_all()
    
    def toggle_play(self, freq_id: int):
        configs = self.repo.get_all()
        for config in configs:
            if config.id == freq_id:
                if not config.is_playing and not config.is_paused:
                    config.is_playing = True
                elif config.is_playing:
                    config.is_playing = False
                    config.is_paused = True
                else:  # Paused
                    config.is_playing = True
                    config.is_paused = False
                self.update_frequency(config)
                return config

    def stop_frequency(self, freq_id: int):
        configs = self.repo.get_all()
        for config in configs:
            if config.id == freq_id:
                config.is_playing = False
                config.is_paused = False
                config.frequency = 0.0
                config.wave_type = WaveType.SILENCE
                self.update_frequency(config)
                return config

class TimerManager:
    def __init__(self, timer_service: TimerService, frequency_manager: FrequencyManager):
        self.timer_service = timer_service
        self.freq_manager = frequency_manager
    
    def start_timer(self, hours: int, minutes: int, seconds: int):
        self.timer_service.start_timer(hours, minutes, seconds)
    
    def stop_timer(self):
        self.timer_service.stop_timer()
        for config in self.freq_manager.get_all_frequencies():
            if config.is_playing:
                self.freq_manager.toggle_play(config.id)
    
    def get_remaining_time(self) -> str:
        return self.timer_service.get_remaining_time()