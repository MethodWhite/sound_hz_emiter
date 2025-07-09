from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import pyqtgraph as pg
import numpy as np

class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.plot = pg.PlotWidget()
        self.plot.setBackground('w')
        self.plot.setLabel('left', 'Amplitude')
        self.plot.setLabel('bottom', 'Time', 's')
        self.plot.showGrid(x=True, y=True)
        
        self.curve = self.plot.plot(pen=pg.mkPen(color='b', width=2))
        layout.addWidget(self.plot)
        
    def update_waveform(self, samples):
        if len(samples) > 0:
            x = np.linspace(0, len(samples)/44100, len(samples))
            self.curve.setData(x, samples)