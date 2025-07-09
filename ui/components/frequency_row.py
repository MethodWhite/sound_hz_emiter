from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QSlider, QPushButton, QComboBox, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette, QColor

class FrequencyRow(QWidget):
    frequency_changed = Signal(int, float)
    volume_changed = Signal(int, float)
    wave_type_changed = Signal(int, str)
    panning_changed = Signal(int, float)
    remove_requested = Signal(int)
    
    WAVE_TYPES = ["Seno", "Cuadrada", "Triangular", "Diente de Sierra", "Ruido Blanco", "Ruido Rosa", "Ruido Marrón"]
    
    def __init__(self, row_id, freq=440.0, volume=0.5, wave_type="Seno", panning=0.0):
        super().__init__()
        self.row_id = row_id
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Frecuencia
        freq_layout = QVBoxLayout()  # Ahora QVBoxLayout está importado
        freq_layout.addWidget(QLabel("Frecuencia (Hz)"))
        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.setRange(1.0, 20000.0)
        self.freq_spinbox.setValue(freq)
        self.freq_spinbox.setSingleStep(1.0)
        self.freq_spinbox.setDecimals(0)
        self.freq_spinbox.valueChanged.connect(self._on_frequency_changed)
        freq_layout.addWidget(self.freq_spinbox)
        layout.addLayout(freq_layout)
        
        # Volumen
        vol_layout = QVBoxLayout()
        vol_layout.addWidget(QLabel("Volumen"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(volume * 100))
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        vol_layout.addWidget(self.volume_slider)
        layout.addLayout(vol_layout)
        
        # Tipo de onda
        wave_layout = QVBoxLayout()
        wave_layout.addWidget(QLabel("Tipo de Onda"))
        self.wave_type_combo = QComboBox()
        self.wave_type_combo.addItems(self.WAVE_TYPES)
        self.wave_type_combo.setCurrentText(wave_type)
        self.wave_type_combo.currentTextChanged.connect(self._on_wave_type_changed)
        wave_layout.addWidget(self.wave_type_combo)
        layout.addLayout(wave_layout)
        
        # Panning
        pan_layout = QVBoxLayout()
        pan_layout.addWidget(QLabel("Panning"))
        panning_container = QHBoxLayout()
        
        self.left_label = QLabel("L")
        panning_container.addWidget(self.left_label)
        
        self.panning_slider = QSlider(Qt.Orientation.Horizontal)
        self.panning_slider.setRange(-100, 100)
        self.panning_slider.setValue(int(panning * 100))
        self.panning_slider.valueChanged.connect(self._on_panning_changed)
        panning_container.addWidget(self.panning_slider)
        
        self.right_label = QLabel("R")
        panning_container.addWidget(self.right_label)
        
        pan_layout.addLayout(panning_container)
        layout.addLayout(pan_layout)
        
        # Botón para eliminar
        self.remove_button = QPushButton("✕")
        self.remove_button.setFixedWidth(40)
        self.remove_button.setStyleSheet("background-color: #ff6666; color: white;")
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.row_id))
        layout.addWidget(self.remove_button)
        
        self.setLayout(layout)
        self.update_panning_colors()
    
    def _on_frequency_changed(self, value):
        self.frequency_changed.emit(self.row_id, value)
    
    def _on_volume_changed(self, value):
        volume = value / 100.0
        self.volume_changed.emit(self.row_id, volume)
    
    def _on_wave_type_changed(self, value):
        self.wave_type_changed.emit(self.row_id, value)
    
    def _on_panning_changed(self, value):
        panning = value / 100.0
        self.panning_changed.emit(self.row_id, panning)
        self.update_panning_colors()
    
    def update_panning_colors(self):
        pan_value = self.panning_slider.value()
        left_intensity = max(150, 255 - abs(pan_value) * 1.5)
        right_intensity = max(150, 255 - abs(pan_value) * 1.5)
        
        if pan_value < 0:
            left_intensity = 255
        elif pan_value > 0:
            right_intensity = 255
        
        # Aplicar colores a las etiquetas
        self.left_label.setStyleSheet(f"color: rgb({left_intensity}, 0, 0); font-weight: bold;")
        self.right_label.setStyleSheet(f"color: rgb(0, 0, {right_intensity}); font-weight: bold;")