from PySide6.QtWidgets import (
    QWidget, QSlider, QLineEdit, QLabel, QHBoxLayout, 
    QComboBox, QPushButton, QVBoxLayout, QGroupBox,
    QListWidget, QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
import math
import pyqtgraph as pg
import numpy as np

from utils.constants import (
    MIN_FREQUENCY, MAX_FREQUENCY, DEFAULT_FREQUENCY,
    MIN_AMPLITUDE, MAX_AMPLITUDE, DEFAULT_AMPLITUDE,
    WAVEFORM_TYPES
)

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
        self.input.setText(str(DEFAULT_FREQUENCY))
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
        freq = MIN_FREQUENCY * (10 ** (slider_val / 333))
        self.input.setText(f"{freq:.2f}")
        self.valueChanged.emit(freq)
    
    def _text_updated(self):
        text = self.input.text()
        try:
            freq = float(text)
            if freq < MIN_FREQUENCY:
                freq = MIN_FREQUENCY
                self.input.setText(f"{freq:.2f}")
            elif freq > MAX_FREQUENCY:
                freq = MAX_FREQUENCY
                self.input.setText(f"{freq:.2f}")
                
            # Convert to logarithmic scale
            slider_val = 333 * math.log10(freq / MIN_FREQUENCY)
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
        self.slider.setValue(int(DEFAULT_AMPLITUDE * 100))
        self.slider.valueChanged.connect(self._update_value)
        
        self.input = QLineEdit()
        self.input.setText(f"{DEFAULT_AMPLITUDE:.2f}")
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
            if amp < MIN_AMPLITUDE:
                amp = MIN_AMPLITUDE
                self.input.setText(f"{amp:.2f}")
            elif amp > MAX_AMPLITUDE:
                amp = MAX_AMPLITUDE
                self.input.setText(f"{amp:.2f}")
                
            self.slider.setValue(int(amp * 100))
            self.valueChanged.emit(amp)
            self.input.setStyleSheet("")
        except ValueError:
            self.input.setStyleSheet("border: 1px solid red;")

class WaveformSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(WAVEFORM_TYPES)
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

class TimerControl(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Duration (seconds)")
        self.input.setFixedWidth(150)
        self.input.returnPressed.connect(self._text_updated)
        
        self.timer_label = QLabel("0:00")
        self.timer_label.setFixedWidth(60)
        
        layout.addWidget(QLabel("Timer:"))
        layout.addWidget(self.input)
        layout.addWidget(self.timer_label)
        self.setLayout(layout)
    
    def get_duration(self):
        text = self.input.text()
        try:
            duration = int(text)
            return duration if duration > 0 else 0
        except ValueError:
            return 0
    
    def update_timer(self, seconds):
        mins, secs = divmod(seconds, 60)
        self.timer_label.setText(f"{mins}:{secs:02d}")
    
    def _text_updated(self):
        text = self.input.text()
        try:
            duration = int(text)
            if duration <= 0:
                raise ValueError("Duration must be positive")
            self.valueChanged.emit(duration)
            self.input.setStyleSheet("")
        except ValueError:
            self.input.setStyleSheet("border: 1px solid red;")

class FrequencyListControl(QGroupBox):
    addFrequency = Signal(float)
    removeFrequency = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__("Additional Frequencies", parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Lista de frecuencias
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.list_widget)
        
        # Controles para añadir/eliminar
        control_layout = QHBoxLayout()
        
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText("Frequency (Hz)")
        self.freq_input.setFixedWidth(120)
        
        self.add_button = QPushButton("Add")
        self.add_button.setFixedWidth(80)
        self.add_button.clicked.connect(self._add_frequency)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setFixedWidth(80)
        self.remove_button.clicked.connect(self._remove_frequency)
        
        control_layout.addWidget(self.freq_input)
        control_layout.addWidget(self.add_button)
        control_layout.addWidget(self.remove_button)
        
        layout.addLayout(control_layout)
        self.setLayout(layout)
    
    def _add_frequency(self):
        text = self.freq_input.text()
        try:
            freq = float(text)
            if MIN_FREQUENCY <= freq <= MAX_FREQUENCY:
                self.list_widget.addItem(f"{freq} Hz")
                self.addFrequency.emit(freq)
                self.freq_input.clear()
                self.freq_input.setStyleSheet("")
            else:
                raise ValueError("Frequency out of range")
        except ValueError:
            self.freq_input.setStyleSheet("border: 1px solid red;")
    
    def _remove_frequency(self):
        selected = self.list_widget.currentRow()
        if selected >= 0:
            item = self.list_widget.takeItem(selected)
            freq = float(item.text().split()[0])
            self.removeFrequency.emit(freq)

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