from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QSlider, 
                              QPushButton, QDoubleSpinBox, QComboBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon

class FrequencyRow(QWidget):
    playClicked = Signal(int)
    stopClicked = Signal(int)
    removeClicked = Signal(int)
    frequencyChanged = Signal(int, float)
    volumeChanged = Signal(int, float)
    waveTypeChanged = Signal(int, str)
    panningChanged = Signal(int, float)
    
    WAVE_TYPES_EN = ["Sine", "Square", "Triangle", "Sawtooth", 
                    "White Noise", "Pink Noise", "Brown Noise"]
    WAVE_TYPES_ES = ["Seno", "Cuadrada", "Triangular", "Diente de Sierra",
                    "Ruido Blanco", "Ruido Rosa", "Ruido Marrón"]
    
    def __init__(self, row_id, frequency=440.0, parent=None):
        super().__init__(parent)
        self.row_id = row_id
        self.is_playing = False
        self.current_language = "en"
        
        self.init_ui(frequency)
        
    def init_ui(self, initial_freq):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Frequency control
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(1, 20000)
        self.freq_spin.setValue(initial_freq)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.setSingleStep(1)
        self.freq_spin.setFixedWidth(80)
        self.freq_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                color: black;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 15px;
                background-color: white;
            }
            QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
                color: black;
            }
        """)
        self.freq_spin.valueChanged.connect(self.on_frequency_changed)
        layout.addWidget(self.freq_spin)
        
        # Wave type selector
        self.wave_combo = QComboBox()
        self.update_wave_types()
        self.wave_combo.setFixedWidth(100)
        self.wave_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
        """)
        self.wave_combo.currentTextChanged.connect(self.on_wave_type_changed)
        layout.addWidget(self.wave_combo)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #cccccc;
                height: 5px;
            }
            QSlider::handle:horizontal {
                background: #4c6cfb;
                width: 10px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #4c6cfb;
            }
        """)
        self.volume_slider.valueChanged.connect(
            lambda: self.volumeChanged.emit(self.row_id, self.volume_slider.value()/100))
        layout.addWidget(QLabel("Vol:"))
        layout.addWidget(self.volume_slider)
        
        # Panning control
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(-100, 100)
        self.pan_slider.setValue(0)
        self.pan_slider.setFixedWidth(80)
        self.pan_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c6cfb, stop:0.5 white, stop:1 #4c6cfb);
                height: 5px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 10px;
                margin: -5px 0;
                border: 1px solid #777;
            }
        """)
        self.pan_slider.valueChanged.connect(self.on_panning_changed)
        layout.addWidget(QLabel("L"))
        layout.addWidget(self.pan_slider)
        layout.addWidget(QLabel("R"))
        
        # Play/Pause button
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c6cfb; 
                color: white;
                min-width: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a5ae8;
            }
        """)
        self.play_pause_btn.clicked.connect(self.on_play_pause)
        layout.addWidget(self.play_pause_btn)
        
        # Stop button
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c6cfb; 
                color: white;
                min-width: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a5ae8;
            }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop)
        layout.addWidget(self.stop_btn)
        
        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c6cfb; 
                color: white;
                font-weight: bold;
                min-width: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3a5ae8;
            }
        """)
        self.remove_btn.clicked.connect(lambda: self.removeClicked.emit(self.row_id))
        layout.addWidget(self.remove_btn)
        
    def update_wave_types(self):
        self.wave_combo.clear()
        if self.current_language == "en":
            self.wave_combo.addItems(self.WAVE_TYPES_EN)
        else:
            self.wave_combo.addItems(self.WAVE_TYPES_ES)
        
    def change_language(self, language):
        self.current_language = language
        self.update_wave_types()
        
    def on_play_pause(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
            self.playClicked.emit(self.row_id)
        else:
            self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
            self.stopClicked.emit(self.row_id)
        self.stop_btn.setEnabled(self.is_playing)
        
    def on_stop(self):
        self.is_playing = False
        self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.stop_btn.setEnabled(False)
        self.stopClicked.emit(self.row_id)
        
    def on_frequency_changed(self, value):
        self.frequencyChanged.emit(self.row_id, value)
        
    def on_wave_type_changed(self, value):
        self.waveTypeChanged.emit(self.row_id, value)
        
    def on_panning_changed(self, value):
        self.panningChanged.emit(self.row_id, value/100)