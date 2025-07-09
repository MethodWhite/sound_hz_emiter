from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                              QSpinBox, QGroupBox)
from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QColor

class TimerControl(QWidget):
    timerStarted = Signal(int)  # seconds
    timerStopped = Signal()
    
    def __init__(self, audio_service):
        super().__init__()
        self.audio_service = audio_service
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_seconds = 0
        
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        group = QGroupBox("Timer Control")
        group_layout = QHBoxLayout(group)
        
        # Time inputs
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 24)
        group_layout.addWidget(QLabel("H:"))
        group_layout.addWidget(self.hour_spin)
        
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 59)
        group_layout.addWidget(QLabel("M:"))
        group_layout.addWidget(self.min_spin)
        
        self.sec_spin = QSpinBox()
        self.sec_spin.setRange(0, 59)
        group_layout.addWidget(QLabel("S:"))
        group_layout.addWidget(self.sec_spin)
        
        # Buttons
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_btn.clicked.connect(self.start_timer)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_timer)
        
        group_layout.addWidget(self.start_btn)
        group_layout.addWidget(self.stop_btn)
        
        # Timer display
        self.timer_display = QLabel("00:00:00")
        self.timer_display.setStyleSheet("font-size: 16pt; color: #f44336;")
        group_layout.addWidget(self.timer_display)
        
        layout.addWidget(group)
        
    def start_timer(self):
        hours = self.hour_spin.value()
        minutes = self.min_spin.value()
        seconds = self.sec_spin.value()
        
        self.remaining_seconds = hours * 3600 + minutes * 60 + seconds
        if self.remaining_seconds > 0:
            self.timer.start(1000)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.timerStarted.emit(self.remaining_seconds)
            self.timer_display.setStyleSheet("font-size: 16pt; color: #4CAF50;")
            self.update_display()
            
    def stop_timer(self):
        self.timer.stop()
        self.remaining_seconds = 0
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.timerStopped.emit()
        self.timer_display.setStyleSheet("font-size: 16pt; color: #f44336;")
        self.update_display()
        
    def update_timer(self):
        if self.remaining_seconds <= 0:
            self.stop_timer()
            return
            
        self.remaining_seconds -= 1
        self.update_display()
        
    def update_display(self):
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        self.timer_display.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")