import threading
import time
from core.ports import TimerService

class ThreadedTimerService(TimerService):
    def __init__(self):
        self.remaining_seconds = 0
        self.is_running = False
        self.lock = threading.Lock()
        self.timer_thread = None
    
    def start_timer(self, hours: int, minutes: int, seconds: int):
        with self.lock:
            if self.timer_thread and self.is_running:
                return
                
            self.remaining_seconds = hours * 3600 + minutes * 60 + seconds
            self.is_running = True
            
            self.timer_thread = threading.Thread(
                target=self._run_timer, 
                daemon=True
            )
            self.timer_thread.start()
    
    def _run_timer(self):
        while self.remaining_seconds > 0 and self.is_running:
            time.sleep(1)
            with self.lock:
                if self.is_running:
                    self.remaining_seconds -= 1
    
    def stop_timer(self):
        with self.lock:
            self.is_running = False
            self.remaining_seconds = 0
    
    def get_remaining_time(self) -> str:
        with self.lock:
            if self.remaining_seconds <= 0:
                return "00:00:00"
                
            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            seconds = self.remaining_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"