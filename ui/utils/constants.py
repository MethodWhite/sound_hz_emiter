"""
Constantes mejoradas - Con todos los tipos de onda y configuraciones
"""

class UIConstants:
    """Constantes de la interfaz de usuario mejoradas"""
    WINDOW_WIDTH = 1400  # Más ancho para estadísticas
    WINDOW_HEIGHT = 900  # Más alto
    MIN_WINDOW_WIDTH = 1000
    MIN_WINDOW_HEIGHT = 700
    TONE_CONTROL_HEIGHT = 250  # Más alto para nuevos controles
    TONE_CONTROL_MIN_WIDTH = 500  # Más ancho
    BUTTON_HEIGHT = 35
    CONTROL_BUTTON_SIZE = 40  # Botones más grandes
    LAYOUT_MARGIN = 15
    LAYOUT_SPACING = 12
    COMPONENT_SPACING = 10

class AudioConstants:
    """Constantes del sistema de audio mejoradas"""
    MAX_CONCURRENT_TONES = 32  # Más tonos simultáneos
    MIN_FREQUENCY = 1  # Frecuencia mínima más baja
    MAX_FREQUENCY = 22000  # Frecuencia máxima más alta
    SAMPLE_RATE = 44100
    BUFFER_SIZE = 512
    
    # Configuraciones de calidad de grabación
    RECORDING_QUALITY = {
        'Estándar': {'bitrate': 128, 'sample_rate': 44100},
        'Alta': {'bitrate': 256, 'sample_rate': 48000},
        'Máxima': {'bitrate': 320, 'sample_rate': 48000}
    }
    
    # Formatos de exportación soportados
    EXPORT_FORMATS = ['WAV', 'MP3', 'FLAC']

class WaveTypes:
    """Tipos de onda disponibles expandidos"""
    
    # Tipos tradicionales
    TRADITIONAL_WAVES = ["Seno", "Cuadrada", "Triángulo", "Sierra"]
    
    # Tipos de ruido
    NOISE_TYPES = ["Ruido Blanco", "Ruido Rosa", "Ruido Marrón"]
    
    # Mapeo para conversión interna
    WAVE_MAPPING = {
        "seno": "sine",
        "cuadrada": "square",
        "triángulo": "triangle",
        "sierra": "sawtooth",
        "ruido blanco": "white_noise",
        "ruido rosa": "pink_noise",
        "ruido marrón": "brown_noise"
    }
    
    @staticmethod
    def get_all_types():
        """Retorna todos los tipos de onda disponibles"""
        return WaveTypes.TRADITIONAL_WAVES + WaveTypes.NOISE_TYPES
    
    @staticmethod
    def get_traditional_types():
        """Retorna solo tipos de onda tradicionales"""
        return WaveTypes.TRADITIONAL_WAVES.copy()
    
    @staticmethod
    def get_noise_types():
        """Retorna solo tipos de ruido"""
        return WaveTypes.NOISE_TYPES.copy()
    
    @staticmethod
    def is_noise_type(wave_type):
        """Verifica si un tipo de onda es ruido"""
        return wave_type.lower() in [t.lower() for t in WaveTypes.NOISE_TYPES]
    
    @staticmethod
    def get_internal_name(wave_type):
        """Convierte nombre de onda a formato interno"""
        return WaveTypes.WAVE_MAPPING.get(wave_type.lower(), wave_type.lower())

class PomodoroPresets:
    """Presets predefinidos para Pomodoro"""
    
    PRESETS = {
        "Clásico": {
            "work": 25,
            "short_break": 5,
            "long_break": 15,
            "cycles": 4,
            "description": "Técnica Pomodoro tradicional de Francesco Cirillo"
        },
        "Extendido": {
            "work": 50,
            "short_break": 10,
            "long_break": 30,
            "cycles": 3,
            "description": "Sesiones más largas para trabajo profundo"
        },
        "Intensivo": {
            "work": 90,
            "short_break": 20,
            "long_break": 45,
            "cycles": 2,
            "description": "Para proyectos que requieren concentración extrema"
        },
        "Rápido": {
            "work": 15,
            "short_break": 3,
            "long_break": 10,
            "cycles": 6,
            "description": "Ciclos cortos para tareas fragmentadas"
        },
        "Personalizado": {
            "work": 25,
            "short_break": 5,
            "long_break": 15,
            "cycles": 4,
            "description": "Configuración personalizable"
        }
    }
    
    @staticmethod
    def get_preset_names():
        """Retorna nombres de presets disponibles"""
        return list(PomodoroPresets.PRESETS.keys())
    
    @staticmethod
    def get_preset(name):
        """Retorna configuración de un preset específico"""
        return PomodoroPresets.PRESETS.get(name, PomodoroPresets.PRESETS["Clásico"])

class ThemeConstants:
    """Constantes para temas"""
    
    # Colores principales
    PRIMARY_BLUE = "#0078d4"
    SUCCESS_GREEN = "#28a745"
    DANGER_RED = "#dc3545"
    WARNING_YELLOW = "#ffc107"
    INFO_CYAN = "#17a2b8"
    
    # Colores de fondo para modo claro
    LIGHT_BACKGROUND = "#ffffff"
    LIGHT_SURFACE = "#f8f9fa"
    LIGHT_BORDER = "#dee2e6"
    
    # Colores de fondo para modo oscuro
    DARK_BACKGROUND = "#2b2b2b"
    DARK_SURFACE = "#3c3c3c"
    DARK_BORDER = "#666666"
    
    # Colores de texto
    LIGHT_TEXT = "#212529"
    DARK_TEXT = "#ffffff"
    MUTED_TEXT = "#6c757d"

class KeyboardShortcuts:
    """Atajos de teclado de la aplicación"""
    
    SHORTCUTS = {
        # Controles generales
        'quit': 'Ctrl+Q',
        'toggle_theme': 'Ctrl+T',
        'show_help': 'F1',
        
        # Timer y Pomodoro
        'start_timer': 'Ctrl+Space',
        'stop_timer': 'Ctrl+S',
        'reset_timer': 'Ctrl+R',
        'start_pomodoro': 'Ctrl+P',
        
        # Tonos
        'add_tone': 'Ctrl+N',
        'play_all': 'Ctrl+A',
        'stop_all': 'Ctrl+Shift+S',
        'clear_all': 'Ctrl+Shift+C',
        
        # Audio
        'toggle_audio': 'Ctrl+M',
        'volume_up': 'Ctrl+Plus',
        'volume_down': 'Ctrl+Minus',
        
        # Grabación
        'start_recording': 'Ctrl+Shift+R',
        'stop_recording': 'Ctrl+Shift+T'
    }
    
    @staticmethod
    def get_shortcut(action):
        """Retorna atajo para una acción específica"""
        return KeyboardShortcuts.SHORTCUTS.get(action, '')

class FileConstants:
    """Constantes para manejo de archivos"""
    
    # Directorios
    CONFIG_DIR = "config"
    RECORDINGS_DIR = "recordings"
    PRESETS_DIR = "presets"
    LOGS_DIR = "logs"
    
    # Extensiones de archivo
    CONFIG_EXTENSION = ".json"
    PRESET_EXTENSION = ".json"
    LOG_EXTENSION = ".log"
    
    # Nombres de archivos
    MAIN_CONFIG_FILE = "app_config.json"
    USER_PRESETS_FILE = "user_presets.json"
    SESSION_LOG_FILE = "session.log"
    
    @staticmethod
    def get_config_path():
        """Retorna ruta del archivo de configuración principal"""
        return f"{FileConstants.CONFIG_DIR}/{FileConstants.MAIN_CONFIG_FILE}"
    
    @staticmethod
    def get_recordings_path():
        """Retorna ruta del directorio de grabaciones"""
        return FileConstants.RECORDINGS_DIR
