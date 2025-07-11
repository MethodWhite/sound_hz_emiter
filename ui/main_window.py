"""
Ventana principal completamente mejorada - Todas las funcionalidades integradas
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QGroupBox, QScrollArea, QPushButton, QStatusBar, QSplitter)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

from .components.tone_control import ToneControl
from .components.timer_control import TimerControl
from .components.pomodoro_control import PomodoroControl
from .components.audio_controls import AudioControls
from .components.statistics_panel import StatisticsPanel
from .components.recording_control import RecordingControl
from .styles.theme_manager import ThemeManager
from .audio.audio_engine import AudioEngine
from .utils.constants import UIConstants, KeyboardShortcuts

class MainWindow(QMainWindow):
    """
    Ventana principal mejorada con todas las funcionalidades
    """
    
    def __init__(self):
        super().__init__()
        
        # Inicializar componentes principales
        self.audio_engine = AudioEngine()
        self.theme_manager = ThemeManager(self)
        
        # Contenedores de controles
        self.tone_controls = {}
        self.next_tone_id = 1
        
        # Timer para actualizaciones
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_statistics)
        self.update_timer.start(1000)  # Actualizar cada segundo
        
        # Configurar ventana
        self._setup_window()
        
        # Crear interfaz
        self._create_user_interface()
        
        # Conectar señales
        self._connect_signals()
        
        # Configurar atajos de teclado
        self._setup_keyboard_shortcuts()
        
        # Aplicar tema inicial
        self.theme_manager.apply_current_theme()
        
        # Agregar primer tono
        self._add_new_tone()
        
        # Iniciar sistema de audio
        self.audio_engine.start_audio()
    
    def _setup_window(self) -> None:
        """Configura las propiedades básicas de la ventana"""
        self.setWindowTitle("🔊 Sound Hz Emitter v2.0 - Clean Code Edition Pro")
        self.setGeometry(100, 100, UIConstants.WINDOW_WIDTH, UIConstants.WINDOW_HEIGHT)
        self.setMinimumSize(UIConstants.MIN_WINDOW_WIDTH, UIConstants.MIN_WINDOW_HEIGHT)
    
    def _create_user_interface(self) -> None:
        """Crea la interfaz de usuario principal mejorada"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(UIConstants.LAYOUT_MARGIN, UIConstants.LAYOUT_MARGIN,
                                     UIConstants.LAYOUT_MARGIN, UIConstants.LAYOUT_MARGIN)
        main_layout.setSpacing(UIConstants.LAYOUT_SPACING)
        
        # Crear splitter principal para redimensionamiento
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo (controles principales)
        self._create_main_controls_panel(main_splitter)
        
        # Panel derecho (estadísticas y grabación)
        self._create_info_and_stats_panel(main_splitter)
        
        # Configurar proporciones del splitter
        main_splitter.setSizes([int(UIConstants.WINDOW_WIDTH * 0.65), 
                               int(UIConstants.WINDOW_WIDTH * 0.35)])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        
        main_layout.addWidget(main_splitter)
        
        # Barra de estado mejorada
        self._create_enhanced_status_bar()
    
    def _create_main_controls_panel(self, parent_splitter: QSplitter) -> None:
        """Crea el panel principal de controles"""
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(UIConstants.LAYOUT_SPACING)
        
        # Controles de tiempo (Timer y Pomodoro) en splitter horizontal
        time_splitter = QSplitter(Qt.Horizontal)
        self._create_timer_controls(time_splitter)
        controls_layout.addWidget(time_splitter)
        
        # Controles de tonos
        self._create_tone_controls_section(controls_layout)
        
        # Controles globales
        self._create_global_controls(controls_layout)
        
        parent_splitter.addWidget(controls_widget)
    
    def _create_timer_controls(self, parent_splitter: QSplitter) -> None:
        """Crea los controles de temporizador y Pomodoro mejorados"""
        # Timer control mejorado
        self.timer_control = TimerControl()
        parent_splitter.addWidget(self.timer_control)
        
        # Pomodoro control mejorado
        self.pomodoro_control = PomodoroControl()
        parent_splitter.addWidget(self.pomodoro_control)
        
        # Configurar proporciones
        parent_splitter.setSizes([300, 300])
    
    def _create_tone_controls_section(self, parent_layout: QVBoxLayout) -> None:
        """Crea la sección de controles de tonos mejorada"""
        tones_group = QGroupBox("🎵 Control de Tonos Avanzado")
        tones_layout = QVBoxLayout(tones_group)
        
        # Botones superiores mejorados
        self._create_enhanced_tone_action_buttons(tones_layout)
        
        # Área de scroll para tonos mejorada
        self._create_enhanced_tones_scroll_area(tones_layout)
        
        parent_layout.addWidget(tones_group, 1)  # Expandible
    
    def _create_enhanced_tone_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Botones de acción para tonos mejorados"""
        buttons_layout = QHBoxLayout()
        
        # Botón agregar mejorado
        add_tone_button = QPushButton("➕ Agregar Nuevo Tono")
        add_tone_button.setFixedHeight(UIConstants.BUTTON_HEIGHT)
        add_tone_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_tone_button.clicked.connect(self._add_new_tone)
        buttons_layout.addWidget(add_tone_button)
        
        # Controles de grupo
        play_all_button = QPushButton("▶ Reproducir Todo")
        play_all_button.setFixedHeight(UIConstants.BUTTON_HEIGHT)
        play_all_button.clicked.connect(self._play_all_tones)
        buttons_layout.addWidget(play_all_button)
        
        stop_all_button = QPushButton("⏹ Detener Todo")
        stop_all_button.setFixedHeight(UIConstants.BUTTON_HEIGHT)
        stop_all_button.clicked.connect(self._stop_all_tones)
        buttons_layout.addWidget(stop_all_button)
        
        clear_all_button = QPushButton("🗑 Limpiar Todo")
        clear_all_button.setFixedHeight(UIConstants.BUTTON_HEIGHT)
        clear_all_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        clear_all_button.clicked.connect(self._clear_all_tones)
        buttons_layout.addWidget(clear_all_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def _create_enhanced_tones_scroll_area(self, parent_layout: QVBoxLayout) -> None:
        """Área de scroll mejorada para controles de tonos"""
        self.tones_scroll_area = QScrollArea()
        self.tones_scroll_area.setWidgetResizable(True)
        self.tones_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tones_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tones_scroll_area.setMinimumHeight(400)
        
        self.tones_container_widget = QWidget()
        self.tones_layout = QVBoxLayout(self.tones_container_widget)
        self.tones_layout.setSpacing(15)  # Más espaciado
        self.tones_layout.setContentsMargins(10, 10, 10, 10)
        self.tones_layout.addStretch()
        
        self.tones_scroll_area.setWidget(self.tones_container_widget)
        parent_layout.addWidget(self.tones_scroll_area, 1)
    
    def _create_global_controls(self, parent_layout: QVBoxLayout) -> None:
        """Crea los controles globales mejorados"""
        self.audio_controls = AudioControls(self.audio_engine, self.theme_manager)
        parent_layout.addWidget(self.audio_controls)
    
    def _create_info_and_stats_panel(self, parent_splitter: QSplitter) -> None:
        """Crea el panel de información y estadísticas"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(UIConstants.LAYOUT_SPACING)
        
        # Panel de estadísticas en tiempo real
        self.statistics_panel = StatisticsPanel()
        info_layout.addWidget(self.statistics_panel, 1)
        
        # Control de grabación
        self.recording_control = RecordingControl(self.audio_engine)
        info_layout.addWidget(self.recording_control)
        
        parent_splitter.addWidget(info_widget)
    
    def _create_enhanced_status_bar(self) -> None:
        """Crea barra de estado mejorada"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Información principal
        self.main_status_label = "🔊 Sound Hz Emitter v2.0 Pro - Sistema inicializado"
        
        # Información de tonos
        self.tones_status_label = "Tonos: 1 total, 0 activos"
        
        # Información de audio
        self.audio_status_label = "Audio: Activo"
        
        self._update_status_bar()
    
    def _update_status_bar(self) -> None:
        """Actualiza la barra de estado"""
        active_tones = sum(1 for control in self.tone_controls.values() if control.is_playing)
        total_tones = len(self.tone_controls)
        
        status_message = (f"{self.main_status_label} | "
                         f"Tonos: {total_tones} total, {active_tones} activos | "
                         f"{self.audio_status_label}")
        
        self.status_bar.showMessage(status_message)
    
    def _connect_signals(self) -> None:
        """Conecta todas las señales entre componentes"""
        # Señales del motor de audio
        self.audio_engine.audio_started.connect(self._on_audio_started)
        self.audio_engine.audio_stopped.connect(self._on_audio_stopped)
        self.audio_engine.audio_stats_updated.connect(self.statistics_panel.update_audio_stats)
        
        # Señales de controles globales
        self.audio_controls.clear_all_requested.connect(self._clear_all_tones)
        
        # Señales de timer
        self.timer_control.timer_started.connect(self.recording_control.on_timer_started)
        self.timer_control.timer_stopped.connect(self.recording_control.on_timer_stopped)
        self.timer_control.timer_tick.connect(self._on_timer_tick)
        
        # Señales de pomodoro
        self.pomodoro_control.pomodoro_tick.connect(self._on_pomodoro_tick)
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Configura atajos de teclado"""
        shortcuts = {
            'add_tone': self._add_new_tone,
            'play_all': self._play_all_tones,
            'stop_all': self._stop_all_tones,
            'clear_all': self._clear_all_tones,
            'toggle_theme': self.theme_manager.toggle_theme,
            'quit': self.close
        }
        
        for action, callback in shortcuts.items():
            shortcut_key = KeyboardShortcuts.get_shortcut(action)
            if shortcut_key:
                shortcut = QShortcut(QKeySequence(shortcut_key), self)
                shortcut.activated.connect(callback)
    
    def _add_new_tone(self) -> None:
        """Agrega un nuevo control de tono mejorado"""
        tone_id = self.next_tone_id
        self.next_tone_id += 1
        
        tone_control = ToneControl(tone_id)
        tone_control.tone_parameters_changed.connect(self._on_tone_parameters_changed)
        tone_control.tone_deletion_requested.connect(self._remove_tone)
        tone_control.tone_play_state_changed.connect(self._on_tone_play_state_changed)
        
        # Insertar antes del spacer
        spacer_index = self.tones_layout.count() - 1
        self.tones_layout.insertWidget(spacer_index, tone_control)
        self.tone_controls[tone_id] = tone_control
        
        # Agregar al motor de audio
        self.audio_engine.add_tone(tone_id, 440, 0.3)
        
        self._update_status_bar()
        self.main_status_label = f"✅ Tono {tone_id} agregado"
    
    def _remove_tone(self, tone_id: int) -> None:
        """Elimina un control de tono"""
        if tone_id in self.tone_controls:
            control = self.tone_controls[tone_id]
            self.tones_layout.removeWidget(control)
            control.deleteLater()
            del self.tone_controls[tone_id]
            
            self.audio_engine.remove_tone(tone_id)
            self._update_status_bar()
            self.main_status_label = f"🗑 Tono {tone_id} eliminado"
    
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
    
    def _on_tone_play_state_changed(self, tone_id: int, is_playing: bool) -> None:
        """Maneja cambios en estado de reproducción"""
        self._update_status_bar()
    
    def _play_all_tones(self) -> None:
        """Reproduce todos los tonos"""
        for control in self.tone_controls.values():
            if not control.is_playing and control.is_enabled():
                control._toggle_play_pause()
        
        self.main_status_label = "▶ Reproduciendo todos los tonos"
        self._update_status_bar()
    
    def _stop_all_tones(self) -> None:
        """Detiene todos los tonos"""
        for control in self.tone_controls.values():
            if control.is_playing:
                control._stop_tone()
        
        self.main_status_label = "⏹ Todos los tonos detenidos"
        self._update_status_bar()
    
    def _clear_all_tones(self) -> None:
        """Elimina todos los tonos"""
        tone_ids = list(self.tone_controls.keys())
        for tone_id in tone_ids:
            self._remove_tone(tone_id)
        
        self.main_status_label = "🗑 Todos los tonos eliminados"
        self._update_status_bar()
    
    def _on_audio_started(self) -> None:
        """Maneja el inicio del audio"""
        self.audio_status_label = "Audio: Activo"
        self._update_status_bar()
    
    def _on_audio_stopped(self) -> None:
        """Maneja la detención del audio"""
        self.audio_status_label = "Audio: Detenido"
        self._update_status_bar()
    
    def _on_timer_tick(self, time_remaining: str) -> None:
        """Maneja tick del timer para estadísticas"""
        stats = self.timer_control.get_time_statistics()
        self.statistics_panel.update_timer_stats(stats)
    
    def _on_pomodoro_tick(self, phase: str, time_remaining: str) -> None:
        """Maneja tick del pomodoro para estadísticas"""
        stats = self.pomodoro_control.get_pomodoro_statistics()
        self.statistics_panel.update_pomodoro_stats(stats)
    
    def _update_statistics(self) -> None:
        """Actualiza estadísticas periódicamente"""
        # Actualizar estadísticas de audio
        audio_stats = self.audio_engine.get_audio_statistics()
        self.statistics_panel.update_audio_stats(audio_stats)
        
        # Actualizar estadísticas de timer si no está en tick
        if hasattr(self.timer_control, 'get_time_statistics'):
            timer_stats = self.timer_control.get_time_statistics()
            self.statistics_panel.update_timer_stats(timer_stats)
        
        # Actualizar estadísticas de pomodoro si no está en tick
        if hasattr(self.pomodoro_control, 'get_pomodoro_statistics'):
            pomodoro_stats = self.pomodoro_control.get_pomodoro_statistics()
            self.statistics_panel.update_pomodoro_stats(pomodoro_stats)
    
    def closeEvent(self, event) -> None:
        """Maneja el cierre de la aplicación"""
        # Detener grabación si está activa
        if hasattr(self.recording_control, 'is_recording') and self.recording_control.is_recording:
            self.recording_control.stop_recording()
        
        # Detener sistema de audio
        self.audio_engine.stop_audio()
        
        # Detener timers
        self.update_timer.stop()
        
        # Aceptar evento de cierre
        event.accept()
