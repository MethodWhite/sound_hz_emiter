from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import pyqtgraph as pg
import numpy as np

class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.plot = pg.PlotWidget()
        self.plot.setBackground('#FFFFFF')
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel('left', 'Amplitude')
        self.plot.setLabel('bottom', 'Time', 's')
        self.plot.setYRange(-1, 1)
        
        self.curve = self.plot.plot(pen=pg.mkPen(color='#1976D2', width=2))
        layout.addWidget(self.plot)
        
    def update_waveform(self, samples):
        if len(samples) > 0:
            x = np.linspace(0, 0.1, len(samples))  # Muestra 100ms de audio
            self.curve.setData(x, samples)