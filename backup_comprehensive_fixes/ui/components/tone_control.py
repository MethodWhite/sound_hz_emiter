"""
Control de tono individual - Responsabilidad única
Refactorizado para ser más pequeño y mantenible
"""

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QSpinBox, QSlider, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, Signal
from ..utils.constants import UIConstants, WaveTypes, AudioConstants

class ToneControl(QFrame):
    """
    Control individual de tono con responsabilidad única
    Aplicando principios de Clean Code
    """
    
    # Señales para comunicación con el exterior
    tone_parameters_changed = Signal(int, dict)  # tone_id, parameters
    tone_play_state_changed = Signal(int, bool)  # tone_id, is_playing
    tone_deletion_requested = Signal(int)  # tone_id
    
    def __init__(self, tone_id: int, initial_frequency: int = 440):
        super().__init__()
        self.tone_id = tone_id
        self.is_playing = False
        self._setup_ui(initial_frequency)
        self._connect_signals()
        self._apply_initial_style()
    
    def _setup_ui(self, initial_frequency: int) -> None:
        """Configura la interfaz del control"""
        self.setFixedHeight(UIConstants.TONE_CONTROL_HEIGHT)
        self.setMinimumWidth(UIConstants.TONE_CONTROL_MIN_WIDTH)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(UIConstants.COMPONENT_SPACING)
        
        # Header con título y controles
        self._create_header(layout)
        
        # Grid de controles principales
        self._create_controls_grid(layout, initial_frequency)
        
        # Checkbox de habilitación
        self._create_enable_checkbox(layout)
    
    def _create_header(self, parent_layout: QVBoxLayout) -> None:
        """Crea el header con título y botones de control"""
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel(f"♪ Tono {self.tone_id}")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d4;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botones de control
        self._create_control_buttons(header_layout)
        
        parent_layout.addLayout(header_layout)
    
    def _create_control_buttons(self, parent_layout: QHBoxLayout) -> None:
        """Crea los botones de control (play, stop, delete)"""
        button_size = UIConstants.CONTROL_BUTTON_SIZE
        
        # Botón play/pause
        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setFixedSize(button_size, button_size)
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        parent_layout.addWidget(self.play_pause_button)
        
        # Botón stop
        self.stop_button = QPushButton("⏹")
        self.stop_button.setFixedSize(button_size, button_size)
        self.stop_button.clicked.connect(self._stop_tone)
        parent_layout.addWidget(self.stop_button)
        
        # Botón eliminar
        delete_button = QPushButton("✕")
        delete_button.setFixedSize(button_size, button_size)
        delete_button.clicked.connect(lambda: self.tone_deletion_requested.emit(self.tone_id))
        parent_layout.addWidget(delete_button)
    
    def _create_controls_grid(self, parent_layout: QVBoxLayout, initial_frequency: int) -> None:
        """Crea el grid de controles principales"""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(UIConstants.COMPONENT_SPACING)
        
        # Frecuencia
        self._create_frequency_control(grid_layout, initial_frequency)
        
        # Volumen
        self._create_volume_control(grid_layout)
        
        # Panning
        self._create_panning_control(grid_layout)
        
        # Tipo de onda
        self._create_wave_type_control(grid_layout)
        
        # Estado
        self._create_status_display(grid_layout)
        
        parent_layout.addLayout(grid_layout)
    
    def _create_frequency_control(self, grid: QGridLayout, initial_frequency: int) -> None:
        """Crea el control de frecuencia"""
        freq_label = QLabel("Frecuencia (Hz)")
        freq_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid.addWidget(freq_label, 0, 0)
        
        self.frequency_spinbox = QSpinBox()
        self.frequency_spinbox.setRange(AudioConstants.MIN_FREQUENCY, AudioConstants.MAX_FREQUENCY)
        self.frequency_spinbox.setValue(initial_frequency)
        self.frequency_spinbox.setSuffix(" Hz")
        self.frequency_spinbox.setFixedWidth(120)
        grid.addWidget(self.frequency_spinbox, 1, 0)
    
    def _create_volume_control(self, grid: QGridLayout) -> None:
        """Crea el control de volumen"""
        vol_label = QLabel("Volumen (%)")
        vol_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid.addWidget(vol_label, 0, 1)
        
        # Container para slider y etiqueta
        vol_container = self._create_slider_container()
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(30)
        self.volume_slider.setMinimumWidth(120)
        vol_container.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("30%")
        self.volume_label.setAlignment(Qt.AlignCenter)
        self.volume_label.setStyleSheet("font-size: 10px; font-weight: bold;")
        vol_container.addWidget(self.volume_label)
        
        vol_widget = self._create_widget_from_layout(vol_container)
        grid.addWidget(vol_widget, 1, 1)
    
    def _create_panning_control(self, grid: QGridLayout) -> None:
        """Crea el control de panning"""
        pan_label = QLabel("Panning L/R")
        pan_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid.addWidget(pan_label, 2, 0)
        
        # Container para slider y etiqueta
        pan_container = self._create_slider_container()
        
        self.panning_slider = QSlider(Qt.Horizontal)
        self.panning_slider.setRange(-100, 100)
        self.panning_slider.setValue(0)
        self.panning_slider.setMinimumWidth(120)
        pan_container.addWidget(self.panning_slider)
        
        self.panning_label = QLabel("Centro")
        self.panning_label.setAlignment(Qt.AlignCenter)
        self.panning_label.setStyleSheet("font-size: 10px; font-weight: bold;")
        pan_container.addWidget(self.panning_label)
        
        pan_widget = self._create_widget_from_layout(pan_container)
        grid.addWidget(pan_widget, 2, 1)
    
    def _create_wave_type_control(self, grid: QGridLayout) -> None:
        """Crea el control de tipo de onda"""
        wave_label = QLabel("Tipo de Onda")
        wave_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid.addWidget(wave_label, 0, 2)
        
        self.wave_type_combo = QComboBox()
        self.wave_type_combo.addItems(WaveTypes.get_all_types())
        self.wave_type_combo.setFixedWidth(120)
        grid.addWidget(self.wave_type_combo, 1, 2)
    
    def _create_status_display(self, grid: QGridLayout) -> None:
        """Crea el display de estado"""
        status_label = QLabel("Estado")
        status_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid.addWidget(status_label, 2, 2)
        
        self.status_label = QLabel("⏸ Pausado")
        self.status_label.setStyleSheet("font-size: 11px; color: #666;")
        grid.addWidget(self.status_label, 3, 2)
    
    def _create_enable_checkbox(self, parent_layout: QVBoxLayout) -> None:
        """Crea el checkbox de habilitación"""
        self.enable_checkbox = QCheckBox("🔊 Tono Habilitado")
        self.enable_checkbox.setChecked(True)
        self.enable_checkbox.setStyleSheet("font-weight: bold; color: #28a745; font-size: 12px;")
        parent_layout.addWidget(self.enable_checkbox)
    
    def _create_slider_container(self) -> QVBoxLayout:
        """Helper para crear containers de sliders"""
        container = QVBoxLayout()
        container.setSpacing(5)
        return container
    
    def _create_widget_from_layout(self, layout: QVBoxLayout):
        """Helper para crear widget desde layout"""
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        widget.setLayout(layout)
        widget.setMinimumWidth(140)
        return widget
    
    def _connect_signals(self) -> None:
        """Conecta las señales de los controles"""
        self.frequency_spinbox.valueChanged.connect(self._emit_parameter_changes)
        self.volume_slider.valueChanged.connect(self._update_volume_label)
        self.volume_slider.valueChanged.connect(self._emit_parameter_changes)
        self.panning_slider.valueChanged.connect(self._update_panning_label)
        self.panning_slider.valueChanged.connect(self._emit_parameter_changes)
        self.wave_type_combo.currentTextChanged.connect(self._emit_parameter_changes)
        self.enable_checkbox.toggled.connect(self._emit_parameter_changes)
    
    def _toggle_play_pause(self) -> None:
        """Alterna entre play y pause"""
        self.is_playing = not self.is_playing
        self._update_play_button_state()
        self._update_status_display()
        self.tone_play_state_changed.emit(self.tone_id, self.is_playing)
        self._emit_parameter_changes()
    
    def _stop_tone(self) -> None:
        """Detiene el tono"""
        self.is_playing = False
        self._update_play_button_state()
        self._update_status_display()
        self.tone_play_state_changed.emit(self.tone_id, self.is_playing)
        self._emit_parameter_changes()
    
    def _update_play_button_state(self) -> None:
        """Actualiza el estado visual del botón play"""
        if self.is_playing:
            self.play_pause_button.setText("⏸")
            self.play_pause_button.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
            """)
        else:
            self.play_pause_button.setText("▶")
            self.play_pause_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
    
    def _update_status_display(self) -> None:
        """Actualiza el display de estado"""
        if self.is_playing:
            self.status_label.setText("▶ Reproduciendo")
            self.status_label.setStyleSheet("font-size: 11px; color: #28a745; font-weight: bold;")
        else:
            self.status_label.setText("⏸ Pausado")
            self.status_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold;")
    
    def _update_volume_label(self) -> None:
        """Actualiza la etiqueta del volumen"""
        volume_percent = self.volume_slider.value()
        self.volume_label.setText(f"{volume_percent}%")
    
    def _update_panning_label(self) -> None:
        """Actualiza la etiqueta del panning"""
        panning_value = self.panning_slider.value()
        if panning_value < -20:
            self.panning_label.setText("◄ Izq")
        elif panning_value > 20:
            self.panning_label.setText("Der ►")
        else:
            self.panning_label.setText("Centro")
    
    def _emit_parameter_changes(self) -> None:
        """Emite los cambios de parámetros"""
        parameters = {
            'frequency': self.frequency_spinbox.value(),
            'volume': self.volume_slider.value() / 100.0,
            'panning': self.panning_slider.value() / 100.0,
            'wave_type': self.wave_type_combo.currentText().lower(),
            'active': self.enable_checkbox.isChecked() and self.is_playing
        }
        self.tone_parameters_changed.emit(self.tone_id, parameters)
    
    def _apply_initial_style(self) -> None:
        """Aplica el estilo inicial del frame"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background-color: #fafafa;
                margin: 3px;
            }
        """)
    
    # Métodos públicos para control externo
    def enable_tone(self) -> None:
        """Habilita el tono externamente"""
        self.enable_checkbox.setChecked(True)
    
    def disable_tone(self) -> None:
        """Deshabilita el tono externamente"""
        self.enable_checkbox.setChecked(False)
    
    def is_enabled(self) -> bool:
        """Retorna si el tono está habilitado"""
        return self.enable_checkbox.isChecked()
    
    def get_current_parameters(self) -> dict:
        """Retorna los parámetros actuales del tono"""
        return {
            'frequency': self.frequency_spinbox.value(),
            'volume': self.volume_slider.value() / 100.0,
            'panning': self.panning_slider.value() / 100.0,
            'wave_type': self.wave_type_combo.currentText().lower(),
            'active': self.enable_checkbox.isChecked() and self.is_playing
        }