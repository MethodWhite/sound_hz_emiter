"""
Estilos del tema oscuro corregidos - Consistencia total
"""

class DarkThemeStyles:
    """Estilos para el tema oscuro con correcciones de consistencia"""
    
    @staticmethod
    def get_complete_stylesheet() -> str:
        """Retorna el stylesheet completo del tema oscuro corregido"""
        return f"""
        {DarkThemeStyles._get_main_window_styles()}
        {DarkThemeStyles._get_button_styles()}
        {DarkThemeStyles._get_input_styles()}
        {DarkThemeStyles._get_container_styles()}
        {DarkThemeStyles._get_scroll_styles()}
        {DarkThemeStyles._get_tone_control_styles()}
        {DarkThemeStyles._get_statistics_styles()}
        """
    
    @staticmethod
    def _get_main_window_styles() -> str:
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        """
    
    @staticmethod
    def _get_button_styles() -> str:
        return """
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #999999;
        }
        """
    
    @staticmethod
    def _get_input_styles() -> str:
        return """
        QSpinBox {
            background-color: #4a4a4a;
            border: 1px solid #666666;
            color: #ffffff;
            border-radius: 4px;
            padding: 4px;
        }
        QSpinBox:focus {
            border: 2px solid #0078d4;
            background-color: #525252;
        }
        QSlider::groove:horizontal {
            border: 1px solid #666666;
            height: 8px;
            background: #555555;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #64b5f6;
            border: 1px solid #42a5f5;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: #90caf9;
            border-color: #64b5f6;
        }
        QComboBox {
            background-color: #4a4a4a;
            border: 1px solid #666666;
            color: #ffffff;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox:focus {
            border: 2px solid #0078d4;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #555555;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        QComboBox QAbstractItemView {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #666666;
            selection-background-color: #0078d4;
        }
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 2px solid #666666;
            background-color: #4a4a4a;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        QCheckBox::indicator:hover {
            border-color: #64b5f6;
        }
        """
    
    @staticmethod
    def _get_container_styles() -> str:
        return """
        QGroupBox {
            font-weight: bold;
            border: 2px solid #666666;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #64b5f6;
            background-color: #3c3c3c;
        }
        QFrame {
            border: 1px solid #666666;
            border-radius: 8px;
            background-color: #4a4a4a;
            color: #ffffff;
        }
        QFrame[frameShape="4"] {
            /* QFrame::StyledPanel */
            border: 2px solid #666666;
            border-radius: 8px;
            background-color: #404040;
        }
        """
    
    @staticmethod
    def _get_scroll_styles() -> str:
        return """
        QScrollArea {
            border: 1px solid #666666;
            border-radius: 5px;
            background-color: #3c3c3c;
        }
        QScrollBar:vertical {
            background-color: #505050;
            width: 12px;
            border-radius: 6px;
            border: none;
        }
        QScrollBar::handle:vertical {
            background-color: #64b5f6;
            border-radius: 6px;
            min-height: 20px;
            margin: 1px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #90caf9;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: #505050;
            height: 12px;
            border-radius: 6px;
            border: none;
        }
        QScrollBar::handle:horizontal {
            background-color: #64b5f6;
            border-radius: 6px;
            min-width: 20px;
            margin: 1px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #90caf9;
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 0px;
        }
        """
    
    @staticmethod
    def _get_tone_control_styles() -> str:
        """Estilos específicos para controles de tono en modo oscuro"""
        return """
        /* Estilo específico para controles de tono */
        QFrame#ToneControl {
            border: 2px solid #64b5f6;
            border-radius: 15px;
            background-color: #404040;
            margin: 5px;
        }
        
        /* Headers de controles de tono */
        QFrame#ToneControlHeader {
            background-color: rgba(100, 181, 246, 0.2);
            border: 1px solid #64b5f6;
            border-radius: 8px;
            padding: 8px;
        }
        
        /* Secciones de controles */
        QFrame#ToneControlSection {
            background-color: rgba(74, 74, 74, 0.8);
            border: 1px solid #666666;
            border-radius: 8px;
            padding: 15px;
        }
        
        /* Sección de habilitación */
        QFrame#ToneEnableSection {
            background-color: rgba(40, 167, 69, 0.2);
            border: 1px solid #28a745;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Labels de control de tono */
        QLabel#ToneControlLabel {
            font-weight: bold;
            font-size: 12px;
            color: #e0e0e0;
            margin-bottom: 5px;
            background-color: transparent;
        }
        
        /* Labels de valor */
        QLabel#ToneValueLabel {
            font-size: 11px;
            font-weight: bold;
            color: #64b5f6;
            background-color: rgba(100, 181, 246, 0.1);
            border-radius: 4px;
            padding: 2px;
            text-align: center;
        }
        
        /* Spinboxes específicos para tonos */
        QSpinBox#ToneFrequencySpinBox {
            background-color: #525252;
            border: 2px solid #666666;
            border-radius: 6px;
            padding: 5px;
            font-size: 12px;
            font-weight: bold;
            color: #ffffff;
        }
        QSpinBox#ToneFrequencySpinBox:focus {
            border-color: #64b5f6;
            background-color: #5a5a5a;
        }
        QSpinBox#ToneFrequencySpinBox:disabled {
            background-color: #3a3a3a;
            color: #999999;
            border-color: #555555;
        }
        
        /* ComboBox específico para tipos de onda */
        QComboBox#WaveTypeComboBox {
            background-color: #525252;
            border: 2px solid #666666;
            border-radius: 6px;
            padding: 5px;
            font-size: 12px;
            font-weight: bold;
            color: #ffffff;
        }
        QComboBox#WaveTypeComboBox:focus {
            border-color: #64b5f6;
        }
        
        /* Sliders específicos para controles de tono */
        QSlider#VolumeSlider::groove:horizontal {
            border: 1px solid #666666;
            height: 10px;
            background: #555555;
            margin: 2px 0;
            border-radius: 5px;
        }
        QSlider#VolumeSlider::handle:horizontal {
            background: #64b5f6;
            border: 2px solid #64b5f6;
            width: 20px;
            margin: -5px 0;
            border-radius: 10px;
        }
        QSlider#VolumeSlider::handle:horizontal:hover {
            background: #90caf9;
            border-color: #90caf9;
        }
        
        QSlider#PanningSlider::groove:horizontal {
            border: 1px solid #666666;
            height: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #ff6b6b, stop:0.5 #666666, stop:1 #4ecdc4);
            margin: 2px 0;
            border-radius: 5px;
        }
        QSlider#PanningSlider::handle:horizontal {
            background: #e0e0e0;
            border: 2px solid #e0e0e0;
            width: 20px;
            margin: -5px 0;
            border-radius: 10px;
        }
        QSlider#PanningSlider::handle:horizontal:hover {
            background: #ffffff;
            border-color: #ffffff;
        }
        """
    
    @staticmethod
    def _get_statistics_styles() -> str:
        """Estilos para el panel de estadísticas en modo oscuro"""
        return """
        /* Panel de estadísticas */
        QGroupBox#StatisticsPanel {
            background-color: #3c3c3c;
            border: 2px solid #666666;
            color: #ffffff;
        }
        
        /* Secciones de estadísticas */
        QFrame#StatsSection {
            background-color: #404040;
            border: 1px solid #666666;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Progress bars en estadísticas */
        QProgressBar {
            border: 1px solid #666666;
            border-radius: 4px;
            text-align: center;
            font-weight: bold;
            color: #ffffff;
            background-color: #4a4a4a;
        }
        QProgressBar::chunk {
            background-color: #64b5f6;
            border-radius: 3px;
        }
        """
