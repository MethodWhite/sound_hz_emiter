"""
Constantes de la aplicación - Centralizadas para fácil mantenimiento
"""

class UIConstants:
    """Constantes de la interfaz de usuario"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    TONE_CONTROL_HEIGHT = 200
    TONE_CONTROL_MIN_WIDTH = 400
    BUTTON_HEIGHT = 35
    CONTROL_BUTTON_SIZE = 35
    LAYOUT_MARGIN = 15
    LAYOUT_SPACING = 10
    COMPONENT_SPACING = 8

class AudioConstants:
    """Constantes del sistema de audio"""
    MAX_CONCURRENT_TONES = 16
    MIN_FREQUENCY = 20
    MAX_FREQUENCY = 20000
    SAMPLE_RATE = 44100
    BUFFER_SIZE = 512

class WaveTypes:
    """Tipos de onda disponibles"""
    @staticmethod
    def get_all_types():
        return ["Seno", "Cuadrada", "Triángulo", "Sierra"]
