import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout  # Añadir QHBoxLayout
from PySide6.QtGui import QColor

class SpectrumWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Espectro de Frecuencias en Tiempo Real")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        layout.addWidget(title)
        
        # Gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#FFFFFF')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Amplitud', units='')
        self.plot_widget.setLabel('bottom', 'Frecuencia', units='Hz')
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.setYRange(0, 1)
        self.plot_widget.setXRange(20, 20000)
        
        # Configurar colores y estilo
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#333'))
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='#333'))
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#1976D2', width=2))
        layout.addWidget(self.plot_widget, 1)
        
        # Leyenda de colores
        color_legend = QWidget()
        color_layout = QHBoxLayout(color_legend)
        color_layout.addWidget(QLabel("Azul: Espectro actual"))
        color_layout.addStretch()
        color_layout.setContentsMargins(5, 0, 5, 0)
        layout.addWidget(color_legend)
        
        self.setLayout(layout)
    
    def update_spectrum(self, freqs, magnitudes):
        if len(freqs) == 0 or len(magnitudes) == 0:
            return
        
        # Suavizar la visualización
        window_size = min(11, len(magnitudes) // 2 or 1)
        if window_size % 2 == 0:  # Asegurar tamaño impar
            window_size += 1
        
        smoothed = np.convolve(magnitudes, np.ones(window_size)/window_size, mode='same')
        
        # Filtrar solo frecuencias audibles
        mask = (freqs >= 20) & (freqs <= 20000)
        self.curve.setData(freqs[mask], smoothed[mask])