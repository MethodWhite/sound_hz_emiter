from infrastructure.repositories import InMemoryFrequencyRepository
from infrastructure.audio_player import PyAudioPlayer
from infrastructure.timer_service import ThreadedTimerService
from core.use_cases import FrequencyManager, TimerManager
from ui.main_window import MainApplication

def main():
    freq_repo = InMemoryFrequencyRepository()
    audio_player = PyAudioPlayer()
    timer_service = ThreadedTimerService()
    
    freq_manager = FrequencyManager(freq_repo, audio_player)
    timer_manager = TimerManager(timer_service, freq_manager)
    
    app = MainApplication(freq_manager, timer_manager)
    app.mainloop()

if __name__ == "__main__":
    main()