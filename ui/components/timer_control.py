"""
Control de temporizador simple
"""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QSpinBox, QLabel)
from PySide6.QtCore import QTimer, Signal

class TimerControl(QGroupBox):
    """Control de temporizador básico"""
    
    timer_finished = Signal()
    timer_started = Signal()
    timer_stopped = Signal()
    
    def __init__(self):
        super().__init__("⏰ Temporizador")
        self.timer = QTimer()
        self.remaining_time = 0
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Configuración de tiempo
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Minutos:"))
        
        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(1, 120)
        self.time_spinbox.setValue(25)
        self.time_spinbox.setSuffix(" min")
        time_layout.addWidget(self.time_spinbox)
        
        layout.addLayout(time_layout)
        
        # Display de tiempo restante
        self.time_display = QLabel("25:00")
        self.time_display.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d4;")
        layout.addWidget(self.time_display)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ Iniciar")
        self.stop_button = QPushButton("⏹ Detener")
        self.stop_button.setEnabled(False)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        
        layout.addLayout(buttons_layout)
    
    def connect_signals(self):
        self.timer.timeout.connect(self.update_timer)
        self.start_button.clicked.connect(self.start_timer)
        self.stop_button.clicked.connect(self.stop_timer)
        self.time_spinbox.valueChanged.connect(self.update_display)
    
    def start_timer(self):
        self.remaining_time = self.time_spinbox.value() * 60
        self.timer.start(1000)  # 1 segundo
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.time_spinbox.setEnabled(False)
        self.timer_started.emit()
    
    def stop_timer(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.time_spinbox.setEnabled(True)
        self.update_display()
        self.timer_stopped.emit()
    
    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.timer.stop()
            self.timer_finished.emit()
            self.stop_timer()
        self.update_display_time()
    
    def update_display(self):
        minutes = self.time_spinbox.value()
        self.time_display.setText(f"{minutes:02d}:00")
    
    def update_display_time(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_display.setText(f"{minutes:02d}:{seconds:02d}")
