from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                              QLabel, QFrame)
from .frequency_row import FrequencyRow
import numpy as np

class FrequencyControl(QWidget):
    def __init__(self, audio_service):
        super().__init__()
        self.audio_service = audio_service
        self.next_id = 0
        self.rows = []
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Frequency Controls")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # Add frequency button
        self.add_btn = QPushButton("Add Frequency")
        self.add_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.add_btn.clicked.connect(self.add_frequency)
        layout.addWidget(self.add_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Container for frequency rows
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.rows_container)
        
        # Add initial frequency
        self.add_frequency(440)
        
    def add_frequency(self, freq=None):
        if freq is None:
            # Add a random frequency between 100-2000 Hz
            freq = np.random.randint(100, 2000)
            
        row_id = self.next_id
        self.next_id += 1
        
        row = FrequencyRow(row_id, freq)
        row.playClicked.connect(lambda: self.audio_service.add_tone(
            row_id, row.freq_spin.value(), row.volume_slider.value()/100,
            row.wave_combo.currentText(), row.pan_slider.value()/100))
        row.pauseClicked.connect(lambda: self.audio_service.remove_tone(row_id))
        row.stopClicked.connect(lambda: self.audio_service.remove_tone(row_id))
        row.frequencyChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, frequency=val))
        row.volumeChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, volume=val))
        row.waveTypeChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, wave_type=val))
        row.panningChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, panning=val))
        row.removeClicked.connect(self.remove_row)
        
        self.rows.append(row)
        self.rows_layout.addWidget(row)
        
    def remove_row(self, row_id):
        for i, row in enumerate(self.rows):
            if row.row_id == row_id:
                self.audio_service.remove_tone(row_id)
                row.deleteLater()
                self.rows.pop(i)
                break