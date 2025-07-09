from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  # Añade QHBoxLayout aquí
    QApplication, QStatusBar, QSplitter, QLabel,
    QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPalette, QColor

from ui.components.frequency_control import FrequencyControl
from ui.components.timer_control import TimerControl
from ui.components.spectrum_widget import SpectrumWidget
from core.audio_service import AudioService


class MainWindow(QMainWindow):
    theme_changed = Signal(bool)  # True for dark, False for light
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Hz Emitter")
        self.setGeometry(100, 100, 1200, 800)
        self.is_dark_theme = False
        
        # Audio service
        self.audio_service = AudioService()
        
        # Setup UI
        self.init_ui()
        self.apply_light_theme()
        
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)  # Ahora QHBoxLayout está definido
        
        # Title
        self.title_label = QLabel("Sound Frequency Emitter")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        # Theme toggle button
        self.theme_btn = QToolButton()
        self.theme_btn.setIcon(QIcon.fromTheme("weather-sunny"))
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn, alignment=Qt.AlignRight)
        
        main_layout.addWidget(header)
        
        # Main content
        splitter = QSplitter(Qt.Vertical)
        
        # Control panel
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        # Timer control
        self.timer_control = TimerControl(self.audio_service)
        control_layout.addWidget(self.timer_control)
        
        # Frequency control
        self.frequency_control = FrequencyControl(self.audio_service)
        control_layout.addWidget(self.frequency_control)
        
        splitter.addWidget(control_panel)
        
        # Spectrum
        self.spectrum_widget = SpectrumWidget()
        splitter.addWidget(self.spectrum_widget)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.apply_dark_theme()
            self.theme_btn.setIcon(QIcon.fromTheme("weather-sunny"))
        else:
            self.apply_light_theme()
            self.theme_btn.setIcon(QIcon.fromTheme("weather-night"))
        self.theme_changed.emit(self.is_dark_theme)
        
    def apply_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(233, 231, 227))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.instance().setPalette(palette)
        
    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        QApplication.instance().setPalette(palette)