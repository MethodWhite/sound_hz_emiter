from PySide6.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, 
                              QPushButton, QSpinBox)
from PySide6.QtCore import QTimer, Signal

class TimerControl(QGroupBox):
    timerStarted = Signal()
    timerStopped = Signal()
    
    def __init__(self, audio_service):
        super().__init__()
        self.audio_service = audio_service
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_seconds = 0
        self.title_text = "Timer Control"
        
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid gray;
                border-radius: 3px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 15, 5, 5)
        layout.setSpacing(5)
        
        # Time inputs
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 24)
        self.hour_spin.setFixedWidth(50)
        layout.addWidget(QLabel("H:"))
        layout.addWidget(self.hour_spin)
        
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 59)
        self.min_spin.setFixedWidth(50)
        layout.addWidget(QLabel("M:"))
        layout.addWidget(self.min_spin)
        
        self.sec_spin = QSpinBox()
        self.sec_spin.setRange(0, 59)
        self.sec_spin.setFixedWidth(50)
        layout.addWidget(QLabel("S:"))
        layout.addWidget(self.sec_spin)
        
        # Buttons
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                min-width: 60px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #3e8e41;
            }
        """)
        self.start_btn.clicked.connect(self.start_timer)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336; 
                color: white; 
                min-width: 60px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_timer)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        
        # Timer display
        self.timer_display = QLabel("00:00:00")
        self.timer_display.setStyleSheet("""
            font-size: 14px; 
            min-width: 80px;
            color: #f44336;
            font-weight: bold;
        """)
        layout.addWidget(self.timer_display)
        
        self.setTitle(self.title_text)
        
    def update_language(self, text):
        self.title_text = text
        self.setTitle(text)
        
    def set_light_theme(self):
        self.setStyleSheet("""
            QGroupBox { 
                color: black;
            }
        """)
        
    def set_dark_theme(self):
        self.setStyleSheet("""
            QGroupBox { 
                color: #64b4ff;
            }
        """)
        
    def start_timer(self):
        hours = self.hour_spin.value()
        minutes = self.min_spin.value()
        seconds = self.sec_spin.value()
        
        self.remaining_seconds = hours * 3600 + minutes * 60 + seconds
        if self.remaining_seconds > 0:
            self.timer.start(1000)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.timer_display.setStyleSheet("""
                font-size: 14px; 
                color: #4CAF50;
                font-weight: bold;
            """)
            self.timerStarted.emit()
            self.update_display()
            
    def stop_timer(self):
        self.timer.stop()
        self.remaining_seconds = 0
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.timerStopped.emit()
        self.timer_display.setStyleSheet("""
            font-size: 14px; 
            color: #f44336;
            font-weight: bold;
        """)
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