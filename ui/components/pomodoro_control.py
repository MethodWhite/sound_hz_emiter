"""
Control Pomodoro completo con múltiples tipos y configuraciones
"""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QComboBox, QSpinBox, QFrame)
from PySide6.QtCore import QTimer, Signal, Qt

class PomodoroControl(QGroupBox):
    """Control Pomodoro avanzado con múltiples tipos"""
    
    work_finished = Signal()
    break_finished = Signal()
    long_break_finished = Signal()
    pomodoro_cycle_completed = Signal()
    pomodoro_tick = Signal(str, str)  # phase, time_remaining
    
    def __init__(self):
        super().__init__("🍅 Sistema Pomodoro Avanzado")
        self.timer = QTimer()
        self.current_phase = "work"  # "work", "short_break", "long_break"
        self.remaining_time = 25 * 60
        self.cycles_completed = 0
        self.is_running = False
        self.total_phase_time = 25 * 60
        
        # Configuraciones por defecto
        self.pomodoro_types = {
            "Clásico": {"work": 25, "short_break": 5, "long_break": 15, "cycles": 4},
            "Extendido": {"work": 50, "short_break": 10, "long_break": 30, "cycles": 3},
            "Intensivo": {"work": 90, "short_break": 20, "long_break": 45, "cycles": 2},
            "Personalizado": {"work": 25, "short_break": 5, "long_break": 15, "cycles": 4}
        }
        
        self.setup_ui()
        self.connect_signals()
        self.update_config_from_type()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Frame de configuración
        config_frame = QFrame()
        config_frame.setFrameStyle(QFrame.StyledPanel)
        config_layout = QVBoxLayout(config_frame)
        
        # Título de configuración
        config_title = QLabel("⚙️ Configuración Pomodoro")
        config_title.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 12px;")
        config_layout.addWidget(config_title)
        
        # Selector de tipo de Pomodoro
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(list(self.pomodoro_types.keys()))
        self.type_combo.setMinimumWidth(120)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        
        config_layout.addLayout(type_layout)
        
        # Configuraciones personalizables
        times_grid = QHBoxLayout()
        
        # Trabajo
        work_layout = QVBoxLayout()
        work_layout.addWidget(QLabel("Trabajo"))
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setRange(1, 120)
        self.work_spinbox.setValue(25)
        self.work_spinbox.setSuffix(" min")
        self.work_spinbox.setMinimumWidth(70)
        work_layout.addWidget(self.work_spinbox)
        times_grid.addLayout(work_layout)
        
        # Descanso corto
        short_break_layout = QVBoxLayout()
        short_break_layout.addWidget(QLabel("Desc. Corto"))
        self.short_break_spinbox = QSpinBox()
        self.short_break_spinbox.setRange(1, 60)
        self.short_break_spinbox.setValue(5)
        self.short_break_spinbox.setSuffix(" min")
        self.short_break_spinbox.setMinimumWidth(70)
        short_break_layout.addWidget(self.short_break_spinbox)
        times_grid.addLayout(short_break_layout)
        
        # Descanso largo
        long_break_layout = QVBoxLayout()
        long_break_layout.addWidget(QLabel("Desc. Largo"))
        self.long_break_spinbox = QSpinBox()
        self.long_break_spinbox.setRange(1, 120)
        self.long_break_spinbox.setValue(15)
        self.long_break_spinbox.setSuffix(" min")
        self.long_break_spinbox.setMinimumWidth(70)
        long_break_layout.addWidget(self.long_break_spinbox)
        times_grid.addLayout(long_break_layout)
        
        # Ciclos
        cycles_layout = QVBoxLayout()
        cycles_layout.addWidget(QLabel("Ciclos"))
        self.cycles_spinbox = QSpinBox()
        self.cycles_spinbox.setRange(1, 10)
        self.cycles_spinbox.setValue(4)
        self.cycles_spinbox.setMinimumWidth(70)
        cycles_layout.addWidget(self.cycles_spinbox)
        times_grid.addLayout(cycles_layout)
        
        config_layout.addLayout(times_grid)
        layout.addWidget(config_frame)
        
        # Estado actual y progreso
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        # Fase actual
        self.phase_label = QLabel("💼 Fase de Trabajo")
        self.phase_label.setStyleSheet("font-weight: bold; color: #28a745; font-size: 14px;")
        self.phase_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.phase_label)
        
        # Display de tiempo
        self.time_display = QLabel("25:00")
        self.time_display.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #e74c3c; 
            background-color: rgba(231, 76, 60, 0.1);
            border: 2px solid #e74c3c;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        """)
        self.time_display.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.time_display)
        
        # Progreso de ciclos
        self.cycle_progress = QLabel("Ciclo 1 de 4")
        self.cycle_progress.setAlignment(Qt.AlignCenter)
        self.cycle_progress.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        status_layout.addWidget(self.cycle_progress)
        
        layout.addWidget(status_frame)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ Iniciar Pomodoro")
        self.pause_button = QPushButton("⏸ Pausar")
        self.skip_button = QPushButton("⏭ Saltar Fase")
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
        
        for btn in [self.start_button, self.pause_button, self.skip_button, self.reset_button]:
            btn.setStyleSheet(button_style)
        
        self.pause_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.skip_button)
        buttons_layout.addWidget(self.reset_button)
        
        layout.addLayout(buttons_layout)
        
        # Información de estado
        self.status_info = QLabel("🍅 Selecciona tipo y presiona Iniciar")
        self.status_info.setStyleSheet("font-size: 11px; color: #666; font-style: italic;")
        layout.addWidget(self.status_info)
    
    def connect_signals(self):
        self.timer.timeout.connect(self.update_timer)
        self.start_button.clicked.connect(self.start_pomodoro)
        self.pause_button.clicked.connect(self.pause_pomodoro)
        self.skip_button.clicked.connect(self.skip_phase)
        self.reset_button.clicked.connect(self.reset_pomodoro)
        self.type_combo.currentTextChanged.connect(self.update_config_from_type)
        
        # Actualizar display cuando cambien las configuraciones
        self.work_spinbox.valueChanged.connect(self.update_display_if_stopped)
        self.short_break_spinbox.valueChanged.connect(self.update_display_if_stopped)
        self.long_break_spinbox.valueChanged.connect(self.update_display_if_stopped)
    
    def update_config_from_type(self):
        """Actualiza configuraciones según el tipo seleccionado"""
        pomodoro_type = self.type_combo.currentText()
        if pomodoro_type in self.pomodoro_types:
            config = self.pomodoro_types[pomodoro_type]
            
            # Solo actualizar si no es personalizado o si no está corriendo
            if pomodoro_type != "Personalizado" or not self.is_running:
                self.work_spinbox.setValue(config["work"])
                self.short_break_spinbox.setValue(config["short_break"])
                self.long_break_spinbox.setValue(config["long_break"])
                self.cycles_spinbox.setValue(config["cycles"])
        
        # Habilitar/deshabilitar controles para tipo personalizado
        is_custom = pomodoro_type == "Personalizado"
        self.work_spinbox.setEnabled(is_custom or not self.is_running)
        self.short_break_spinbox.setEnabled(is_custom or not self.is_running)
        self.long_break_spinbox.setEnabled(is_custom or not self.is_running)
        self.cycles_spinbox.setEnabled(is_custom or not self.is_running)
        
        if not self.is_running:
            self.update_display_for_current_phase()
    
    def start_pomodoro(self):
        if not self.is_running:
            self.cycles_completed = 0
            self.current_phase = "work"
            self.remaining_time = self.work_spinbox.value() * 60
            self.total_phase_time = self.remaining_time
        
        self.timer.start(1000)
        self.is_running = True
        
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        
        # Deshabilitar configuración
        self.type_combo.setEnabled(False)
        if self.type_combo.currentText() != "Personalizado":
            self.work_spinbox.setEnabled(False)
            self.short_break_spinbox.setEnabled(False)
            self.long_break_spinbox.setEnabled(False)
            self.cycles_spinbox.setEnabled(False)
        
        self.update_ui_for_phase()
        self.status_info.setText("▶ Pomodoro en progreso...")
    
    def pause_pomodoro(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("▶ Continuar")
            self.start_button.setEnabled(True)
            self.status_info.setText("⏸ Pomodoro pausado")
        else:
            self.timer.start(1000)
            self.pause_button.setText("⏸ Pausar")
            self.start_button.setEnabled(False)
            self.status_info.setText("▶ Pomodoro continuando...")
    
    def skip_phase(self):
        """Salta a la siguiente fase"""
        self.remaining_time = 0
        self.update_timer()  # Esto provocará el cambio de fase
    
    def reset_pomodoro(self):
        self.timer.stop()
        self.is_running = False
        self.cycles_completed = 0
        self.current_phase = "work"
        
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.pause_button.setText("⏸ Pausar")
        
        # Habilitar configuración
        self.type_combo.setEnabled(True)
        self.update_config_from_type()
        
        self.update_display_for_current_phase()
        self.update_cycle_display()
        self.status_info.setText("🔄 Pomodoro reiniciado")
    
    def update_timer(self):
        self.remaining_time -= 1
        
        if self.remaining_time <= 0:
            self.switch_phase()
        
        self.update_display()
        
        # Emitir para estadísticas
        phase_name = self.get_phase_name()
        time_str = self.format_time(self.remaining_time)
        self.pomodoro_tick.emit(phase_name, time_str)
    
    def switch_phase(self):
        if self.current_phase == "work":
            self.work_finished.emit()
            self.cycles_completed += 1
            
            # Decidir si es descanso corto o largo
            if self.cycles_completed >= self.cycles_spinbox.value():
                self.current_phase = "long_break"
                self.remaining_time = self.long_break_spinbox.value() * 60
                self.cycles_completed = 0  # Reiniciar ciclos
                self.pomodoro_cycle_completed.emit()
            else:
                self.current_phase = "short_break"
                self.remaining_time = self.short_break_spinbox.value() * 60
                
        elif self.current_phase == "short_break":
            self.break_finished.emit()
            self.current_phase = "work"
            self.remaining_time = self.work_spinbox.value() * 60
            
        elif self.current_phase == "long_break":
            self.long_break_finished.emit()
            self.current_phase = "work"
            self.remaining_time = self.work_spinbox.value() * 60
        
        self.total_phase_time = self.remaining_time
        self.update_ui_for_phase()
        self.update_cycle_display()
    
    def update_ui_for_phase(self):
        if self.current_phase == "work":
            self.phase_label.setText("💼 Fase de Trabajo")
            self.phase_label.setStyleSheet("font-weight: bold; color: #28a745; font-size: 14px;")
            self.time_display.setStyleSheet("""
                font-size: 22px; font-weight: bold; color: #28a745; 
                background-color: rgba(40, 167, 69, 0.1);
                border: 2px solid #28a745; border-radius: 8px; padding: 10px;
            """)
        elif self.current_phase == "short_break":
            self.phase_label.setText("☕ Descanso Corto")
            self.phase_label.setStyleSheet("font-weight: bold; color: #ffc107; font-size: 14px;")
            self.time_display.setStyleSheet("""
                font-size: 22px; font-weight: bold; color: #ffc107; 
                background-color: rgba(255, 193, 7, 0.1);
                border: 2px solid #ffc107; border-radius: 8px; padding: 10px;
            """)
        elif self.current_phase == "long_break":
            self.phase_label.setText("🌴 Descanso Largo")
            self.phase_label.setStyleSheet("font-weight: bold; color: #17a2b8; font-size: 14px;")
            self.time_display.setStyleSheet("""
                font-size: 22px; font-weight: bold; color: #17a2b8; 
                background-color: rgba(23, 162, 184, 0.1);
                border: 2px solid #17a2b8; border-radius: 8px; padding: 10px;
            """)
    
    def update_display_if_stopped(self):
        if not self.is_running:
            self.update_display_for_current_phase()
    
    def update_display_for_current_phase(self):
        if self.current_phase == "work":
            time_minutes = self.work_spinbox.value()
        elif self.current_phase == "short_break":
            time_minutes = self.short_break_spinbox.value()
        else:  # long_break
            time_minutes = self.long_break_spinbox.value()
        
        self.time_display.setText(f"{time_minutes:02d}:00")
        self.update_ui_for_phase()
    
    def update_display(self):
        self.time_display.setText(self.format_time(self.remaining_time))
    
    def update_cycle_display(self):
        current_cycle = self.cycles_completed + (1 if self.current_phase == "work" else 0)
        total_cycles = self.cycles_spinbox.value()
        self.cycle_progress.setText(f"Ciclo {current_cycle} de {total_cycles}")
    
    def format_time(self, total_seconds):
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_phase_name(self):
        names = {
            "work": "Trabajo",
            "short_break": "Descanso Corto", 
            "long_break": "Descanso Largo"
        }
        return names.get(self.current_phase, "Desconocido")
    
    def get_pomodoro_statistics(self):
        """Retorna estadísticas del pomodoro para el panel de estadísticas"""
        if self.is_running:
            progress = 1.0 - (self.remaining_time / self.total_phase_time) if self.total_phase_time > 0 else 0
            return {
                'status': 'running',
                'phase': self.get_phase_name(),
                'remaining': self.format_time(self.remaining_time),
                'current_cycle': self.cycles_completed + (1 if self.current_phase == "work" else 0),
                'total_cycles': self.cycles_spinbox.value(),
                'progress_percent': int(progress * 100),
                'type': self.type_combo.currentText()
            }
        else:
            return {
                'status': 'stopped',
                'phase': 'Detenido',
                'remaining': '00:00',
                'current_cycle': 0,
                'total_cycles': self.cycles_spinbox.value(),
                'progress_percent': 0,
                'type': self.type_combo.currentText()
            }
