from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
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
        title = QLabel("Control de Frecuencias")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Botón para añadir
        self.add_button = QPushButton("+ Añadir Frecuencia")
        self.add_button.clicked.connect(self.add_frequency_row)
        layout.addWidget(self.add_button)
        
        # Añadir una fila inicial
        self.add_frequency_row()
    
    def add_frequency_row(self, freq=440.0, volume=0.5):
        row_id = self.next_id
        self.next_id += 1
        
        row = FrequencyRow(row_id, freq, volume)
        row.frequency_changed.connect(self.update_frequency)
        row.volume_changed.connect(self.update_volume)
        row.remove_requested.connect(self.remove_row)
        
        self.rows.append(row)
        self.layout().insertWidget(self.layout().count() - 1, row)  # Insertar antes del botón
        
        # Registrar en el servicio de audio
        self.audio_service.add_tone(row_id, freq, volume)
    
    def remove_row(self, row_id):
        for i, row in enumerate(self.rows):
            if row.row_id == row_id:
                row.deleteLater()
                self.rows.pop(i)
                self.audio_service.remove_tone(row_id)
                break
    
    def update_frequency(self, row_id, frequency):
        # Buscar la fila para obtener el volumen actual
        for row in self.rows:
            if row.row_id == row_id:
                volume = row.volume_slider.value() / 100.0
                self.audio_service.update_tone(row_id, frequency, volume)
                break
    
    def update_volume(self, row_id, volume):
        # Buscar la fila para obtener la frecuencia actual
        for row in self.rows:
            if row.row_id == row_id:
                frequency = row.freq_spinbox.value()
                self.audio_service.update_tone(row_id, frequency, volume)
                break