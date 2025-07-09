from PySide6.QtWidgets import QWidget, QHBoxLayout, QDoubleSpinBox, QSlider, QPushButton
from PySide6.QtCore import Signal, Qt

class FrequencyRow(QWidget):
    frequency_changed = Signal(int, float)
    volume_changed = Signal(int, float)
    remove_requested = Signal(int)
    
    def __init__(self, row_id, freq=440.0, volume=0.5):
        super().__init__()
        self.row_id = row_id
        
        layout = QHBoxLayout()
        
        # Frecuencia
        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.setRange(20.0, 20000.0)
        self.freq_spinbox.setValue(freq)
        self.freq_spinbox.setSingleStep(1.0)
        self.freq_spinbox.setSuffix(" Hz")
        self.freq_spinbox.valueChanged.connect(self._on_frequency_changed)
        layout.addWidget(self.freq_spinbox)
        
        # Volumen
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(volume * 100))
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        layout.addWidget(self.volume_slider)
        
        # Botón para eliminar
        self.remove_button = QPushButton("✕")
        self.remove_button.setFixedWidth(30)
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.row_id))
        layout.addWidget(self.remove_button)
        
        self.setLayout(layout)
    
    def _on_frequency_changed(self, value):
        self.frequency_changed.emit(self.row_id, value)
    
    def _on_volume_changed(self, value):
        volume = value / 100.0
        self.volume_changed.emit(self.row_id, volume)