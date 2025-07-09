from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QSlider, 
                              QPushButton, QDoubleSpinBox, QComboBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon

class FrequencyRow(QWidget):
    playClicked = Signal(int)
    pauseClicked = Signal(int)
    stopClicked = Signal(int)
    volumeChanged = Signal(int, float)
    frequencyChanged = Signal(int, float)
    waveTypeChanged = Signal(int, str)
    panningChanged = Signal(int, float)
    removeClicked = Signal(int)
    
    WAVE_TYPES = ["Sine", "Square", "Triangle", "Sawtooth", 
                 "White Noise", "Pink Noise", "Brown Noise"]
    
    def __init__(self, row_id, frequency=440.0, parent=None):
        super().__init__(parent)
        self.row_id = row_id
        self.is_playing = False
        self.is_paused = False
        
        self.init_ui(frequency)
        
    def init_ui(self, initial_freq):
        layout = QHBoxLayout(self)
        
        # Frequency control
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(1, 20000)
        self.freq_spin.setValue(initial_freq)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.valueChanged.connect(self.on_frequency_changed)
        layout.addWidget(self.freq_spin)
        
        # Wave type selector
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(self.WAVE_TYPES)
        self.wave_combo.currentTextChanged.connect(self.on_wave_type_changed)
        layout.addWidget(self.wave_combo)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(
            lambda: self.volumeChanged.emit(self.row_id, self.volume_slider.value()/100))
        layout.addWidget(QLabel("Vol:"))
        layout.addWidget(self.volume_slider)
        
        # Panning control
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(-100, 100)
        self.pan_slider.setValue(0)
        self.pan_slider.valueChanged.connect(self.on_panning_changed)
        layout.addWidget(QLabel("L"))
        layout.addWidget(self.pan_slider)
        layout.addWidget(QLabel("R"))
        
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
        
        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setStyleSheet("color: red; font-weight: bold;")
        self.remove_btn.clicked.connect(lambda: self.removeClicked.emit(self.row_id))
        
        layout.addWidget(self.play_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.remove_btn)
        
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
        
    def on_frequency_changed(self, value):
        self.frequencyChanged.emit(self.row_id, value)
        
    def on_wave_type_changed(self, value):
        self.waveTypeChanged.emit(self.row_id, value)
        
    def on_panning_changed(self, value):
        self.panningChanged.emit(self.row_id, value/100)