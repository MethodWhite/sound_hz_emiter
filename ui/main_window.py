"""
Ventana principal refactorizada - Solo coordinación y layout
Aplicando Clean Code: Single Responsibility Principle
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QGroupBox, QScrollArea, QPushButton, QStatusBar)
from PySide6.QtCore import Qt

from .components.tone_control import ToneControl
from .components.timer_control import TimerControl
from .components.pomodoro_control import PomodoroControl
from .components.audio_controls import AudioControls
from .styles.theme_manager import ThemeManager
from .audio.audio_engine import AudioEngine
from .utils.constants import UIConstants

class MainWindow(QMainWindow):
    """
    Ventana principal refactorizada con responsabilidad única
    Solo se encarga de la coordinación entre componentes
    """
    
    def __init__(self):
        super().__init__()
        
        # Inicializar componentes principales
        self.audio_engine = AudioEngine()
        self.theme_manager = ThemeManager(self)
        
        # Contenedores de controles
        self.tone_controls = {}
        self.next_tone_id = 1
        
        # Configurar ventana
        self._setup_window()
        
        # Crear interfaz
        self._create_user_interface()
        
        # Conectar señales
        self._connect_signals()
        
        # Aplicar tema inicial
        self.theme_manager.apply_current_theme()
        
        # Agregar primer tono
        self._add_new_tone()
    
    def _setup_window(self) -> None:
        """Configura las propiedades básicas de la ventana"""
        self.setWindowTitle("🔊 Sound Hz Emitter v2.0 - Clean Code Edition")
        self.setGeometry(100, 100, UIConstants.WINDOW_WIDTH, UIConstants.WINDOW_HEIGHT)
        self.setMinimumSize(UIConstants.MIN_WINDOW_WIDTH, UIConstants.MIN_WINDOW_HEIGHT)
    
    def _create_user_interface(self) -> None:
        """Crea la interfaz de usuario principal"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(UIConstants.LAYOUT_MARGIN, UIConstants.LAYOUT_MARGIN,
                                     UIConstants.LAYOUT_MARGIN, UIConstants.LAYOUT_MARGIN)
        main_layout.setSpacing(UIConstants.LAYOUT_SPACING)
        
        # Panel izquierdo (controles)
        self._create_controls_panel(main_layout)
        
        # Panel derecho (información)
        self._create_info_panel(main_layout)
        
        # Barra de estado
        self._create_status_bar()
    
    def _create_controls_panel(self, parent_layout: QHBoxLayout) -> None:
        """Crea el panel de controles (lado izquierdo)"""
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(UIConstants.LAYOUT_SPACING)
        
        # Timer y Pomodoro
        self._create_timer_controls(controls_layout)
        
        # Controles de tonos
        self._create_tone_controls_section(controls_layout)
        
        # Controles globales
        self._create_global_controls(controls_layout)
        
        parent_layout.addWidget(controls_widget, 2)  # 2/3 del espacio
    
    def _create_timer_controls(self, parent_layout: QVBoxLayout) -> None:
        """Crea los controles de temporizador y Pomodoro"""
        # Timer control
        self.timer_control = TimerControl()
        parent_layout.addWidget(self.timer_control)
        
        # Pomodoro control
        self.pomodoro_control = PomodoroControl()
        parent_layout.addWidget(self.pomodoro_control)
    
    def _create_tone_controls_section(self, parent_layout: QVBoxLayout) -> None:
        """Crea la sección de controles de tonos"""
        tones_group = QGroupBox("🎵 Control de Tonos")
        tones_layout = QVBoxLayout(tones_group)
        
        # Botones superiores
        self._create_tone_action_buttons(tones_layout)
        
        # Área de scroll para tonos
        self._create_tones_scroll_area(tones_layout)
        
        parent_layout.addWidget(tones_group, 1)  # Expandible
    
    def _create_tone_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Crea los botones de acción para tonos"""
        buttons_layout = QHBoxLayout()
        
        add_tone_button = QPushButton("➕ Agregar Nuevo Tono")
        add_tone_button.setFixedHeight(UIConstants.BUTTON_HEIGHT)
        add_tone_button.clicked.connect(self._add_new_tone)
        buttons_layout.addWidget(add_tone_button)
        
        play_all_button = QPushButton("▶ Todo")
        play_all_button.setFixedSize(80, UIConstants.BUTTON_HEIGHT)
        play_all_button.clicked.connect(self._play_all_tones)
        buttons_layout.addWidget(play_all_button)
        
        stop_all_button = QPushButton("⏹ Todo")
        stop_all_button.setFixedSize(80, UIConstants.BUTTON_HEIGHT)
        stop_all_button.clicked.connect(self._stop_all_tones)
        buttons_layout.addWidget(stop_all_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def _create_tones_scroll_area(self, parent_layout: QVBoxLayout) -> None:
        """Crea el área de scroll para los controles de tonos"""
        self.tones_scroll_area = QScrollArea()
        self.tones_scroll_area.setWidgetResizable(True)
        self.tones_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tones_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tones_scroll_area.setMinimumHeight(350)
        self.tones_scroll_area.setMaximumHeight(550)
        
        self.tones_container_widget = QWidget()
        self.tones_layout = QVBoxLayout(self.tones_container_widget)
        self.tones_layout.setSpacing(12)
        self.tones_layout.setContentsMargins(10, 10, 10, 10)
        self.tones_layout.addStretch()
        
        self.tones_scroll_area.setWidget(self.tones_container_widget)
        parent_layout.addWidget(self.tones_scroll_area, 1)
    
    def _create_global_controls(self, parent_layout: QVBoxLayout) -> None:
        """Crea los controles globales"""
        self.audio_controls = AudioControls(self.audio_engine, self.theme_manager)
        parent_layout.addWidget(self.audio_controls)
    
    def _create_info_panel(self, parent_layout: QHBoxLayout) -> None:
        """Crea el panel de información (lado derecho)"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # Aquí iría el panel de información refactorizado
        # (Estadísticas, ayuda, etc.)
        
        parent_layout.addWidget(info_widget, 1)  # 1/3 del espacio
    
    def _create_status_bar(self) -> None:
        """Crea la barra de estado"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🔊 Sound Hz Emitter v2.0 Clean Code - Listo para usar")
    
    def _connect_signals(self) -> None:
        """Conecta las señales entre componentes"""
        # Señales del motor de audio
        self.audio_engine.audio_started.connect(self._on_audio_started)
        self.audio_engine.audio_stopped.connect(self._on_audio_stopped)
        
        # Señales de controles globales
        self.audio_controls.clear_all_requested.connect(self._clear_all_tones)
    
    def _add_new_tone(self) -> None:
        """Agrega un nuevo control de tono"""
        tone_id = self.next_tone_id
        self.next_tone_id += 1
        
        tone_control = ToneControl(tone_id)
        tone_control.tone_parameters_changed.connect(self._on_tone_parameters_changed)
        tone_control.tone_deletion_requested.connect(self._remove_tone)
        
        # Insertar antes del spacer
        spacer_index = self.tones_layout.count() - 1
        self.tones_layout.insertWidget(spacer_index, tone_control)
        self.tone_controls[tone_id] = tone_control
        
        # Agregar al motor de audio
        self.audio_engine.add_tone(tone_id, 440, 0.3)
        
        self.status_bar.showMessage(f"✅ Tono {tone_id} agregado - Total: {len(self.tone_controls)}")
    
    def _remove_tone(self, tone_id: int) -> None:
        """Elimina un control de tono"""
        if tone_id in self.tone_controls:
            control = self.tone_controls[tone_id]
            self.tones_layout.removeWidget(control)
            control.deleteLater()
            del self.tone_controls[tone_id]
            
            self.audio_engine.remove_tone(tone_id)
            self.status_bar.showMessage(f"🗑 Tono {tone_id} eliminado")
    
    def _on_tone_parameters_changed(self, tone_id: int, parameters: dict) -> None:
        """Maneja cambios en parámetros de tonos"""
        self.audio_engine.update_tone(
            tone_id,
            parameters['frequency'],
            parameters['volume'],
            parameters['wave_type'],
            parameters['panning']
        )
        
        self.audio_engine.set_tone_active(tone_id, parameters['active'])
    
    def _play_all_tones(self) -> None:
        """Reproduce todos los tonos"""
        for control in self.tone_controls.values():
            if not control.is_playing:
                control._toggle_play_pause()
    
    def _stop_all_tones(self) -> None:
        """Detiene todos los tonos"""
        for control in self.tone_controls.values():
            if control.is_playing:
                control._stop_tone()
    
    def _clear_all_tones(self) -> None:
        """Elimina todos los tonos"""
        tone_ids = list(self.tone_controls.keys())
        for tone_id in tone_ids:
            self._remove_tone(tone_id)
    
    def _on_audio_started(self) -> None:
        """Maneja el inicio del audio"""
        self.status_bar.showMessage("🔊 Sistema de audio iniciado")
    
    def _on_audio_stopped(self) -> None:
        """Maneja la detención del audio"""
        self.status_bar.showMessage("🔇 Sistema de audio detenido")
    
    def closeEvent(self, event) -> None:
        """Maneja el cierre de la aplicación"""
        self.audio_engine.stop_audio()
        event.accept()