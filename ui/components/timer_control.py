from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox
from PySide6.QtCore import QTimer, Qt

class TimerControl(QWidget):
    def __init__(self, audio_service):
        super().__init__()
        self.audio_service = audio_service
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Temporizador")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Controles de tiempo
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Duración:"))
        
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 3600)
        self.time_input.setValue(60)
        self.time_input.setSuffix(" seg")
        time_layout.addWidget(self.time_input)
        
        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_timer)
        time_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Detener Todo")
        self.stop_button.clicked.connect(self.stop_all)
        time_layout.addWidget(self.stop_button)
        
        layout.addLayout(time_layout)
        
        # Display
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2E7D32;")
        layout.addWidget(self.timer_label)
        
        self.setLayout(layout)
    
    def start_timer(self):
        self.remaining_time = self.time_input.value()
        self.update_display()
        self.timer.start(1000)  # Actualizar cada segundo
    
    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.audio_service.stop_all_tones()
    
    def stop_all(self):
        self.timer.stop()
        self.remaining_time = 0
        self.update_display()
        self.audio_service.stop_all_tones()
    
    def update_display(self):
        mins, secs = divmod(self.remaining_time, 60)
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")
        # Cambiar color cuando el tiempo está por acabarse
        if self.remaining_time < 10:
            self.timer_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #C62828;")
        else:
            self.timer_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2E7D32;")