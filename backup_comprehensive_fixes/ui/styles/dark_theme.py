"""
Estilos del tema oscuro - Separados del código lógico
"""

class DarkThemeStyles:
    """Estilos para el tema oscuro"""
    
    @staticmethod
    def get_complete_stylesheet() -> str:
        """Retorna el stylesheet completo del tema oscuro"""
        return f"""
        {DarkThemeStyles._get_main_window_styles()}
        {DarkThemeStyles._get_button_styles()}
        {DarkThemeStyles._get_input_styles()}
        {DarkThemeStyles._get_container_styles()}
        {DarkThemeStyles._get_scroll_styles()}
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
            background-color: #404040;
            border: 1px solid #555555;
            color: #ffffff;
            border-radius: 4px;
            padding: 2px;
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
        QComboBox {
            background-color: #404040;
            border: 1px solid #555555;
            color: #ffffff;
            border-radius: 4px;
            padding: 2px;
        }
        """
    
    @staticmethod
    def _get_container_styles() -> str:
        return """
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #64b5f6;
        }
        QFrame {
            border: 1px solid #555555;
            border-radius: 8px;
            background-color: #404040;
        }
        """
    
    @staticmethod
    def _get_scroll_styles() -> str:
        return """
        QScrollArea {
            border: 1px solid #555555;
            border-radius: 5px;
            background-color: #3c3c3c;
        }
        QScrollBar:vertical {
            background-color: #505050;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #64b5f6;
            border-radius: 6px;
            min-height: 20px;
        }
        """