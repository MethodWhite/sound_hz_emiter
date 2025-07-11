"""
Control Pomodoro básico
"""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel)
from PySide6.QtCore import QTimer, Signal

class PomodoroControl(QGroupBox):
    """Control Pomodoro con ciclos automáticos"""
    
    work_finished = Signal()
    break_finished = Signal()
    pomodoro_cycle_completed = Signal()
    
    def __init__(self):
        super().__init__("🍅 Pomodoro")
        self.timer = QTimer()
        self.current_phase = "work"  # "work" o "break"
        self.remaining_time = 25 * 60  # 25 minutos
        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Estado actual
        self.phase_label = QLabel("💼 Fase de Trabajo")
        self.phase_label.setStyleSheet("font-weight: bold; color: #28a745;")
        layout.addWidget(self.phase_label)
        
        # Display de tiempo
        self.time_display = QLabel("25:00")
        self.time_display.setStyleSheet("font-size: 16px; font-weight: bold; color: #0078d4;")
        layout.addWidget(self.time_display)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ Iniciar Pomodoro")
        self.pause_button = QPushButton("⏸ Pausar")
        self.reset_button = QPushButton("🔄 Reiniciar")
        
        self.pause_button.setEnabled(False)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.reset_button)
        
        layout.addLayout(buttons_layout)
    
    def connect_signals(self):
        self.timer.timeout.connect(self.update_timer)
        self.start_button.clicked.connect(self.start_pomodoro)
        self.pause_button.clicked.connect(self.pause_pomodoro)
        self.reset_button.clicked.connect(self.reset_pomodoro)
    
    def start_pomodoro(self):
        self.timer.start(1000)
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
    
    def pause_pomodoro(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("▶ Continuar")
            self.start_button.setEnabled(True)
        else:
            self.timer.start(1000)
            self.pause_button.setText("⏸ Pausar")
            self.start_button.setEnabled(False)
    
    def reset_pomodoro(self):
        self.timer.stop()
        self.current_phase = "work"
        self.remaining_time = self.work_time
        self.update_ui_for_phase()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("⏸ Pausar")
    
    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.switch_phase()
        self.update_display()
    
    def switch_phase(self):
        if self.current_phase == "work":
            self.current_phase = "break"
            self.remaining_time = self.break_time
            self.work_finished.emit()
        else:
            self.current_phase = "work"
            self.remaining_time = self.work_time
            self.break_finished.emit()
            self.pomodoro_cycle_completed.emit()
        
        self.update_ui_for_phase()
    
    def update_ui_for_phase(self):
        if self.current_phase == "work":
            self.phase_label.setText("💼 Fase de Trabajo")
            self.phase_label.setStyleSheet("font-weight: bold; color: #28a745;")
        else:
            self.phase_label.setText("☕ Descanso")
            self.phase_label.setStyleSheet("font-weight: bold; color: #ffc107;")
    
    def update_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_display.setText(f"{minutes:02d}:{seconds:02d}")
