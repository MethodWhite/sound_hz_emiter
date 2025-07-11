"""
Control de temporizador mejorado - Con horas, minutos y segundos
"""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QSpinBox, QLabel, QFrame)
from PySide6.QtCore import QTimer, Signal, Qt

class TimerControl(QGroupBox):
    """Control de temporizador con horas, minutos y segundos"""
    
    timer_finished = Signal()
    timer_started = Signal()
    timer_stopped = Signal()
    timer_tick = Signal(str)  # Para estadísticas en tiempo real
    
    def __init__(self):
        super().__init__("⏰ Temporizador Avanzado")
        self.timer = QTimer()
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Frame de configuración
        config_frame = QFrame()
        config_frame.setFrameStyle(QFrame.StyledPanel)
        config_layout = QVBoxLayout(config_frame)
        
        # Título de configuración
        config_title = QLabel("⚙️ Configuración de Tiempo")
        config_title.setStyleSheet("font-weight: bold; color: #0078d4; font-size: 12px;")
        config_layout.addWidget(config_title)
        
        # Controles de tiempo en grid
        time_grid = QHBoxLayout()
        
        # Horas
        hours_layout = QVBoxLayout()
        hours_layout.addWidget(QLabel("Horas"))
        self.hours_spinbox = QSpinBox()
        self.hours_spinbox.setRange(0, 23)
        self.hours_spinbox.setValue(0)
        self.hours_spinbox.setSuffix(" h")
        self.hours_spinbox.setMinimumWidth(70)
        hours_layout.addWidget(self.hours_spinbox)
        time_grid.addLayout(hours_layout)
        
        # Minutos
        minutes_layout = QVBoxLayout()
        minutes_layout.addWidget(QLabel("Minutos"))
        self.minutes_spinbox = QSpinBox()
        self.minutes_spinbox.setRange(0, 59)
        self.minutes_spinbox.setValue(25)
        self.minutes_spinbox.setSuffix(" min")
        self.minutes_spinbox.setMinimumWidth(70)
        minutes_layout.addWidget(self.minutes_spinbox)
        time_grid.addLayout(minutes_layout)
        
        # Segundos
        seconds_layout = QVBoxLayout()
        seconds_layout.addWidget(QLabel("Segundos"))
        self.seconds_spinbox = QSpinBox()
        self.seconds_spinbox.setRange(0, 59)
        self.seconds_spinbox.setValue(0)
        self.seconds_spinbox.setSuffix(" seg")
        self.seconds_spinbox.setMinimumWidth(70)
        seconds_layout.addWidget(self.seconds_spinbox)
        time_grid.addLayout(seconds_layout)
        
        config_layout.addLayout(time_grid)
        layout.addWidget(config_frame)
        
        # Display de tiempo restante
        self.time_display = QLabel("25:00:00")
        self.time_display.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #0078d4; 
            background-color: rgba(0, 120, 212, 0.1);
            border: 2px solid #0078d4;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        """)
        self.time_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_display)
        
        # Barra de progreso visual
        self.progress_label = QLabel("⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(self.progress_label)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ Iniciar Timer")
        self.pause_button = QPushButton("⏸ Pausar")
        self.stop_button = QPushButton("⏹ Detener")
        self.reset_button = QPushButton("🔄 Reiniciar")
        
        # Estilo de botones
        button_style = """
            QPushButton {
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 12px;
                margin: 2px;
            }
        """
        
        for btn in [self.start_button, self.pause_button, self.stop_button, self.reset_button]:
            btn.setStyleSheet(button_style)
        
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.reset_button)
        
        layout.addLayout(buttons_layout)
        
        # Información de estado
        self.status_label = QLabel("⏱️ Timer listo para iniciar")
        self.status_label.setStyleSheet("font-size: 11px; color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
    
    def connect_signals(self):
        self.timer.timeout.connect(self.update_timer)
        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.stop_button.clicked.connect(self.stop_timer)
        self.reset_button.clicked.connect(self.reset_timer)
        
        # Actualizar display cuando cambie la configuración
        self.hours_spinbox.valueChanged.connect(self.update_display_from_config)
        self.minutes_spinbox.valueChanged.connect(self.update_display_from_config)
        self.seconds_spinbox.valueChanged.connect(self.update_display_from_config)
    
    def start_timer(self):
        if not self.is_running:
            # Calcular tiempo total
            hours = self.hours_spinbox.value()
            minutes = self.minutes_spinbox.value()
            seconds = self.seconds_spinbox.value()
            
            self.total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if self.total_seconds <= 0:
                self.status_label.setText("❌ Configura un tiempo válido")
                return
            
            self.remaining_seconds = self.total_seconds
            
        self.timer.start(1000)  # 1 segundo
        self.is_running = True
        
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
        # Deshabilitar configuración
        self.hours_spinbox.setEnabled(False)
        self.minutes_spinbox.setEnabled(False)
        self.seconds_spinbox.setEnabled(False)
        
        self.status_label.setText("▶ Timer en ejecución...")
        self.timer_started.emit()
    
    def pause_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("▶ Continuar")
            self.start_button.setEnabled(True)
            self.status_label.setText("⏸ Timer pausado")
        else:
            self.timer.start(1000)
            self.pause_button.setText("⏸ Pausar")
            self.start_button.setEnabled(False)
            self.status_label.setText("▶ Timer continuando...")
    
    def stop_timer(self):
        self.timer.stop()
        self.is_running = False
        
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("⏸ Pausar")
        
        # Habilitar configuración
        self.hours_spinbox.setEnabled(True)
        self.minutes_spinbox.setEnabled(True)
        self.seconds_spinbox.setEnabled(True)
        
        self.update_display_from_config()
        self.update_progress_bar(0)
        self.status_label.setText("⏹ Timer detenido")
        self.timer_stopped.emit()
    
    def reset_timer(self):
        self.stop_timer()
        self.hours_spinbox.setValue(0)
        self.minutes_spinbox.setValue(25)
        self.seconds_spinbox.setValue(0)
        self.update_display_from_config()
        self.status_label.setText("🔄 Timer reiniciado")
    
    def update_timer(self):
        self.remaining_seconds -= 1
        
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.timer_finished.emit()
            self.stop_timer()
            self.status_label.setText("🎉 ¡Timer completado!")
            return
        
        self.update_display_time()
        self.update_progress_bar()
        
        # Emitir para estadísticas
        self.timer_tick.emit(self.format_time(self.remaining_seconds))
    
    def update_display_from_config(self):
        hours = self.hours_spinbox.value()
        minutes = self.minutes_spinbox.value()
        seconds = self.seconds_spinbox.value()
        total_seconds = hours * 3600 + minutes * 60 + seconds
        self.time_display.setText(self.format_time(total_seconds))
    
    def update_display_time(self):
        self.time_display.setText(self.format_time(self.remaining_seconds))
    
    def format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def update_progress_bar(self, override_progress=None):
        if override_progress is not None:
            progress = override_progress
        else:
            if self.total_seconds > 0:
                progress = 1.0 - (self.remaining_seconds / self.total_seconds)
            else:
                progress = 0
        
        # Barra de progreso visual con bloques
        total_blocks = 10
        filled_blocks = int(progress * total_blocks)
        empty_blocks = total_blocks - filled_blocks
        
        progress_text = "🟦" * filled_blocks + "⬜" * empty_blocks
        self.progress_label.setText(progress_text)
    
    def get_time_statistics(self):
        """Retorna estadísticas del timer para el panel de estadísticas"""
        if self.is_running and self.total_seconds > 0:
            elapsed = self.total_seconds - self.remaining_seconds
            progress = elapsed / self.total_seconds
            return {
                'status': 'running',
                'elapsed': self.format_time(elapsed),
                'remaining': self.format_time(self.remaining_seconds),
                'total': self.format_time(self.total_seconds),
                'progress_percent': int(progress * 100)
            }
        else:
            return {
                'status': 'stopped',
                'elapsed': '00:00:00',
                'remaining': '00:00:00', 
                'total': '00:00:00',
                'progress_percent': 0
            }
