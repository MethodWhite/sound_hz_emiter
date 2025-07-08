import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AudioVisualizer:
    @staticmethod
    def create_waveform_plot(parent=None):
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title('Waveform')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.grid(True)
        
        canvas = FigureCanvas(fig)
        if parent is not None:
            parent.layout().addWidget(canvas)
            
        return fig, ax, canvas
        
    @staticmethod
    def create_spectrum_plot(parent=None):
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title('Frequency Spectrum')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Magnitude')
        ax.grid(True)
        
        canvas = FigureCanvas(fig)
        if parent is not None:
            parent.layout().addWidget(canvas)
            
        return fig, ax, canvas
        
    @staticmethod
    def update_waveform_plot(ax, canvas, data, sample_rate):
        ax.clear()
        time = np.linspace(0, len(data)/sample_rate, num=len(data))
        ax.plot(time, data)
        ax.set_title('Waveform')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.grid(True)
        canvas.draw()
        
    @staticmethod
    def update_spectrum_plot(ax, canvas, spectrum, sample_rate):
        ax.clear()
        freq = np.linspace(0, sample_rate/2, len(spectrum))
        ax.plot(freq, spectrum)
        ax.set_title('Frequency Spectrum')
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Magnitude')
        ax.grid(True)
        canvas.draw()
