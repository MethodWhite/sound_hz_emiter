"""
Controles globales de audio
"""

from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QSlider, QLabel)
from PySide6.QtCore import Qt, Signal

class AudioControls(QGroupBox):
    """Controles globales del sistema de audio"""
    
    clear_all_requested = Signal()
    master_volume_changed = Signal(float)
    audio_system_toggled = Signal(bool)
    
    def __init__(self, audio_engine, theme_manager):
        super().__init__("🎛️ Controles Globales")
        self.audio_engine = audio_engine
        self.theme_manager = theme_manager
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Volumen maestro
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("🔊 Volumen General:"))
        
        self.master_volume_slider = QSlider(Qt.Horizontal)
        self.master_volume_slider.setRange(0, 100)
        self.master_volume_slider.setValue(50)
        vol_layout.addWidget(self.master_volume_slider)
        
        self.volume_label = QLabel("50%")
        vol_layout.addWidget(self.volume_label)
        
        layout.addLayout(vol_layout)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        self.start_audio_button = QPushButton("🔊 Iniciar Audio")
        self.stop_audio_button = QPushButton("🔇 Detener Audio")
        self.clear_all_button = QPushButton("🗑️ Limpiar Todo")
        self.theme_button = QPushButton("🎨 Cambiar Tema")
        
        buttons_layout.addWidget(self.start_audio_button)
        buttons_layout.addWidget(self.stop_audio_button)
        buttons_layout.addWidget(self.clear_all_button)
        buttons_layout.addWidget(self.theme_button)
        
        layout.addLayout(buttons_layout)
        
        # Información del sistema
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Sistema de audio: Detenido")
        self.info_label.setStyleSheet("font-size: 10px; color: #666;")
        info_layout.addWidget(self.info_label)
        
        layout.addLayout(info_layout)
    
    def connect_signals(self):
        # Controles locales
        self.master_volume_slider.valueChanged.connect(self.update_volume_label)
        self.master_volume_slider.valueChanged.connect(
            lambda v: self.master_volume_changed.emit(v / 100.0)
        )
        
        self.start_audio_button.clicked.connect(self.start_audio_system)
        self.stop_audio_button.clicked.connect(self.stop_audio_system)
        self.clear_all_button.clicked.connect(self.clear_all_requested.emit)
        self.theme_button.clicked.connect(self.toggle_theme)
        
        # Señales del motor de audio
        if self.audio_engine:
            self.audio_engine.audio_started.connect(self.on_audio_started)
            self.audio_engine.audio_stopped.connect(self.on_audio_stopped)
    
    def update_volume_label(self):
        volume = self.master_volume_slider.value()
        self.volume_label.setText(f"{volume}%")
    
    def start_audio_system(self):
        if self.audio_engine and self.audio_engine.start_audio():
            self.audio_system_toggled.emit(True)
    
    def stop_audio_system(self):
        if self.audio_engine:
            self.audio_engine.stop_audio()
            self.audio_system_toggled.emit(False)
    
    def toggle_theme(self):
        if self.theme_manager:
            self.theme_manager.toggle_theme()
    
    def on_audio_started(self):
        self.info_label.setText("🔊 Sistema de audio: Activo")
        self.info_label.setStyleSheet("font-size: 10px; color: #28a745; font-weight: bold;")
        self.start_audio_button.setEnabled(False)
        self.stop_audio_button.setEnabled(True)
    
    def on_audio_stopped(self):
        self.info_label.setText("🔇 Sistema de audio: Detenido")
        self.info_label.setStyleSheet("font-size: 10px; color: #dc3545; font-weight: bold;")
        self.start_audio_button.setEnabled(True)
        self.stop_audio_button.setEnabled(False)
