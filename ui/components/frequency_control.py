from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from .frequency_row import FrequencyRow

class FrequencyControl(QWidget):
    def __init__(self, audio_service):
        super().__init__()
        self.audio_service = audio_service
        self.frequencies = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        self.rows = {}
        for freq in self.frequencies:
            row = FrequencyRow(freq, freq)
            row.playClicked.connect(self.on_play)
            row.pauseClicked.connect(self.on_pause)
            row.stopClicked.connect(self.on_stop)
            row.volumeChanged.connect(self.on_volume_changed)
            container_layout.addWidget(row)
            self.rows[freq] = row
            
        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
    def on_play(self, freq):
        row = self.rows[freq]
        self.audio_service.play_frequency(freq, freq, row.volume_slider.value()/100)
        
    def on_pause(self, freq):
        self.audio_service.pause_frequency(freq)
        
    def on_stop(self, freq):
        self.audio_service.stop_frequency(freq)
        
    def on_volume_changed(self, freq, volume):
        self.audio_service.set_volume(freq, volume)