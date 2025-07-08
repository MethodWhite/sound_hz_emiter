from PySide6.QtWidgets import (
    QWidget, QSlider, QLineEdit, QLabel, QHBoxLayout, 
    QComboBox, QPushButton, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from utils import constants
import math
import pyqtgraph as pg
import numpy as np

class FrequencyControl(QWidget):
    valueChanged = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Logarithmic slider for better frequency control
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.valueChanged.connect(self._update_value)
        
        # Precise input field
        self.input = QLineEdit()
        self.input.setText(str(constants.DEFAULT_FREQUENCY))
        self.input.setFixedWidth(80)
        self.input.setAlignment(Qt.AlignRight)
        self.input.returnPressed.connect(self._text_updated)
        
        # Unit label
        unit = QLabel("Hz")
        
        layout.addWidget(self.slider, 70)
        layout.addWidget(self.input, 15)
        layout.addWidget(unit, 5)
        self.setLayout(layout)
        
        # Set initial value
        self._text_updated()
    
    def set_value(self, frequency):
        self.input.setText(f"{frequency:.2f}")
        self._text_updated()
    
    def _update_value(self, slider_val):
        # Convert logarithmic scale to linear frequency
        freq = constants.MIN_FREQUENCY * (10 ** (slider_val / 333))
        self.input.setText(f"{freq:.2f}")
        self.valueChanged.emit(freq)
    
    def _text_updated(self):
        text = self.input.text()
        try:
            freq = float(text)
            if freq < constants.MIN_FREQUENCY:
                freq = constants.MIN_FREQUENCY
                self.input.setText(f"{freq:.2f}")
            elif freq > constants.MAX_FREQUENCY:
                freq = constants.MAX_FREQUENCY
                self.input.setText(f"{freq:.2f}")
                
            # Convert to logarithmic scale
            slider_val = 333 * math.log10(freq / constants.MIN_FREQUENCY)
            self.slider.setValue(int(slider_val))
            self.valueChanged.emit(freq)
            self.input.setStyleSheet("")
        except ValueError:
            self.input.setStyleSheet("border: 1px solid red;")

class AmplitudeControl(QWidget):
    valueChanged = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(int(constants.DEFAULT_AMPLITUDE * 100))
        self.slider.valueChanged.connect(self._update_value)
        
        self.input = QLineEdit()
        self.input.setText(f"{constants.DEFAULT_AMPLITUDE:.2f}")
        self.input.setFixedWidth(60)
        self.input.setAlignment(Qt.AlignRight)
        self.input.returnPressed.connect(self._text_updated)
        
        layout.addWidget(self.slider, 80)
        layout.addWidget(self.input, 20)
        self.setLayout(layout)
        
    def set_value(self, amplitude):
        self.input.setText(f"{amplitude:.2f}")
        self._text_updated()
    
    def _update_value(self, slider_val):
        amp = slider_val / 100.0
        self.input.setText(f"{amp:.2f}")
        self.valueChanged.emit(amp)
    
    def _text_updated(self):
        text = self.input.text()
        try:
            amp = float(text)
            if amp < constants.MIN_AMPLITUDE:
                amp = constants.MIN_AMPLITUDE
                self.input.setText(f"{amp:.2f}")
            elif amp > constants.MAX_AMPLITUDE:
                amp = constants.MAX_AMPLITUDE
                self.input.setText(f"{amp:.2f}")
                
            self.slider.setValue(int(amp * 100))
            self.valueChanged.emit(amp)
            self.input.setStyleSheet("")
        except ValueError:
            self.input.setStyleSheet("border: 1px solid red;")

class WaveformSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(constants.WAVEFORM_TYPES)
        self.setCurrentIndex(0)
        
    def get_waveform_type(self):
        return self.currentIndex()

class PlaybackControl(QWidget):
    playClicked = Signal()
    stopClicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.setFixedWidth(100)
        self.play_button.clicked.connect(self.playClicked)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(100)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stopClicked)
        
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)
    
    def set_playing(self, is_playing):
        self.play_button.setEnabled(not is_playing)
        self.stop_button.setEnabled(is_playing)

class VisualizationWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground(None)
        self.plot_item = self.getPlotItem()
        self.plot_item.hideAxis('bottom')
        self.plot_item.hideAxis('left')
        self.curve = self.plot_item.plot(pen='#1f77b4')
        self.data = np.zeros(1000)
        
    def update_waveform(self, samples):
        if len(samples) > 0:
            # Downsample para mejor rendimiento
            step = max(1, len(samples) // 1000)
            self.data = samples[::step]
            self.curve.setData(self.data)