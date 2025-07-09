from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                              QLabel, QFrame)
from PySide6.QtCore import Qt
from ui.components.frequency_row import FrequencyRow
import numpy as np

class FrequencyControl(QWidget):
    def __init__(self, audio_service):
        super().__init__()
        self.audio_service = audio_service
        self.next_id = 0
        self.rows = []
        self.controls_title = "Frequency Controls"
        self.add_button_text = "Add Frequency"
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel(self.controls_title)
        self.title_label.setStyleSheet("""
            font-weight: bold; 
            color: black;
            background-color: white;
            padding: 5px;
        """)
        layout.addWidget(self.title_label)
        
        # Add frequency button
        self.add_btn = QPushButton(self.add_button_text)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c6cfb; 
                color: white;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #3a5ae8;
            }
        """)
        self.add_btn.clicked.connect(self.add_frequency)
        layout.addWidget(self.add_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #cccccc;")
        layout.addWidget(separator)
        
        # Container for frequency rows
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(5)
        layout.addWidget(self.rows_container)
        
        # Add initial frequency
        self.add_frequency(440)
        
    def update_language(self, controls_text, add_button_text):
        self.controls_title = controls_text
        self.add_button_text = add_button_text
        self.title_label.setText(self.controls_title)
        self.add_btn.setText(self.add_button_text)
        
    def set_light_theme(self):
        self.title_label.setStyleSheet("""
            font-weight: bold; 
            color: black;
            background-color: white;
            padding: 5px;
        """)
        
    def set_dark_theme(self):
        self.title_label.setStyleSheet("""
            font-weight: bold; 
            color: #64b4ff;
            background-color: #353535;
            padding: 5px;
        """)
        
    def add_frequency(self, freq=None):
        if freq is None:
            freq = np.random.randint(100, 2000)
            
        row_id = self.next_id
        self.next_id += 1
        
        row = FrequencyRow(row_id, freq)
        row.playClicked.connect(lambda: self.audio_service.play_tone(
            row_id, row.freq_spin.value(), row.volume_slider.value()/100,
            row.wave_combo.currentText(), row.pan_slider.value()/100))
        row.stopClicked.connect(lambda: self.audio_service.stop_tone(row_id))
        row.removeClicked.connect(self.remove_row)
        
        # Connect other signals
        row.frequencyChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, frequency=val))
        row.volumeChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, volume=val))
        row.waveTypeChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, wave_type=val))
        row.panningChanged.connect(
            lambda id, val: self.audio_service.update_tone(id, panning=val))
        
        self.rows.append(row)
        self.rows_layout.addWidget(row)
        
    def remove_row(self, row_id):
        for i, row in enumerate(self.rows):
            if row.row_id == row_id:
                self.audio_service.remove_tone(row_id)
                row.deleteLater()
                self.rows.pop(i)
                break