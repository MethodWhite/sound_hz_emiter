import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SpectrumWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Espectro de Frecuencias")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#FFFFFF')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Amplitud')
        self.plot_widget.setLabel('bottom', 'Frecuencia (Hz)')
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.setYRange(0, 1)
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#1976D2', width=2))
        layout.addWidget(self.plot_widget)
        
        self.setLayout(layout)
    
    def update_spectrum(self, freqs, magnitudes):
        if len(freqs) == 0 or len(magnitudes) == 0:
            return
        
        # Suavizar la visualización
        smoothed = np.convolve(magnitudes, np.ones(5)/5, mode='same')
        
        # Filtrar solo frecuencias audibles
        mask = (freqs >= 20) & (freqs <= 20000)
        self.curve.setData(freqs[mask], smoothed[mask])