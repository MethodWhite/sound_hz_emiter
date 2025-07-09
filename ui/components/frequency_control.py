from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QHBoxLayout  # Añadir QHBoxLayout
from .frequency_row import FrequencyRow

class FrequencyControl(QWidget):
    def __init__(self, audio_service):
        super().__init__()
        self.audio_service = audio_service
        self.rows = []
        self.next_id = 0
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Título
        title_layout = QHBoxLayout()
        title = QLabel("Control de Frecuencias")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        title_layout.addWidget(title)
        
        # Botón para añadir
        self.add_button = QPushButton("+ Añadir Frecuencia")
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.add_button.clicked.connect(self.add_frequency_row)
        title_layout.addWidget(self.add_button)
        
        layout.addLayout(title_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #ddd;")
        layout.addWidget(separator)
        
        # Contenedor para filas
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.rows_container)
        
        # Añadir una fila inicial
        self.add_frequency_row()
    
    def add_frequency_row(self, freq=440.0, volume=0.5, wave_type="Seno", panning=0.0):
        row_id = self.next_id
        self.next_id += 1
        
        row = FrequencyRow(row_id, freq, volume, wave_type, panning)
        row.frequency_changed.connect(self.update_frequency)
        row.volume_changed.connect(self.update_volume)
        row.wave_type_changed.connect(self.update_wave_type)
        row.panning_changed.connect(self.update_panning)
        row.remove_requested.connect(self.remove_row)
        
        self.rows.append(row)
        self.rows_layout.addWidget(row)
        
        # Registrar en el servicio de audio
        self.audio_service.add_tone(row_id, freq, volume, wave_type, panning)
    
    def remove_row(self, row_id):
        for i, row in enumerate(self.rows):
            if row.row_id == row_id:
                row.deleteLater()
                self.rows.pop(i)
                self.audio_service.remove_tone(row_id)
                break
    
    def update_frequency(self, row_id, frequency):
        self.audio_service.update_frequency(row_id, frequency)
    
    def update_volume(self, row_id, volume):
        self.audio_service.update_volume(row_id, volume)
    
    def update_wave_type(self, row_id, wave_type):
        self.audio_service.update_wave_type(row_id, wave_type)
    
    def update_panning(self, row_id, panning):
        self.audio_service.update_panning(row_id, panning)