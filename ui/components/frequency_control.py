from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QFrame, QHBoxLayout, QScrollArea)
from PySide6.QtCore import Qt
from .frequency_row import FrequencyRow
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
        
        # Title and Add button row
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(5, 5, 5, 5)
        
        self.title_label = QLabel(self.controls_title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(self.title_label)
        
        self.add_btn = QPushButton(self.add_button_text)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c6cfb; 
                color: white;
                padding: 3px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a5ae8;
            }
        """)
        self.add_btn.clicked.connect(self.add_frequency)
        title_layout.addWidget(self.add_btn, alignment=Qt.AlignRight)
        
        layout.addLayout(title_layout)
        
        # Separator - Hacerlo más visible
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("margin: 5px 0; border: 1px solid #ccc;")
        layout.addWidget(separator)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Container for frequency rows
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(5, 5, 5, 5)  # Añadir márgenes
        self.rows_layout.setSpacing(8)
        scroll.setWidget(self.rows_container)
        layout.addWidget(scroll)
        
        # Add initial frequency (440 Hz)
        self.add_frequency(440)
        
    def update_language(self, controls_text, add_button_text, current_language=None):
        self.controls_title = controls_text
        self.add_button_text = add_button_text
        self.title_label.setText(self.controls_title)
        self.add_btn.setText(self.add_button_text)
        
        if current_language is not None:
            for row in self.rows:
                row.change_language(current_language)
        
    def set_light_theme(self):
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")
        for row in self.rows:
            row.set_light_theme()
        
    def set_dark_theme(self):
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #64b4ff;")
        for row in self.rows:
            row.set_dark_theme()
        
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