"""
Control de tono mejorado - UI corregida y funcional
"""

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QSpinBox, QSlider, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, Signal
from ..utils.constants import UIConstants, WaveTypes, AudioConstants

class ToneControl(QFrame):
    """Control individual de tono con UI mejorada y funcional"""
    
    # Señales para comunicación con el exterior
    tone_parameters_changed = Signal(int, dict)
    tone_play_state_changed = Signal(int, bool)
    tone_deletion_requested = Signal(int)
    
    def __init__(self, tone_id: int, initial_frequency: int = 440):
        super().__init__()
        self.tone_id = tone_id
        self.is_playing = False
        self._setup_ui(initial_frequency)
        self._connect_signals()
        self._apply_initial_style()
    
    def _setup_ui(self, initial_frequency: int) -> None:
        """Configura la interfaz del control con UI mejorada"""
        self.setFixedHeight(UIConstants.TONE_CONTROL_HEIGHT + 50)  # Más espacio
        self.setMinimumWidth(UIConstants.TONE_CONTROL_MIN_WIDTH + 100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header mejorado
        self._create_enhanced_header(layout)
        
        # Grid de controles principales con mejor espaciado
        self._create_enhanced_controls_grid(layout, initial_frequency)
        
        # Checkbox de habilitación mejorado
        self._create_enhanced_enable_section(layout)
    
    def _create_enhanced_header(self, parent_layout: QVBoxLayout) -> None:
        """Header mejorado con mejor diseño"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 120, 212, 0.1);
                border: 1px solid #0078d4;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 8, 10, 8)
        
        # Título con mejor estilo
        title_label = QLabel(f"🎵 Tono {self.tone_id}")
        title_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #0078d4;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botones de control mejorados
        self._create_enhanced_control_buttons(header_layout)
        
        parent_layout.addWidget(header_frame)
    
    def _create_enhanced_control_buttons(self, parent_layout: QHBoxLayout) -> None:
        """Botones de control mejorados"""
        button_size = 40  # Más grandes
        
        # Botón play/pause mejorado
        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setFixedSize(button_size, button_size)
        self.play_pause_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #218838;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        parent_layout.addWidget(self.play_pause_button)
        
        # Botón stop mejorado
        self.stop_button = QPushButton("⏹")
        self.stop_button.setFixedSize(button_size, button_size)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c82333;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.stop_button.clicked.connect(self._stop_tone)
        parent_layout.addWidget(self.stop_button)
        
        # Botón eliminar mejorado
        delete_button = QPushButton("🗑")
        delete_button.setFixedSize(button_size, button_size)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #545b62;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        delete_button.clicked.connect(lambda: self.tone_deletion_requested.emit(self.tone_id))
        parent_layout.addWidget(delete_button)
    
    def _create_enhanced_controls_grid(self, parent_layout: QVBoxLayout, initial_frequency: int) -> None:
        """Grid de controles mejorado con mejor espaciado y visibilidad"""
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(248, 249, 250, 0.8);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        grid_layout = QGridLayout(controls_frame)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        
        # Frecuencia mejorada
        self._create_enhanced_frequency_control(grid_layout, initial_frequency)
        
        # Volumen mejorado
        self._create_enhanced_volume_control(grid_layout)
        
        # Panning mejorado
        self._create_enhanced_panning_control(grid_layout)
        
        # Tipo de onda mejorado
        self._create_enhanced_wave_type_control(grid_layout)
        
        # Estado mejorado
        self._create_enhanced_status_display(grid_layout)
        
        parent_layout.addWidget(controls_frame)
    
    def _create_enhanced_frequency_control(self, grid: QGridLayout, initial_frequency: int) -> None:
        """Control de frecuencia mejorado"""
        freq_label = QLabel("🎼 Frecuencia (Hz)")
        freq_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px; 
            color: #495057;
            margin-bottom: 5px;
        """)
        grid.addWidget(freq_label, 0, 0)
        
        self.frequency_spinbox = QSpinBox()
        self.frequency_spinbox.setRange(AudioConstants.MIN_FREQUENCY, AudioConstants.MAX_FREQUENCY)
        self.frequency_spinbox.setValue(initial_frequency)
        self.frequency_spinbox.setSuffix(" Hz")
        self.frequency_spinbox.setMinimumWidth(140)
        self.frequency_spinbox.setMinimumHeight(35)
        self.frequency_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: white;
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QSpinBox:focus {
                border-color: #0078d4;
                background-color: #f8f9fa;
            }
        """)
        grid.addWidget(self.frequency_spinbox, 1, 0)
    
    def _create_enhanced_volume_control(self, grid: QGridLayout) -> None:
        """Control de volumen mejorado"""
        vol_label = QLabel("🔊 Volumen (%)")
        vol_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px; 
            color: #495057;
            margin-bottom: 5px;
        """)
        grid.addWidget(vol_label, 0, 1)
        
        # Container para slider y etiqueta con mejor diseño
        vol_widget = QFrame()
        vol_layout = QVBoxLayout(vol_widget)
        vol_layout.setContentsMargins(0, 0, 0, 0)
        vol_layout.setSpacing(8)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(30)
        self.volume_slider.setMinimumWidth(140)
        self.volume_slider.setMinimumHeight(25)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #ced4da;
                height: 10px;
                background: #e9ecef;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 2px solid #0078d4;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
                border-color: #106ebe;
            }
        """)
        vol_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("30%")
        self.volume_label.setAlignment(Qt.AlignCenter)
        self.volume_label.setStyleSheet("""
            font-size: 11px; 
            font-weight: bold; 
            color: #0078d4;
            background-color: rgba(0, 120, 212, 0.1);
            border-radius: 4px;
            padding: 2px;
        """)
        vol_layout.addWidget(self.volume_label)
        
        grid.addWidget(vol_widget, 1, 1)
    
    def _create_enhanced_panning_control(self, grid: QGridLayout) -> None:
        """Control de panning mejorado"""
        pan_label = QLabel("🎧 Panning L/R")
        pan_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px; 
            color: #495057;
            margin-bottom: 5px;
        """)
        grid.addWidget(pan_label, 2, 0)
        
        # Container para slider y etiqueta con mejor diseño
        pan_widget = QFrame()
        pan_layout = QVBoxLayout(pan_widget)
        pan_layout.setContentsMargins(0, 0, 0, 0)
        pan_layout.setSpacing(8)
        
        self.panning_slider = QSlider(Qt.Horizontal)
        self.panning_slider.setRange(-100, 100)
        self.panning_slider.setValue(0)
        self.panning_slider.setMinimumWidth(140)
        self.panning_slider.setMinimumHeight(25)
        self.panning_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #ced4da;
                height: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ff6b6b, stop:0.5 #ced4da, stop:1 #4ecdc4);
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #495057;
                border: 2px solid #495057;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #343a40;
                border-color: #343a40;
            }
        """)
        pan_layout.addWidget(self.panning_slider)
        
        self.panning_label = QLabel("Centro")
        self.panning_label.setAlignment(Qt.AlignCenter)
        self.panning_label.setStyleSheet("""
            font-size: 11px; 
            font-weight: bold; 
            color: #495057;
            background-color: rgba(73, 80, 87, 0.1);
            border-radius: 4px;
            padding: 2px;
        """)
        pan_layout.addWidget(self.panning_label)
        
        grid.addWidget(pan_widget, 2, 1)
    
    def _create_enhanced_wave_type_control(self, grid: QGridLayout) -> None:
        """Control de tipo de onda mejorado con todos los tipos"""
        wave_label = QLabel("🌊 Tipo de Onda")
        wave_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px; 
            color: #495057;
            margin-bottom: 5px;
        """)
        grid.addWidget(wave_label, 0, 2)
        
        self.wave_type_combo = QComboBox()
        # Agregar todos los tipos incluyendo ruidos
        all_wave_types = WaveTypes.get_all_types() + ["Ruido Blanco", "Ruido Rosa", "Ruido Marrón"]
        self.wave_type_combo.addItems(all_wave_types)
        self.wave_type_combo.setMinimumWidth(140)
        self.wave_type_combo.setMinimumHeight(35)
        self.wave_type_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QComboBox:focus {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        grid.addWidget(self.wave_type_combo, 1, 2)
    
    def _create_enhanced_status_display(self, grid: QGridLayout) -> None:
        """Display de estado mejorado"""
        status_label = QLabel("📊 Estado")
        status_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px; 
            color: #495057;
            margin-bottom: 5px;
        """)
        grid.addWidget(status_label, 2, 2)
        
        self.status_label = QLabel("⏸ Pausado")
        self.status_label.setStyleSheet("""
            font-size: 12px; 
            color: #6c757d;
            font-weight: bold;
            background-color: rgba(108, 117, 125, 0.1);
            border-radius: 4px;
            padding: 8px;
            text-align: center;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.status_label, 3, 2)
    
    def _create_enhanced_enable_section(self, parent_layout: QVBoxLayout) -> None:
        """Sección de habilitación mejorada"""
        enable_frame = QFrame()
        enable_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 167, 69, 0.1);
                border: 1px solid #28a745;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        enable_layout = QHBoxLayout(enable_frame)
        enable_layout.setContentsMargins(15, 10, 15, 10)
        
        self.enable_checkbox = QCheckBox("🔊 Tono Habilitado")
        self.enable_checkbox.setChecked(True)
        self.enable_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold; 
                color: #28a745; 
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #28a745;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border-color: #28a745;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #218838;
            }
        """)
        enable_layout.addWidget(self.enable_checkbox)
        enable_layout.addStretch()
        
        parent_layout.addWidget(enable_frame)
    
    def _connect_signals(self) -> None:
        """Conecta las señales de los controles"""
        self.frequency_spinbox.valueChanged.connect(self._emit_parameter_changes)
        self.volume_slider.valueChanged.connect(self._update_volume_label)
        self.volume_slider.valueChanged.connect(self._emit_parameter_changes)
        self.panning_slider.valueChanged.connect(self._update_panning_label)
        self.panning_slider.valueChanged.connect(self._emit_parameter_changes)
        self.wave_type_combo.currentTextChanged.connect(self._on_wave_type_changed)
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
    
    def _on_wave_type_changed(self) -> None:
        """Maneja el cambio de tipo de onda"""
        wave_type = self.wave_type_combo.currentText()
        
        # Si es un tipo de ruido, deshabilitar frecuencia
        is_noise = wave_type in ["Ruido Blanco", "Ruido Rosa", "Ruido Marrón"]
        self.frequency_spinbox.setEnabled(not is_noise)
        
        if is_noise:
            self.frequency_spinbox.setStyleSheet("""
                QSpinBox {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 12px;
                    color: #6c757d;
                }
            """)
        else:
            self.frequency_spinbox.setStyleSheet("""
                QSpinBox {
                    background-color: white;
                    border: 2px solid #ced4da;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QSpinBox:focus {
                    border-color: #0078d4;
                    background-color: #f8f9fa;
                }
            """)
        
        self._emit_parameter_changes()
    
    def _update_play_button_state(self) -> None:
        """Actualiza el estado visual del botón play"""
        if self.is_playing:
            self.play_pause_button.setText("⏸")
            self.play_pause_button.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: #212529;
                    border: none;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background-color: #d39e00;
                }
            """)
        else:
            self.play_pause_button.setText("▶")
            self.play_pause_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #218838;
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
    
    def _update_status_display(self) -> None:
        """Actualiza el display de estado"""
        if self.is_playing:
            self.status_label.setText("▶ Reproduciendo")
            self.status_label.setStyleSheet("""
                font-size: 12px; 
                color: #28a745;
                font-weight: bold;
                background-color: rgba(40, 167, 69, 0.2);
                border-radius: 4px;
                padding: 8px;
                text-align: center;
            """)
        else:
            self.status_label.setText("⏸ Pausado")
            self.status_label.setStyleSheet("""
                font-size: 12px; 
                color: #6c757d;
                font-weight: bold;
                background-color: rgba(108, 117, 125, 0.1);
                border-radius: 4px;
                padding: 8px;
                text-align: center;
            """)
    
    def _update_volume_label(self) -> None:
        """Actualiza la etiqueta del volumen"""
        volume_percent = self.volume_slider.value()
        self.volume_label.setText(f"{volume_percent}%")
    
    def _update_panning_label(self) -> None:
        """Actualiza la etiqueta del panning"""
        panning_value = self.panning_slider.value()
        if panning_value < -20:
            self.panning_label.setText("◄ Izquierda")
        elif panning_value > 20:
            self.panning_label.setText("Derecha ►")
        else:
            self.panning_label.setText("Centro")
    
    def _emit_parameter_changes(self) -> None:
        """Emite los cambios de parámetros"""
        wave_type = self.wave_type_combo.currentText().lower()
        
        # Convertir nombres de ruido a formato interno
        noise_mapping = {
            "ruido blanco": "white_noise",
            "ruido rosa": "pink_noise", 
            "ruido marrón": "brown_noise"
        }
        
        if wave_type in noise_mapping:
            wave_type = noise_mapping[wave_type]
        
        parameters = {
            'frequency': self.frequency_spinbox.value() if self.frequency_spinbox.isEnabled() else 0,
            'volume': self.volume_slider.value() / 100.0,
            'panning': self.panning_slider.value() / 100.0,
            'wave_type': wave_type,
            'active': self.enable_checkbox.isChecked() and self.is_playing
        }
        self.tone_parameters_changed.emit(self.tone_id, parameters)
    
    def _apply_initial_style(self) -> None:
        """Aplica el estilo inicial del frame"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #0078d4;
                border-radius: 15px;
                background-color: #ffffff;
                margin: 5px;
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
        wave_type = self.wave_type_combo.currentText().lower()
        
        # Convertir nombres de ruido
        noise_mapping = {
            "ruido blanco": "white_noise",
            "ruido rosa": "pink_noise",
            "ruido marrón": "brown_noise"
        }
        
        if wave_type in noise_mapping:
            wave_type = noise_mapping[wave_type]
        
        return {
            'frequency': self.frequency_spinbox.value() if self.frequency_spinbox.isEnabled() else 0,
            'volume': self.volume_slider.value() / 100.0,
            'panning': self.panning_slider.value() / 100.0,
            'wave_type': wave_type,
            'active': self.enable_checkbox.isChecked() and self.is_playing,
            'is_playing': self.is_playing,
            'is_enabled': self.enable_checkbox.isChecked()
        }
