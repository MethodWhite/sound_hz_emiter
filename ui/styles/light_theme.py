"""
Estilos del tema claro - Separados del código lógico
"""

class LightThemeStyles:
    """Estilos para el tema claro"""
    
    @staticmethod
    def get_complete_stylesheet() -> str:
        """Retorna el stylesheet completo del tema claro"""
        return f"""
        {LightThemeStyles._get_main_window_styles()}
        {LightThemeStyles._get_button_styles()}
        {LightThemeStyles._get_input_styles()}
        {LightThemeStyles._get_container_styles()}
        {LightThemeStyles._get_scroll_styles()}
        """
    
    @staticmethod
    def _get_main_window_styles() -> str:
        return """
        QMainWindow {
            background-color: #f5f5f5;
            color: #333333;
        }
        QWidget {
            background-color: #ffffff;
            color: #333333;
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
            background-color: #cccccc;
            color: #666666;
        }
        """
    
    @staticmethod
    def _get_input_styles() -> str:
        return """
        QSpinBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 2px;
            background-color: white;
        }
        QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 8px;
            background: #e0e0e0;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #0078d4;
            border: 1px solid #0078d4;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 2px;
            background-color: white;
        }
        """
    
    @staticmethod
    def _get_container_styles() -> str:
        return """
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #0078d4;
        }
        QFrame {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #fafafa;
        }
        """
    
    @staticmethod
    def _get_scroll_styles() -> str:
        return """
        QScrollArea {
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: white;
        }
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #0078d4;
            border-radius: 6px;
            min-height: 20px;
        }
        """