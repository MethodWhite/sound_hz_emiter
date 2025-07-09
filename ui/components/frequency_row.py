from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QSlider, 
                              QPushButton, QDoubleSpinBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon

class FrequencyRow(QWidget):
    playClicked = Signal(int)
    pauseClicked = Signal(int)
    stopClicked = Signal(int)
    volumeChanged = Signal(int, float)
    
    def __init__(self, row_id, frequency=440.0, parent=None):
        super().__init__(parent)
        self.row_id = row_id
        self.frequency = frequency
        self.is_playing = False
        self.is_paused = False
        
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Frequency label
        self.freq_label = QLabel(f"{self.frequency} Hz")
        self.freq_label.setFixedWidth(80)
        layout.addWidget(self.freq_label)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(
            lambda: self.volumeChanged.emit(self.row_id, self.volume_slider.value()/100))
        layout.addWidget(self.volume_slider)
        
        # Play/Pause/Stop buttons
        self.play_btn = QPushButton()
        self.play_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_btn.clicked.connect(self.on_play)
        
        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.on_pause)
        
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop)
        
        layout.addWidget(self.play_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)
        
    def on_play(self):
        self.is_playing = True
        self.is_paused = False
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.playClicked.emit(self.row_id)
        
    def on_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            self.pauseClicked.emit(self.row_id)
        else:
            self.pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
            self.playClicked.emit(self.row_id)
        
    def on_stop(self):
        self.is_playing = False
        self.is_paused = False
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.stopClicked.emit(self.row_id)