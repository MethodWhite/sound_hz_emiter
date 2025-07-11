"""
Panel de estadísticas en tiempo real
"""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QProgressBar, QFrame, QScrollArea, QWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class StatisticsPanel(QGroupBox):
    """Panel de estadísticas en tiempo real"""
    
    def __init__(self):
        super().__init__("📊 Estadísticas en Tiempo Real")
        self.timer_stats = {}
        self.pomodoro_stats = {}
        self.audio_stats = {}
        self.setup_ui()
        
        # Timer para actualización periódica
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Actualizar cada segundo
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Crear scroll area para estadísticas
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(400)
        
        # Widget contenedor para estadísticas
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(12)
        
        # Sección de sistema
        self.create_system_stats_section(stats_layout)
        
        # Sección de timer
        self.create_timer_stats_section(stats_layout)
        
        # Sección de pomodoro
        self.create_pomodoro_stats_section(stats_layout)
        
        # Sección de audio
        self.create_audio_stats_section(stats_layout)
        
        scroll_area.setWidget(stats_widget)
        layout.addWidget(scroll_area)
    
    def create_system_stats_section(self, parent_layout):
        """Crea sección de estadísticas del sistema"""
        system_frame = QFrame()
        system_frame.setFrameStyle(QFrame.StyledPanel)
        system_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(23, 162, 184, 0.1);
                border: 1px solid #17a2b8;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        system_layout = QVBoxLayout(system_frame)
        
        # Título
        title = QLabel("🖥️ Sistema")
        title.setStyleSheet("font-weight: bold; color: #17a2b8; font-size: 14px;")
        system_layout.addWidget(title)
        
        # Grid de información
        info_grid = QGridLayout()
        
        # Tiempo de sesión
        info_grid.addWidget(QLabel("Tiempo de sesión:"), 0, 0)
        self.session_time_label = QLabel("00:00:00")
        self.session_time_label.setStyleSheet("font-weight: bold; color: #17a2b8;")
        info_grid.addWidget(self.session_time_label, 0, 1)
        
        # Fecha y hora
        info_grid.addWidget(QLabel("Fecha/Hora:"), 1, 0)
        self.datetime_label = QLabel("--")
        self.datetime_label.setStyleSheet("font-weight: bold; color: #17a2b8;")
        info_grid.addWidget(self.datetime_label, 1, 1)
        
        system_layout.addLayout(info_grid)
        parent_layout.addWidget(system_frame)
    
    def create_timer_stats_section(self, parent_layout):
        """Crea sección de estadísticas del timer"""
        timer_frame = QFrame()
        timer_frame.setFrameStyle(QFrame.StyledPanel)
        timer_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 120, 212, 0.1);
                border: 1px solid #0078d4;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        timer_layout = QVBoxLayout(timer_frame)
        
        # Título
        title = QLabel("⏰ Timer")
        title.setStyleSheet("font-weight: bold; color: #0078d4; font-size: 14px;")
        timer_layout.addWidget(title)
        
        # Grid de información
        timer_grid = QGridLayout()
        
        # Estado
        timer_grid.addWidget(QLabel("Estado:"), 0, 0)
        self.timer_status_label = QLabel("Detenido")
        self.timer_status_label.setStyleSheet("font-weight: bold; color: #6c757d;")
        timer_grid.addWidget(self.timer_status_label, 0, 1)
        
        # Tiempo transcurrido
        timer_grid.addWidget(QLabel("Transcurrido:"), 1, 0)
        self.timer_elapsed_label = QLabel("00:00:00")
        self.timer_elapsed_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        timer_grid.addWidget(self.timer_elapsed_label, 1, 1)
        
        # Tiempo restante
        timer_grid.addWidget(QLabel("Restante:"), 2, 0)
        self.timer_remaining_label = QLabel("00:00:00")
        self.timer_remaining_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        timer_grid.addWidget(self.timer_remaining_label, 2, 1)
        
        timer_layout.addLayout(timer_grid)
        
        # Barra de progreso
        self.timer_progress_bar = QProgressBar()
        self.timer_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #0078d4;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        timer_layout.addWidget(self.timer_progress_bar)
        
        timer_layout.addLayout(timer_grid)
        parent_layout.addWidget(timer_frame)
    
    def create_pomodoro_stats_section(self, parent_layout):
        """Crea sección de estadísticas del pomodoro"""
        pomodoro_frame = QFrame()
        pomodoro_frame.setFrameStyle(QFrame.StyledPanel)
        pomodoro_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(231, 76, 60, 0.1);
                border: 1px solid #e74c3c;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        pomodoro_layout = QVBoxLayout(pomodoro_frame)
        
        # Título
        title = QLabel("🍅 Pomodoro")
        title.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 14px;")
        pomodoro_layout.addWidget(title)
        
        # Grid de información
        pomodoro_grid = QGridLayout()
        
        # Estado y fase
        pomodoro_grid.addWidget(QLabel("Estado:"), 0, 0)
        self.pomodoro_status_label = QLabel("Detenido")
        self.pomodoro_status_label.setStyleSheet("font-weight: bold; color: #6c757d;")
        pomodoro_grid.addWidget(self.pomodoro_status_label, 0, 1)
        
        pomodoro_grid.addWidget(QLabel("Fase:"), 1, 0)
        self.pomodoro_phase_label = QLabel("--")
        self.pomodoro_phase_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        pomodoro_grid.addWidget(self.pomodoro_phase_label, 1, 1)
        
        # Ciclos
        pomodoro_grid.addWidget(QLabel("Ciclos:"), 2, 0)
        self.pomodoro_cycles_label = QLabel("0 / 0")
        self.pomodoro_cycles_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        pomodoro_grid.addWidget(self.pomodoro_cycles_label, 2, 1)
        
        # Tipo
        pomodoro_grid.addWidget(QLabel("Tipo:"), 3, 0)
        self.pomodoro_type_label = QLabel("--")
        self.pomodoro_type_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        pomodoro_grid.addWidget(self.pomodoro_type_label, 3, 1)
        
        pomodoro_layout.addLayout(pomodoro_grid)
        
        # Barra de progreso de fase
        self.pomodoro_progress_bar = QProgressBar()
        self.pomodoro_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e74c3c;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
                border-radius: 3px;
            }
        """)
        pomodoro_layout.addWidget(self.pomodoro_progress_bar)
        
        parent_layout.addWidget(pomodoro_frame)
    
    def create_audio_stats_section(self, parent_layout):
        """Crea sección de estadísticas de audio"""
        audio_frame = QFrame()
        audio_frame.setFrameStyle(QFrame.StyledPanel)
        audio_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 167, 69, 0.1);
                border: 1px solid #28a745;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        audio_layout = QVBoxLayout(audio_frame)
        
        # Título
        title = QLabel("🔊 Audio")
        title.setStyleSheet("font-weight: bold; color: #28a745; font-size: 14px;")
        audio_layout.addWidget(title)
        
        # Grid de información
        audio_grid = QGridLayout()
        
        # Estado del sistema
        audio_grid.addWidget(QLabel("Sistema:"), 0, 0)
        self.audio_system_label = QLabel("Detenido")
        self.audio_system_label.setStyleSheet("font-weight: bold; color: #6c757d;")
        audio_grid.addWidget(self.audio_system_label, 0, 1)
        
        # Tonos activos
        audio_grid.addWidget(QLabel("Tonos activos:"), 1, 0)
        self.active_tones_label = QLabel("0 / 0")
        self.active_tones_label.setStyleSheet("font-weight: bold; color: #28a745;")
        audio_grid.addWidget(self.active_tones_label, 1, 1)
        
        # Volumen maestro
        audio_grid.addWidget(QLabel("Vol. maestro:"), 2, 0)
        self.master_volume_label = QLabel("50%")
        self.master_volume_label.setStyleSheet("font-weight: bold; color: #28a745;")
        audio_grid.addWidget(self.master_volume_label, 2, 1)
        
        # Carga de CPU (estimada)
        audio_grid.addWidget(QLabel("Carga CPU:"), 3, 0)
        self.cpu_load_label = QLabel("0%")
        self.cpu_load_label.setStyleSheet("font-weight: bold; color: #28a745;")
        audio_grid.addWidget(self.cpu_load_label, 3, 1)
        
        audio_layout.addLayout(audio_grid)
        
        # Información adicional
        self.freq_range_label = QLabel("Rango de freq: 0 - 0 Hz")
        self.freq_range_label.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        audio_layout.addWidget(self.freq_range_label)
        
        parent_layout.addWidget(audio_frame)
    
    def update_timer_stats(self, stats):
        """Actualiza estadísticas del timer"""
        self.timer_stats = stats
        
        # Actualizar labels
        status_colors = {
            'running': ('#28a745', 'En ejecución'),
            'stopped': ('#6c757d', 'Detenido'),
            'paused': ('#ffc107', 'Pausado')
        }
        
        color, text = status_colors.get(stats['status'], ('#6c757d', 'Desconocido'))
        self.timer_status_label.setText(text)
        self.timer_status_label.setStyleSheet(f"font-weight: bold; color: {color};")
        
        self.timer_elapsed_label.setText(stats['elapsed'])
        self.timer_remaining_label.setText(stats['remaining'])
        
        # Actualizar barra de progreso
        self.timer_progress_bar.setValue(stats['progress_percent'])
    
    def update_pomodoro_stats(self, stats):
        """Actualiza estadísticas del pomodoro"""
        self.pomodoro_stats = stats
        
        # Actualizar labels
        status_colors = {
            'running': ('#28a745', 'En ejecución'),
            'stopped': ('#6c757d', 'Detenido'),
            'paused': ('#ffc107', 'Pausado')
        }
        
        color, text = status_colors.get(stats['status'], ('#6c757d', 'Desconocido'))
        self.pomodoro_status_label.setText(text)
        self.pomodoro_status_label.setStyleSheet(f"font-weight: bold; color: {color};")
        
        self.pomodoro_phase_label.setText(stats['phase'])
        self.pomodoro_cycles_label.setText(f"{stats['current_cycle']} / {stats['total_cycles']}")
        self.pomodoro_type_label.setText(stats['type'])
        
        # Actualizar barra de progreso
        self.pomodoro_progress_bar.setValue(stats['progress_percent'])
    
    def update_audio_stats(self, stats):
        """Actualiza estadísticas de audio"""
        self.audio_stats = stats
        
        # Sistema de audio
        if stats.get('is_running', False):
            self.audio_system_label.setText("Activo")
            self.audio_system_label.setStyleSheet("font-weight: bold; color: #28a745;")
        else:
            self.audio_system_label.setText("Detenido")
            self.audio_system_label.setStyleSheet("font-weight: bold; color: #6c757d;")
        
        # Tonos
        active = stats.get('active_tones', 0)
        total = stats.get('total_tones', 0)
        self.active_tones_label.setText(f"{active} / {total}")
        
        # Volumen maestro
        master_vol = stats.get('master_volume', 0.5) * 100
        self.master_volume_label.setText(f"{master_vol:.0f}%")
        
        # Carga CPU
        cpu_load = stats.get('cpu_load', 0)
        self.cpu_load_label.setText(f"{cpu_load}%")
        
        # Rango de frecuencias
        freq_range = stats.get('frequency_range', {'min': 0, 'max': 0})
        self.freq_range_label.setText(f"Rango de freq: {freq_range['min']} - {freq_range['max']} Hz")
    
    def update_display(self):
        """Actualiza la información que cambia periódicamente"""
        from datetime import datetime
        
        # Actualizar fecha y hora
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Actualizar tiempo de sesión (simplificado)
        # En una implementación real, esto vendría de un contador de sesión
        self.session_time_label.setText("--:--:--")
