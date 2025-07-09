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
    
    def __init__(self, row_id, frequency=1.0, parent=None):
        super().__init__(parent)
        self.row_id = row_id
        self.is_playing = False
        self.current_language = "en"
        self.init_ui(frequency)
        
    def init_ui(self, initial_freq):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 8, 5, 8)
        layout.setSpacing(10)
        
        # Frequency control
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(1, 20000)
        self.freq_spin.setValue(initial_freq)
        self.freq_spin.setSuffix(" Hz")
        self.freq_spin.setFixedWidth(100)
        self.freq_spin.valueChanged.connect(self.on_frequency_changed)
        layout.addWidget(self.freq_spin)
        
        # Wave type selector
        self.wave_combo = QComboBox()
        self.update_wave_types()
        self.wave_combo.setFixedWidth(120)
        self.wave_combo.currentTextChanged.connect(self.on_wave_type_changed)
        layout.addWidget(self.wave_combo)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(80)
        layout.addWidget(QLabel("Vol:"))
        layout.addWidget(self.volume_slider)
        
        # Panning control
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(-100, 100)
        self.pan_slider.setValue(0)
        self.pan_slider.setFixedWidth(100)
        layout.addWidget(QLabel("L"))
        layout.addWidget(self.pan_slider)
        layout.addWidget(QLabel("R"))
        
        # Play/Pause button
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_pause_btn.setFixedSize(30, 30)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c6cfb; 
                color: white;
                border: none;
                border-radius: 4px;
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
        self.stop_btn.setFixedSize(30, 30)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c6cfb; 
                color: white;
                border: none;
                border-radius: 4px;
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
        self.remove_btn.setFixedSize(30, 30)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
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
        
    def on_frequency_changed(self, value):
        self.frequencyChanged.emit(self.row_id, value)
        
    def on_wave_type_changed(self, value):
        self.waveTypeChanged.emit(self.row_id, value)
        
    def on_panning_changed(self, value):
        self.panningChanged.emit(self.row_id, value/100)
        
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
        
    def set_light_theme(self):
        """Restablece los estilos a los valores por defecto del sistema"""
        self.setStyleSheet("")
        
        # Resetear estilos para cada tipo de widget por separado
        for spinbox in self.findChildren(QDoubleSpinBox):
            spinbox.setStyleSheet("")
        for combobox in self.findChildren(QComboBox):
            combobox.setStyleSheet("")
        for label in self.findChildren(QLabel):
            label.setStyleSheet("")
        
    def set_dark_theme(self):
        """Aplica estilos para el tema oscuro"""
        self.setStyleSheet("""
            QWidget {
                background-color: #353535;
            }
            QLabel {
                color: #64b4ff;
            }
            QDoubleSpinBox, QComboBox {
                background-color: #252525;
                color: #64b4ff;
                border: 1px solid #555;
            }
        """)