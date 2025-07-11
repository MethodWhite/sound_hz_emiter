"""Ventana principal mejorada con audio real, temas, controles individuales, panning estéreo, nuevos tipos de onda y Pomodoro integrado"""

import sys
import random
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QSlider, QComboBox, QCheckBox,
    QFrame, QGroupBox, QStatusBar, QMessageBox, QTextEdit,
    QScrollArea, QSizePolicy, QSpacerItem, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QPalette, QColor

# Imports condicionales para audio
try:
    import sounddevice as sd
    AUDIO_DISPONIBLE = True
except ImportError:
    AUDIO_DISPONIBLE = False

# Asegurar que numpy esté disponible para generación de ruidos
try:
    import numpy as np
    NUMPY_DISPONIBLE = True
except ImportError:
    NUMPY_DISPONIBLE = False
    print("Warning: NumPy no disponible - ruidos no funcionarán correctamente")

class AudioThread(QThread):
    """Hilo para generación de audio en tiempo real con panning estéreo"""
    
    def __init__(self, sample_rate=44100):
        super().__init__()
        self.sample_rate = sample_rate
        self.running = False
        self.tonos_activos = {}
        self.stream = None
        
    def add_tone(self, tone_id, frequency, volume, wave_type="sine", active=True, panning=0.0):
        """Añade o actualiza un tono con panning"""
        self.tonos_activos[tone_id] = {
            'frequency': frequency,
            'volume': volume,
            'wave_type': wave_type,
            'active': active,
            'panning': panning,  # -1.0 = izquierda, 0.0 = centro, 1.0 = derecha
            'phase': 0.0
        }
        
    def remove_tone(self, tone_id):
        """Elimina un tono"""
        if tone_id in self.tonos_activos:
            del self.tonos_activos[tone_id]

    def set_tone_active(self, tone_id, active):
        """Activa/desactiva un tono"""
        if tone_id in self.tonos_activos:
            self.tonos_activos[tone_id]['active'] = active
    
    def generate_wave(self, frequency, wave_type, frames, phase):
        """Genera una forma de onda incluyendo ruidos y pulsos"""
        t = np.arange(frames) / self.sample_rate
        t = t + phase
        
        if wave_type == "sine" or wave_type == "seno":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "square" or wave_type == "cuadrada":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "triangle" or wave_type == "triangular":
            wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
        elif wave_type == "sawtooth" or wave_type == "sierra":
            wave = 2 * (frequency * t - np.floor(frequency * t + 0.5))
        elif wave_type == "white_noise" or wave_type == "ruido blanco":
            # Ruido blanco: todas las frecuencias con igual intensidad
            if NUMPY_DISPONIBLE:
                wave = np.random.normal(0, 0.3, frames).astype(np.float32)
            else:
                # Fallback sin numpy
                wave = np.array([random.gauss(0, 0.3) for _ in range(frames)], dtype=np.float32)
        elif wave_type == "pink_noise" or wave_type == "ruido rosa":
            # Ruido rosa: potencia inversamente proporcional a la frecuencia
            if NUMPY_DISPONIBLE:
                white = np.random.normal(0, 1, frames)
                # Filtro simple para ruido rosa (aproximación)
                wave = np.zeros(frames)
                b = [0.02109238, 0.07113478, 0.68873558]  # Coeficientes de filtro rosa
                for i in range(len(b)):
                    if i < len(white):
                        wave[i:] += b[i] * white[:-i] if i > 0 else b[i] * white
                wave = wave * 0.3
            else:
                # Fallback simplificado
                wave = np.array([random.gauss(0, 0.2) * (0.5 + 0.5 * np.sin(2 * np.pi * i / frames)) for i in range(frames)], dtype=np.float32)
        elif wave_type == "brown_noise" or wave_type == "ruido marrón":
            # Ruido marrón: potencia inversamente proporcional al cuadrado de la frecuencia
            if NUMPY_DISPONIBLE:
                white = np.random.normal(0, 1, frames)
                # Integración del ruido blanco para obtener ruido marrón
                wave = np.cumsum(white) * 0.01
                wave = wave - np.mean(wave)  # Centrar en cero
                wave = wave * 0.2  # Normalizar
            else:
                # Fallback simplificado
                accumulated = 0
                wave_list = []
                for i in range(frames):
                    accumulated += random.gauss(0, 0.1)
                    wave_list.append(accumulated * 0.01)
                wave = np.array(wave_list, dtype=np.float32)
                wave = wave - np.mean(wave)  # Centrar en cero
        elif wave_type == "pulse" or wave_type == "pulsar":
            # Onda pulsar: modulación de amplitud sinusoidal
            pulse_freq = frequency * 0.1  # Frecuencia de pulsación (10% de la frecuencia base)
            carrier = np.sin(2 * np.pi * frequency * t)
            modulator = (np.sin(2 * np.pi * pulse_freq * t) + 1) / 2  # Modulador de 0 a 1
            wave = carrier * modulator
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        return wave, t[-1] if len(t) > 0 else 0
    
    def audio_callback(self, outdata, frames, time, status):
        """Callback para generación de audio con panning estéreo"""
        if status:
            print(f"Audio status: {status}")
        # Inicializar buffers estéreo
        buffer_left = np.zeros(frames, dtype=np.float32)
        buffer_right = np.zeros(frames, dtype=np.float32)
        
        # Generar y mezclar tonos activos
        for tone_id, tone_data in self.tonos_activos.items():
            if tone_data['active'] and tone_data['volume'] > 0:
                wave, new_phase = self.generate_wave(
                    tone_data['frequency'],
                    tone_data['wave_type'],
                    frames,
                    tone_data['phase']
                )
                # Aplicar volumen
                wave = wave * tone_data['volume']
                # Aplicar panning estéreo
                panning = tone_data['panning']  # -1.0 a 1.0
                # Calcular ganancia para cada canal
                left_gain = np.sqrt((1.0 - panning) / 2.0) if panning >= 0 else 1.0
                right_gain = np.sqrt((1.0 + panning) / 2.0) if panning <= 0 else 1.0
                # Mezclar con buffers
                buffer_left += wave * left_gain
                buffer_right += wave * right_gain
                # Actualizar fase
                tone_data['phase'] = new_phase
        
        # Normalizar para evitar clipping
        if len(self.tonos_activos) > 0:
            max_amplitude_left = np.max(np.abs(buffer_left)) if len(buffer_left) > 0 else 0
            max_amplitude_right = np.max(np.abs(buffer_right)) if len(buffer_right) > 0 else 0
            max_amplitude = max(max_amplitude_left, max_amplitude_right)
            if max_amplitude > 0.8:
                buffer_left = buffer_left * 0.8 / max_amplitude
                buffer_right = buffer_right * 0.8 / max_amplitude
        
        # Copiar a salida estéreo
        outdata[:, 0] = buffer_left
        outdata[:, 1] = buffer_right
    
    def start_audio(self):
        """Inicia el stream de audio"""
        if not AUDIO_DISPONIBLE:
            print("Audio no disponible - sounddevice no instalado")
            return False
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,
                callback=self.audio_callback,
                blocksize=1024
            )
            self.stream.start()
            self.running = True
            print("Audio iniciado correctamente")
            return True
        except Exception as e:
            print(f"Error iniciando audio: {e}")
            return False
    
    def stop_audio(self):
        """Detiene el stream de audio"""
        self.running = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("Audio detenido")

class MotorAudioReal:
    """Motor de audio real usando sounddevice con panning"""
    
    def __init__(self):
        self.audio_thread = AudioThread()
        self.reproduciendo = False
        
    def iniciar(self):
        """Inicia el motor de audio"""
        if AUDIO_DISPONIBLE:
            success = self.audio_thread.start_audio()
            if success:
                self.reproduciendo = True
                return True
            else:
                print("Fallback a modo simulación")
                self.reproduciendo = True
                return True
        else:
            print("Audio iniciado (modo simulación)")
            self.reproduciendo = True
            return True

    def detener(self):
        """Detiene el motor de audio"""
        if AUDIO_DISPONIBLE:
            self.audio_thread.stop_audio()
        self.reproduciendo = False
        print("Audio detenido")
        
    def agregar_tono(self, id_tono, frecuencia, volumen, tipo_onda="seno", panning=0.0):
        """Agrega un tono con panning"""
        if AUDIO_DISPONIBLE:
            self.audio_thread.add_tone(id_tono, frecuencia, volumen, tipo_onda, True, panning)
        print(f"Tono {id_tono} agregado: {frecuencia} Hz, Panning: {panning}")
        
    def eliminar_tono(self, id_tono):
        """Elimina un tono"""
        if AUDIO_DISPONIBLE:
            self.audio_thread.remove_tone(id_tono)
        print(f"Tono {id_tono} eliminado")
        
    def actualizar_tono(self, id_tono, **parametros):
        """Actualiza un tono"""
        if AUDIO_DISPONIBLE and id_tono in self.audio_thread.tonos_activos:
            tone_data = self.audio_thread.tonos_activos[id_tono]
            if 'frecuencia' in parametros:
                tone_data['frequency'] = parametros['frecuencia']
            if 'volumen' in parametros:
                tone_data['volume'] = parametros['volumen']
            if 'tipo_onda' in parametros:
                tone_data['wave_type'] = parametros['tipo_onda']
            if 'activo' in parametros:
                tone_data['active'] = parametros['activo']
            if 'panning' in parametros:
                tone_data['panning'] = parametros['panning']
        
    def set_tono_activo(self, id_tono, activo):
        """Activa/desactiva un tono"""
        if AUDIO_DISPONIBLE:
            self.audio_thread.set_tone_active(id_tono, activo)

class ThemeManager:
    """Gestor de temas claro y oscuro - MEJORADO CON ESTILOS CONSISTENTES"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.is_dark = False
        
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        self.is_dark = not self.is_dark
        self.apply_theme()
        
        # Actualizar información del panel
        if hasattr(self.main_window, 'crear_panel_informacion'):
            try:
                # Refrescar el contenido informativo
                theme_text = "🌙 Oscuro" if self.is_dark else "☀ Claro"
                self.main_window.barra_estado.showMessage(f"🎨 Tema cambiado a: {theme_text}")
            except:
                pass
        
    def apply_theme(self):
        """Aplica el tema actual"""
        if self.is_dark:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_light_theme(self):
        """Aplica tema claro"""
        self.main_window.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
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
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
            }
            QScrollArea {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
                border: 1px solid #cccccc;
            }
            QScrollBar::handle:vertical {
                background-color: #0078d4;
                border-radius: 6px;
                min-height: 20px;
                border: 1px solid #106ebe;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #106ebe;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: #f8f9fa;
            }
            QWidget#widget_contenedor_tonos {
                background-color: white;
                border: none;
            }
            QScrollArea#scroll_area_tonos {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        
    def apply_dark_theme(self):
        """Aplica tema oscuro - MEJORADO CON ESTILOS CONSISTENTES PARA CONTROLES DE TONOS"""
        self.main_window.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #3c3c3c;
                color: #ffffff;
            }
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
            QFrame {
                border: 1px solid #555555;
                border-radius: 8px;
                background-color: #404040;
            }
            QScrollArea {
                border: 1px solid #555555;
                border-radius: 5px;
                background-color: #3c3c3c;
            }
            QScrollBar:vertical {
                background-color: #505050;
                width: 12px;
                border-radius: 6px;
                border: 1px solid #666666;
            }
            QScrollBar::handle:vertical {
                background-color: #64b5f6;
                border-radius: 6px;
                min-height: 20px;
                border: 1px solid #42a5f5;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #42a5f5;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: #404040;
            }
            QStatusBar {
                background-color: #404040;
                border-top: 1px solid #555555;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #404040;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QSpinBox {
                background-color: #404040;
                border: 1px solid #555555;
                color: #ffffff;
                border-radius: 4px;
                padding: 2px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #555555;
                border: 1px solid #666666;
            }
            QSlider {
                background: transparent;
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
                background: #42a5f5;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #555555;
                color: #ffffff;
                border-radius: 4px;
                padding: 2px;
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
            QCheckBox {
                color: #ffffff;
                background-color: transparent;
            }
            QCheckBox::indicator {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border: 1px solid #28a745;
            }
            QFrame#temporizador_frame {
                background-color: #404040;
                border: 2px solid #6f42c1;
                border-radius: 10px;
            }
            QLabel#temporizador_display {
                background-color: #2b2b2b;
                border: 3px solid #6f42c1;
                color: #6f42c1;
            }
            QLabel#temporizador_titulo {
                color: #6f42c1;
                background-color: transparent;
            }
            QLabel#estadisticas_label {
                background-color: #404040;
                color: #64b5f6;
                border-left: 4px solid #64b5f6;
                border-radius: 8px;
            }
            QFrame[styleClass="control_tono"] {
                border: 2px solid #555555;
                border-radius: 12px;
                background-color: #404040;
                margin: 3px;
            }
            QWidget#widget_contenedor_tonos {
                background-color: #3c3c3c;
                border: none;
            }
            QScrollArea#scroll_area_tonos {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 8px;
            }
        """)

class ControlTonoMejorado(QFrame):
    """Widget mejorado para controlar un tono individual con panning estéreo - CORRECCIONES APLICADAS"""
    
    tono_modificado = Signal(int, dict)
    tono_eliminado = Signal(int)
    
    def __init__(self, id_tono, frecuencia_inicial=440):
        super().__init__()
        self.id_tono = id_tono
        self.esta_reproduciendo = False
        self.detenido_por_temporizador = False  # NUEVO: Flag para rastrear detención por temporizador
        self.configurar_interfaz(frecuencia_inicial)
        
    def configurar_interfaz(self, frecuencia_inicial):
        """Configura la interfaz mejorada del control de tono"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Cabecera con titulo y controles
        cabecera = QHBoxLayout()
        
        # Título
        titulo = QLabel(f"♪ Tono {self.id_tono}")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d4;")
        cabecera.addWidget(titulo)
        
        # Espaciador
        cabecera.addStretch()
        
        # Controles de reproducción mejorados
        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setFixedSize(35, 35)
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 17px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        cabecera.addWidget(self.btn_play_pause)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(35, 35)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 17px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_tone)
        cabecera.addWidget(self.btn_stop)
        
        # Botón eliminar
        btn_eliminar = QPushButton("✕")
        btn_eliminar.setFixedSize(35, 35)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 17px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.tono_eliminado.emit(self.id_tono))
        cabecera.addWidget(btn_eliminar)
        
        layout.addLayout(cabecera)
        
        # Grid de controles mejorado
        grid_controles = QGridLayout()
        grid_controles.setSpacing(10)
        
        # Frecuencia
        freq_label = QLabel("Frecuencia (Hz)")
        freq_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid_controles.addWidget(freq_label, 0, 0)
        
        self.spin_frecuencia = QSpinBox()
        self.spin_frecuencia.setRange(20, 20000)
        self.spin_frecuencia.setValue(frecuencia_inicial)
        self.spin_frecuencia.setSuffix(" Hz")
        self.spin_frecuencia.setFixedWidth(120)
        self.spin_frecuencia.valueChanged.connect(self.emitir_cambios)
        grid_controles.addWidget(self.spin_frecuencia, 1, 0)
        
        # Volumen
        vol_label = QLabel("Volumen (%)")
        vol_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid_controles.addWidget(vol_label, 0, 1)
        
        # Contenedor de volumen con sliders visibles
        vol_container = QVBoxLayout()
        vol_container.setSpacing(5)
        
        self.slider_volumen = QSlider(Qt.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(30)
        self.slider_volumen.setMinimumWidth(120)
        self.slider_volumen.setMinimumHeight(20)
        self.slider_volumen.valueChanged.connect(self.emitir_cambios)
        vol_container.addWidget(self.slider_volumen)
        
        self.etiqueta_volumen = QLabel("30%")
        self.etiqueta_volumen.setAlignment(Qt.AlignCenter)
        self.etiqueta_volumen.setStyleSheet("font-size: 10px; font-weight: bold;")
        vol_container.addWidget(self.etiqueta_volumen)
        
        vol_widget = QWidget()
        vol_widget.setLayout(vol_container)
        vol_widget.setMinimumWidth(140)
        grid_controles.addWidget(vol_widget, 1, 1)
        
        # Panning Estéreo
        pan_label = QLabel("Panning L/R")
        pan_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid_controles.addWidget(pan_label, 2, 0)
        
        # Contenedor de panning con sliders visibles
        pan_container = QVBoxLayout()
        pan_container.setSpacing(5)
        
        self.slider_panning = QSlider(Qt.Horizontal)
        self.slider_panning.setRange(-100, 100)
        self.slider_panning.setValue(0)
        self.slider_panning.setMinimumWidth(120)
        self.slider_panning.setMinimumHeight(20)
        self.slider_panning.valueChanged.connect(self.emitir_cambios)
        pan_container.addWidget(self.slider_panning)
        
        self.etiqueta_panning = QLabel("Centro")
        self.etiqueta_panning.setAlignment(Qt.AlignCenter)
        self.etiqueta_panning.setStyleSheet("font-size: 10px; font-weight: bold;")
        pan_container.addWidget(self.etiqueta_panning)
        
        pan_widget = QWidget()
        pan_widget.setLayout(pan_container)
        pan_widget.setMinimumWidth(140)
        grid_controles.addWidget(pan_widget, 2, 1)
        
        # Tipo de onda
        onda_label = QLabel("Tipo de Onda")
        onda_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid_controles.addWidget(onda_label, 0, 2)
        
        self.combo_onda = QComboBox()
        self.combo_onda.addItems(["Seno", "Cuadrada", "Triangular", "Sierra", "Ruido Blanco", "Ruido Rosa", "Ruido Marrón", "Pulsar"])
        self.combo_onda.setFixedWidth(120)
        self.combo_onda.currentTextChanged.connect(self.emitir_cambios)
        grid_controles.addWidget(self.combo_onda, 1, 2)
        
        # Estado
        estado_label = QLabel("Estado")
        estado_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        grid_controles.addWidget(estado_label, 2, 2)
        
        self.etiqueta_estado = QLabel("⏸ Pausado")
        self.etiqueta_estado.setStyleSheet("font-size: 11px; color: #666;")
        grid_controles.addWidget(self.etiqueta_estado, 3, 2)
        
        layout.addLayout(grid_controles)
        
        # Checkbox master
        self.check_activo = QCheckBox("🔊 Tono Habilitado")
        self.check_activo.setChecked(True)
        self.check_activo.setStyleSheet("font-weight: bold; color: #28a745; font-size: 12px;")
        self.check_activo.toggled.connect(self.emitir_cambios)
        layout.addWidget(self.check_activo)
        
        # CORRECCIÓN: Agregar identificador de clase para estilos consistentes
        self.setProperty("styleClass", "control_tono")
        
        # Estilo del frame mejorado
        self.setFrameStyle(QFrame.Box)
        self.setFixedHeight(240)
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background-color: #fafafa;
                margin: 3px;
            }
            QSlider {
                background: transparent;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0078d4, stop:1 #106ebe);
            }
            QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 2px;
                background-color: white;
                color: black;
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 2px;
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
                background-color: transparent;
            }
        """)
        
    def toggle_play_pause(self):
        """Alterna entre play y pause para este tono"""
        self.esta_reproduciendo = not self.esta_reproduciendo
        self.detenido_por_temporizador = False  # CORRECCIÓN: Resetear flag al usar control manual
        
        if self.esta_reproduciendo:
            self.btn_play_pause.setText("⏸")
            self.btn_play_pause.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
            """)
            self.etiqueta_estado.setText("▶ Reproduciendo")
            self.etiqueta_estado.setStyleSheet("font-size: 11px; color: #28a745; font-weight: bold;")
            # Activar el tono
            self.check_activo.setChecked(True)
            # Asegurar que el motor de audio esté activo
            self.asegurar_motor_audio_activo()
        else:
            self.btn_play_pause.setText("▶")
            self.btn_play_pause.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.etiqueta_estado.setText("⏸ Pausado")
            self.etiqueta_estado.setStyleSheet("font-size: 11px; color: #ffc107; font-weight: bold;")
        self.emitir_cambios()
        
    def asegurar_motor_audio_activo(self):
        """Asegura que el motor de audio esté activo cuando sea necesario"""
        if hasattr(self, 'ventana_principal') and self.ventana_principal:
            if not self.ventana_principal.motor_audio.reproduciendo:
                self.ventana_principal.iniciar_audio_global()
        else:
            # Fallback: buscar en parent hierarchy
            parent = self.parent()
            while parent and not hasattr(parent, 'motor_audio'):
                parent = parent.parent()
            if parent and hasattr(parent, 'motor_audio'):
                if not parent.motor_audio.reproduciendo:
                    parent.iniciar_audio_global()

    def pausar_si_reproduciendose(self):
        """NUEVO: Pausa el tono si está reproduciéndose (para pausa de temporizador)"""
        if self.esta_reproduciendo and self.check_activo.isChecked():
            print(f"DEBUG: Pausando tono {self.id_tono} por pausa de temporizador")
            self.stop_tone(desde_pausa_temporizador=True)
            return True
        return False
        
    def reactivar_si_habilitado(self):
        """CORRECCIÓN DEFINITIVA: Reactiva el tono si está habilitado, sin importar cómo fue detenido"""
        # CAMBIO CRÍTICO: Solo verificar el checkbox, ignorar estado anterior
        if self.check_activo.isChecked() and not self.esta_reproduciendo:
            print(f"DEBUG: Reactivando tono {self.id_tono} - Checkbox habilitado: {self.check_activo.isChecked()}")
            self.esta_reproduciendo = True
            self.detenido_por_temporizador = False
            # CORRECCIÓN: Actualizar interfaz visual COMPLETA
            self.btn_play_pause.setText("⏸")
            self.btn_play_pause.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
            """)
            self.etiqueta_estado.setText("▶ Reproduciendo")
            self.etiqueta_estado.setStyleSheet("font-size: 11px; color: #28a745; font-weight: bold;")
            # IMPORTANTE: Forzar actualización visual
            self.btn_play_pause.update()
            self.etiqueta_estado.update()
            # Emitir cambios para actualizar motor de audio
            self.emitir_cambios()
            self.asegurar_motor_audio_activo()
            print(f"DEBUG: Tono {self.id_tono} reactivado exitosamente")
            return True
        else:
            print(f"DEBUG: No se puede reactivar tono {self.id_tono} - Checkbox: {self.check_activo.isChecked()}, Reproduciendo: {self.esta_reproduciendo}")
        return False
        
    def reanudar_si_estaba_pausado_por_temporizador(self):
        """NUEVO: Reanuda el tono si estaba pausado por temporizador"""
        if not self.esta_reproduciendo and self.check_activo.isChecked():
            print(f"DEBUG: Reanudando tono {self.id_tono} después de pausa de temporizador")
            self.esta_reproduciendo = True
            # Actualizar interfaz visual
            self.btn_play_pause.setText("⏸")
            self.btn_play_pause.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    border-radius: 17px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
            """)
            self.etiqueta_estado.setText("▶ Reproduciendo")
            self.etiqueta_estado.setStyleSheet("font-size: 11px; color: #28a745; font-weight: bold;")
            # Emitir cambios para actualizar motor de audio
            self.emitir_cambios()
            self.asegurar_motor_audio_activo()
            return True
        return False
        
    def stop_tone(self, desde_temporizador=False, desde_pausa_temporizador=False):
        """CORRECCIÓN RADICAL: Stop que preserva checkbox para permitir reactivación"""
        self.esta_reproduciendo = False
        
        if desde_temporizador:
            self.detenido_por_temporizador = True
        elif desde_pausa_temporizador:
            self.detenido_por_temporizador = False
        else:
            self.detenido_por_temporizador = False

        self.btn_play_pause.setText("▶")
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 17px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        if desde_pausa_temporizador:
            self.etiqueta_estado.setText("⏸ Pausado por temporizador")
            self.etiqueta_estado.setStyleSheet("font-size: 11px; color: #ffc107; font-weight: bold;")
        else:
            self.etiqueta_estado.setText("⏹ Detenido")
            self.etiqueta_estado.setStyleSheet("font-size: 11px; color: #dc3545; font-weight: bold;")
        
        # CAMBIO CRÍTICO: NUNCA desactivar el checkbox automáticamente
        # El usuario debe controlar manualmente el checkbox
        
        # Emitir cambios para asegurar sincronización con motor de audio
        self.emitir_cambios()
        
        # Notificar a la ventana principal para verificar auto-detención
        if hasattr(self, 'ventana_principal') and self.ventana_principal:
            QTimer.singleShot(100, self.ventana_principal.verificar_y_gestionar_audio_global)
        
    def emitir_cambios(self):
        """Emite los cambios realizados en el control"""
        volumen_porcentaje = self.slider_volumen.value()
        panning_valor = self.slider_panning.value()
        
        # Actualizar etiquetas
        self.etiqueta_volumen.setText(f"{volumen_porcentaje}%")
        
        if panning_valor < -20:
            self.etiqueta_panning.setText("◄ Izq")
        elif panning_valor > 20:
            self.etiqueta_panning.setText("Der ►")
        else:
            self.etiqueta_panning.setText("Centro")
        
        configuracion = {
            'frecuencia': self.spin_frecuencia.value(),
            'volumen': volumen_porcentaje / 100.0,
            'panning': panning_valor / 100.0,  # Convertir a rango -1.0 a 1.0
            'tipo_onda': self.combo_onda.currentText().lower(),
            'activo': self.check_activo.isChecked() and self.esta_reproduciendo
        }
        
        # Solo emitir cambios, no iniciar audio automáticamente aquí
        self.tono_modificado.emit(self.id_tono, configuracion)

class ControlPomodoro(QFrame):
    """Widget del Pomodoro personalizable con mejores prácticas"""
    
    pomodoro_iniciado = Signal()
    pomodoro_pausado = Signal()
    pomodoro_finalizado = Signal()
    ciclo_completado = Signal(str)  # "trabajo" o "descanso"
    
    def __init__(self):
        super().__init__()
        self.timer_qt = QTimer()
        self.timer_qt.timeout.connect(self.actualizar_display)
        self.tiempo_restante_segundos = 0
        self.tiempo_total_segundos = 0
        self.en_descanso = False
        self.ciclos_completados = 0
        self.sesiones_trabajo_completadas = 0
        
        # CORRECCIÓN: Configuraciones predefinidas ANTES de configurar interfaz
        self.configuraciones = {
            "Estudio/Trabajo (25/5)": {"trabajo": 25, "descanso_corto": 5, "descanso_largo": 15, "ciclos_largo": 4},
            "Inmersión Profunda (50/10)": {"trabajo": 50, "descanso_corto": 10, "descanso_largo": 30, "ciclos_largo": 3},
            "Clásico": {"trabajo": 25, "descanso_corto": 5, "descanso_largo": 15, "ciclos_largo": 4},
            "Trabajo Creativo": {"trabajo": 90, "descanso_corto": 20, "descanso_largo": 60, "ciclos_largo": 2},
            "Concentración Ultra": {"trabajo": 120, "descanso_corto": 30, "descanso_largo": 90, "ciclos_largo": 2},
            "Sesiones Cortas": {"trabajo": 15, "descanso_corto": 3, "descanso_largo": 10, "ciclos_largo": 6},
            "Personalizado": {"trabajo": 25, "descanso_corto": 5, "descanso_largo": 15, "ciclos_largo": 4}
        }
        
        self.configuracion_actual = self.configuraciones["Clásico"].copy()
        
        # Ahora sí configurar la interfaz
        self.configurar_interfaz()
        
    def configurar_interfaz(self):
        """Configura la interfaz del Pomodoro"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        titulo = QLabel("🍅 Técnica Pomodoro")
        titulo.setObjectName("pomodoro_titulo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #d63031;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(titulo)
        
        # Selector de configuración
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Modo:"))
        self.combo_config = QComboBox()
        self.combo_config.addItems(list(self.configuraciones.keys()))
        self.combo_config.currentTextChanged.connect(self.cambiar_configuracion)
        config_layout.addWidget(self.combo_config)
        layout.addLayout(config_layout)
        
        # Configuración personalizable
        self.grupo_personalizado = QGroupBox("⚙ Configuración")
        self.grupo_personalizado.setVisible(False)
        layout_personalizado = QGridLayout(self.grupo_personalizado)
        
        # Trabajo
        layout_personalizado.addWidget(QLabel("Trabajo (min):"), 0, 0)
        self.spin_trabajo = QSpinBox()
        self.spin_trabajo.setRange(1, 180)
        self.spin_trabajo.setValue(25)
        self.spin_trabajo.valueChanged.connect(self.actualizar_configuracion_personalizada)
        layout_personalizado.addWidget(self.spin_trabajo, 0, 1)
        
        # Descanso corto
        layout_personalizado.addWidget(QLabel("Descanso corto (min):"), 0, 2)
        self.spin_descanso_corto = QSpinBox()
        self.spin_descanso_corto.setRange(1, 60)
        self.spin_descanso_corto.setValue(5)
        self.spin_descanso_corto.valueChanged.connect(self.actualizar_configuracion_personalizada)
        layout_personalizado.addWidget(self.spin_descanso_corto, 0, 3)
        
        # Descanso largo
        layout_personalizado.addWidget(QLabel("Descanso largo (min):"), 1, 0)
        self.spin_descanso_largo = QSpinBox()
        self.spin_descanso_largo.setRange(1, 120)
        self.spin_descanso_largo.setValue(15)
        self.spin_descanso_largo.valueChanged.connect(self.actualizar_configuracion_personalizada)
        layout_personalizado.addWidget(self.spin_descanso_largo, 1, 1)
        
        # Ciclos hasta descanso largo
        layout_personalizado.addWidget(QLabel("Ciclos para descanso largo:"), 1, 2)
        self.spin_ciclos_largo = QSpinBox()
        self.spin_ciclos_largo.setRange(1, 10)
        self.spin_ciclos_largo.setValue(4)
        self.spin_ciclos_largo.valueChanged.connect(self.actualizar_configuracion_personalizada)
        layout_personalizado.addWidget(self.spin_ciclos_largo, 1, 3)
        
        layout.addWidget(self.grupo_personalizado)
        
        # Display del tiempo
        self.display_tiempo = QLabel("25:00")
        self.display_tiempo.setObjectName("pomodoro_display")
        self.display_tiempo.setAlignment(Qt.AlignCenter)
        self.display_tiempo.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', 'Monaco', monospace;
                font-size: 36px;
                font-weight: bold;
                color: #d63031;
                background-color: #f8f9fa;
                border: 3px solid #d63031;
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0;
            }
        """)
        layout.addWidget(self.display_tiempo)
        
        # Indicador de fase
        self.indicador_fase = QLabel("🍅 Listo para trabajar")
        self.indicador_fase.setAlignment(Qt.AlignCenter)
        self.indicador_fase.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #d63031;
                background-color: #fff5f5;
                border: 1px solid #d63031;
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0;
            }
        """)
        layout.addWidget(self.indicador_fase)
        
        # Botones de control
        botones = QHBoxLayout()
        self.btn_iniciar = QPushButton("▶ Iniciar")
        self.btn_iniciar.setFixedHeight(45)
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #d63031;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.btn_iniciar.clicked.connect(self.iniciar_pomodoro)
        botones.addWidget(self.btn_iniciar)
        
        self.btn_detener = QPushButton("⏹ Detener")
        self.btn_detener.setEnabled(False)
        self.btn_detener.setFixedHeight(45)
        self.btn_detener.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.btn_detener.clicked.connect(self.detener_pomodoro)
        botones.addWidget(self.btn_detener)
        
        self.btn_saltar = QPushButton("⏭ Saltar")
        self.btn_saltar.setEnabled(False)
        self.btn_saltar.setFixedHeight(45)
        self.btn_saltar.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e55100;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.btn_saltar.clicked.connect(self.saltar_fase)
        botones.addWidget(self.btn_saltar)
        
        layout.addLayout(botones)
        
        # Estadísticas
        self.etiqueta_stats = QLabel("📊 Ciclos: 0 | Sesiones: 0")
        self.etiqueta_stats.setAlignment(Qt.AlignCenter)
        self.etiqueta_stats.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-style: italic;
                font-size: 11px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px;
                margin: 5px 0;
            }
        """)
        layout.addWidget(self.etiqueta_stats)
        
        self.setFrameStyle(QFrame.Box)
        self.setObjectName("pomodoro_frame")
        
    def cambiar_configuracion(self, nombre_config):
        """Cambia la configuración del Pomodoro"""
        if nombre_config == "Personalizado":
            self.grupo_personalizado.setVisible(True)
            self.configuracion_actual = self.configuraciones[nombre_config].copy()
            self.actualizar_configuracion_personalizada()
        else:
            self.grupo_personalizado.setVisible(False)
            self.configuracion_actual = self.configuraciones[nombre_config].copy()
            self.actualizar_display_configuracion()

    def actualizar_configuracion_personalizada(self):
        """Actualiza la configuración personalizada"""
        self.configuracion_actual["trabajo"] = self.spin_trabajo.value()
        self.configuracion_actual["descanso_corto"] = self.spin_descanso_corto.value()
        self.configuracion_actual["descanso_largo"] = self.spin_descanso_largo.value()
        self.configuracion_actual["ciclos_largo"] = self.spin_ciclos_largo.value()
        self.actualizar_display_configuracion()
        
    def actualizar_display_configuracion(self):
        """Actualiza el display según la configuración"""
        if not self.timer_qt.isActive():
            tiempo_trabajo = self.configuracion_actual["trabajo"]
            minutos = tiempo_trabajo
            self.display_tiempo.setText(f"{minutos:02d}:00")

    def iniciar_pomodoro(self):
        """Inicia un ciclo Pomodoro"""
        if not self.timer_qt.isActive():
            # Iniciar nueva sesión de trabajo
            self.en_descanso = False
            tiempo_minutos = self.configuracion_actual["trabajo"]
            self.indicador_fase.setText("🍅 Trabajando - ¡Concéntrate!")
            self.indicador_fase.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #d63031;
                    background-color: #fff5f5;
                    border: 2px solid #d63031;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 5px 0;
                }
            """)
        else:
            # Reanudar
            self.timer_qt.start(1000)
            self.btn_iniciar.setText("⏸ Pausar")
            self.btn_iniciar.clicked.disconnect()
            self.btn_iniciar.clicked.connect(self.pausar_pomodoro)
            return

        self.tiempo_total_segundos = tiempo_minutos * 60
        self.tiempo_restante_segundos = tiempo_minutos * 60
        self.timer_qt.start(1000)
        
        self.btn_iniciar.setText("⏸ Pausar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.pausar_pomodoro)
        self.btn_detener.setEnabled(True)
        self.btn_saltar.setEnabled(True)
        self.combo_config.setEnabled(False)
        
        self.pomodoro_iniciado.emit()
        
    def pausar_pomodoro(self):
        """Pausa el Pomodoro"""
        self.timer_qt.stop()
        self.btn_iniciar.setText("▶ Continuar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.iniciar_pomodoro)
        self.pomodoro_pausado.emit()
        
    def detener_pomodoro(self):
        """Detiene completamente el Pomodoro"""
        self.timer_qt.stop()
        self.btn_iniciar.setText("▶ Iniciar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.iniciar_pomodoro)
        self.btn_detener.setEnabled(False)
        self.btn_saltar.setEnabled(False)
        self.combo_config.setEnabled(True)
        
        self.en_descanso = False
        self.indicador_fase.setText("🍅 Listo para trabajar")
        self.indicador_fase.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #d63031;
                background-color: #fff5f5;
                border: 1px solid #d63031;
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0;
            }
        """)
        
        self.actualizar_display_configuracion()
        self.pomodoro_finalizado.emit()
        
    def saltar_fase(self):
        """Salta a la siguiente fase"""
        self.tiempo_restante_segundos = 0
        self.actualizar_display()
        
    def actualizar_display(self):
        """Actualiza el display del tiempo restante"""
        self.tiempo_restante_segundos -= 1
        
        if self.tiempo_restante_segundos <= 0:
            self.completar_fase()
            return

        minutos = self.tiempo_restante_segundos // 60
        segundos = self.tiempo_restante_segundos % 60
        self.display_tiempo.setText(f"{minutos:02d}:{segundos:02d}")
        
    def completar_fase(self):
        """Completa la fase actual y decide la siguiente"""
        if not self.en_descanso:
            # Terminó trabajo, ir a descanso
            self.ciclos_completados += 1
            self.sesiones_trabajo_completadas += 1
            self.ciclo_completado.emit("trabajo")

            # Determinar tipo de descanso
            if self.ciclos_completados % self.configuracion_actual["ciclos_largo"] == 0:
                # Descanso largo
                tiempo_descanso = self.configuracion_actual["descanso_largo"]
                self.indicador_fase.setText("☕ Descanso Largo - ¡Relájate!")
                self.indicador_fase.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        font-weight: bold;
                        color: #28a745;
                        background-color: #f5fff5;
                        border: 2px solid #28a745;
                        border-radius: 8px;
                        padding: 8px;
                        margin: 5px 0;
                    }
                """)
            else:
                # Descanso corto
                tiempo_descanso = self.configuracion_actual["descanso_corto"]
                self.indicador_fase.setText("🌱 Descanso Corto - Respira")
                self.indicador_fase.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        font-weight: bold;
                        color: #17a2b8;
                        background-color: #f5fcff;
                        border: 2px solid #17a2b8;
                        border-radius: 8px;
                        padding: 8px;
                        margin: 5px 0;
                    }
                """)

            self.en_descanso = True
            self.tiempo_total_segundos = tiempo_descanso * 60
            self.tiempo_restante_segundos = tiempo_descanso * 60
            self.timer_qt.start(1000)
        else:
            # Terminó descanso, volver a trabajo
            self.ciclo_completado.emit("descanso")
            self.en_descanso = False

            # Preparar siguiente sesión de trabajo
            tiempo_trabajo = self.configuracion_actual["trabajo"]
            self.tiempo_total_segundos = tiempo_trabajo * 60
            self.tiempo_restante_segundos = tiempo_trabajo * 60
            self.indicador_fase.setText("🍅 Trabajando - ¡Concéntrate!")
            self.indicador_fase.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #d63031;
                    background-color: #fff5f5;
                    border: 2px solid #d63031;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 5px 0;
                }
            """)
            self.timer_qt.start(1000)

        # Actualizar estadísticas
        self.etiqueta_stats.setText(f"📊 Ciclos: {self.ciclos_completados} | Sesiones: {self.sesiones_trabajo_completadas}")

class ControlTemporizador(QFrame):
    """Widget del temporizador - CORRECCIÓN: Sin mensaje de alerta"""
    
    temporizador_iniciado = Signal()
    temporizador_detenido = Signal()
    temporizador_finalizado = Signal()
    temporizador_pausado = Signal()  # NUEVO: Señal para pausa
    temporizador_reanudado = Signal()  # NUEVO: Señal para reanudación
    
    def __init__(self):
        super().__init__()
        self.timer_qt = QTimer()
        self.timer_qt.timeout.connect(self.actualizar_display)
        self.tiempo_restante_segundos = 0
        self.tiempo_total_segundos = 0
        self.configurar_interfaz()
        
    def configurar_interfaz(self):
        """Configura la interfaz del temporizador"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        titulo = QLabel("⏱ Temporizador de Sesión")
        titulo.setObjectName("temporizador_titulo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #6f42c1;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(titulo)
        
        config_tiempo = QHBoxLayout()
        config_tiempo.addWidget(QLabel("Min:"))
        self.spin_minutos = QSpinBox()
        self.spin_minutos.setRange(0, 999)
        self.spin_minutos.setValue(5)
        self.spin_minutos.setFixedWidth(70)
        # Conectar cambios para actualización automática
        self.spin_minutos.valueChanged.connect(self.actualizar_display_configuracion)
        config_tiempo.addWidget(self.spin_minutos)
        
        config_tiempo.addWidget(QLabel("Seg:"))
        self.spin_segundos = QSpinBox()
        self.spin_segundos.setRange(0, 59)
        self.spin_segundos.setValue(0)
        self.spin_segundos.setFixedWidth(70)
        # Conectar cambios para actualización automática
        self.spin_segundos.valueChanged.connect(self.actualizar_display_configuracion)
        config_tiempo.addWidget(self.spin_segundos)
        layout.addLayout(config_tiempo)
        
        self.display_tiempo = QLabel("05:00")
        self.display_tiempo.setObjectName("temporizador_display")
        self.display_tiempo.setAlignment(Qt.AlignCenter)
        self.display_tiempo.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', 'Monaco', monospace;
                font-size: 36px;
                font-weight: bold;
                color: #6f42c1;
                background-color: #f8f9fa;
                border: 3px solid #6f42c1;
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0;
            }
        """)
        layout.addWidget(self.display_tiempo)
        
        botones = QHBoxLayout()
        self.btn_iniciar = QPushButton("▶ Iniciar")
        self.btn_iniciar.setFixedHeight(45)
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_iniciar.clicked.connect(self.iniciar_temporizador)
        botones.addWidget(self.btn_iniciar)
        
        self.btn_detener = QPushButton("⏹ Detener")
        self.btn_detener.setEnabled(False)
        self.btn_detener.setFixedHeight(45)
        self.btn_detener.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.btn_detener.clicked.connect(self.detener_temporizador)
        botones.addWidget(self.btn_detener)
        layout.addLayout(botones)
        
        self.etiqueta_estado = QLabel("🔄 Listo para iniciar")
        self.etiqueta_estado.setAlignment(Qt.AlignCenter)
        self.etiqueta_estado.setStyleSheet("color: #6c757d; font-style: italic; font-size: 11px;")
        layout.addWidget(self.etiqueta_estado)
        
        self.setFrameStyle(QFrame.Box)
        self.setObjectName("temporizador_frame")
        
    def actualizar_display_configuracion(self):
        """Actualiza el display cuando se cambian los minutos/segundos sin estar ejecutándose"""
        if not self.timer_qt.isActive():  # Solo actualizar si no está corriendo
            minutos = self.spin_minutos.value()
            segundos = self.spin_segundos.value()
            tiempo_total = minutos * 60 + segundos
            # Actualizar display
            minutos_display = tiempo_total // 60
            segundos_display = tiempo_total % 60
            self.display_tiempo.setText(f"{minutos_display:02d}:{segundos_display:02d}")
            # Actualizar estado
            if tiempo_total > 0:
                self.etiqueta_estado.setText("🔄 Listo para iniciar")
            else:
                self.etiqueta_estado.setText("⚠ Configura un tiempo mayor a 0")
        
    def iniciar_temporizador(self):
        minutos = self.spin_minutos.value()
        segundos = self.spin_segundos.value()
        tiempo_total = minutos * 60 + segundos
        
        if tiempo_total <= 0:
            # Sin QMessageBox, solo mostrar en estado
            self.etiqueta_estado.setText("⚠ Configura un tiempo mayor a 0")
            return
        
        self.tiempo_total_segundos = tiempo_total
        self.tiempo_restante_segundos = tiempo_total
        self.timer_qt.start(1000)
        
        self.btn_iniciar.setText("⏸ Pausar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.pausar_temporizador)
        self.btn_detener.setEnabled(True)
        self.spin_minutos.setEnabled(False)
        self.spin_segundos.setEnabled(False)
        self.etiqueta_estado.setText("⏱ Temporizador activo...")
        
        # Actualizar display inmediatamente al iniciar
        minutos_display = self.tiempo_restante_segundos // 60
        segundos_display = self.tiempo_restante_segundos % 60
        self.display_tiempo.setText(f"{minutos_display:02d}:{segundos_display:02d}")
        
        self.temporizador_iniciado.emit()
        
    def pausar_temporizador(self):
        self.timer_qt.stop()
        self.btn_iniciar.setText("▶ Continuar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.continuar_temporizador)
        self.etiqueta_estado.setText("⏸ Temporizador pausado")
        
        # NUEVO: Emitir señal para pausar tonos activos
        self.temporizador_pausado.emit()
        
    def continuar_temporizador(self):
        self.timer_qt.start(1000)
        self.btn_iniciar.setText("⏸ Pausar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.pausar_temporizador)
        self.etiqueta_estado.setText("⏱ Temporizador activo...")
        
        # NUEVO: Emitir señal para reanudar tonos
        self.temporizador_reanudado.emit()
        
    def detener_temporizador(self):
        self.timer_qt.stop()
        self.btn_iniciar.setText("▶ Iniciar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.iniciar_temporizador)
        self.btn_detener.setEnabled(False)
        self.spin_minutos.setEnabled(True)
        self.spin_segundos.setEnabled(True)
        self.etiqueta_estado.setText("⏹ Temporizador detenido")
        
        # Restaurar display a la configuración actual
        self.actualizar_display_configuracion()
        
        # CORRECCIÓN: Emitir señal para detener tonos al detener temporizador manualmente
        self.temporizador_detenido.emit()
        
    def actualizar_display(self):
        self.tiempo_restante_segundos -= 1
        if self.tiempo_restante_segundos <= 0:
            self.detener_temporizador()
            self.etiqueta_estado.setText("✅ ¡Tiempo completado!")
            # CORRECCIÓN: Eliminar QMessageBox, solo emitir señal
            self.temporizador_finalizado.emit()
            return
        
        minutos = self.tiempo_restante_segundos // 60
        segundos = self.tiempo_restante_segundos % 60
        self.display_tiempo.setText(f"{minutos:02d}:{segundos:02d}")

class VentanaPrincipal(QMainWindow):
    """Ventana principal mejorada con todas las correcciones - PROBLEMAS SOLUCIONADOS"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("🔊 Sound Hz Emitter v2.0 - Generador Completo con Pomodoro")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Motor de audio real
        self.motor_audio = MotorAudioReal()
        
        # Gestor de temas
        self.theme_manager = ThemeManager(self)
        
        # Control de tonos
        self.controles_tonos = {}
        self.siguiente_id_tono = 1
        
        self.configurar_interfaz()
        self.agregar_nuevo_tono()
        
        # Aplicar tema inicial
        self.theme_manager.apply_theme()
        
        # Asegurar que el motor de audio esté disponible
        print("🔊 Motor de audio inicializado y listo")
        print(f"🎯 Modo de audio: {'Real' if AUDIO_DISPONIBLE else 'Simulación'}")
        print("⏱ Temporizador v4 + 🍅 Pomodoro v1.0 integrados")
        print("🎵 8 tipos de onda disponibles (incluye ruidos y pulsar)")
        print("🎨 Estilos modo oscuro completamente consistentes")
        print("📊 Mensaje en estadísticas con duración extendida (15s)")
        print("🔧 Todas las correcciones aplicadas exitosamente")
        
    def configurar_interfaz(self):
        """Configura la interfaz mejorada"""
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(20)
        
        self.crear_panel_controles(layout_principal)
        self.crear_panel_informacion(layout_principal)
        
        self.barra_estado = QStatusBar()
        self.setStatusBar(self.barra_estado)
        status_msg = "🔊 Sound Hz Emitter v2.0 VERSIÓN COMPLETA - "
        if AUDIO_DISPONIBLE:
            status_msg += "🎵 8 tipos de onda ✓ | 🍅 Pomodoro integrado ⏱ | 🎨 Modo oscuro perfecto | 🔧 Todas las correcciones ✅"
        else:
            status_msg += "🎵 8 tipos de onda (simulado) | 🍅 Pomodoro completo | 🎨 Temas perfectos | 🔧 Versión completa ✅"
        self.barra_estado.showMessage(status_msg)
        
    def crear_panel_controles(self, layout_padre):
        """Crea el panel izquierdo mejorado"""
        panel_controles = QWidget()
        layout_controles = QVBoxLayout(panel_controles)
        layout_controles.setSpacing(20)
        
        # Temporizador
        self.control_temporizador = ControlTemporizador()
        self.control_temporizador.temporizador_iniciado.connect(self.al_iniciar_temporizador)
        self.control_temporizador.temporizador_detenido.connect(self.al_detener_temporizador)
        self.control_temporizador.temporizador_finalizado.connect(self.al_finalizar_temporizador)
        self.control_temporizador.temporizador_pausado.connect(self.al_pausar_temporizador)  # NUEVO
        self.control_temporizador.temporizador_reanudado.connect(self.al_reanudar_temporizador)  # NUEVO
        layout_controles.addWidget(self.control_temporizador)
        
        # NUEVO: Control Pomodoro
        self.control_pomodoro = ControlPomodoro()
        self.control_pomodoro.pomodoro_iniciado.connect(self.al_iniciar_pomodoro)
        self.control_pomodoro.pomodoro_pausado.connect(self.al_pausar_pomodoro)
        self.control_pomodoro.pomodoro_finalizado.connect(self.al_finalizar_pomodoro)
        self.control_pomodoro.ciclo_completado.connect(self.al_completar_ciclo_pomodoro)
        layout_controles.addWidget(self.control_pomodoro)
        
        # Grupo de tonos mejorado
        grupo_tonos = QGroupBox("🎵 Control de Tonos")
        layout_grupo_tonos = QVBoxLayout(grupo_tonos)
        
        # Botones superiores
        botones_superiores = QHBoxLayout()
        
        btn_agregar_tono = QPushButton("➕ Agregar Nuevo Tono")
        btn_agregar_tono.setFixedHeight(40)
        btn_agregar_tono.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_agregar_tono.clicked.connect(self.agregar_nuevo_tono)
        botones_superiores.addWidget(btn_agregar_tono)
        
        btn_play_all = QPushButton("▶ Todo")
        btn_play_all.setFixedSize(80, 40)
        btn_play_all.clicked.connect(self.play_all_tones)
        botones_superiores.addWidget(btn_play_all)
        
        btn_stop_all = QPushButton("⏹ Todo")
        btn_stop_all.setFixedSize(80, 40)
        btn_stop_all.clicked.connect(self.stop_all_tones)
        botones_superiores.addWidget(btn_stop_all)
        
        layout_grupo_tonos.addLayout(botones_superiores)
        
        # Área de scroll mejorada
        self.scroll_area_tonos = QScrollArea()
        self.scroll_area_tonos.setObjectName("scroll_area_tonos")  # CORRECCIÓN: ID para estilos
        self.scroll_area_tonos.setWidgetResizable(True)
        self.scroll_area_tonos.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_tonos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_tonos.setMinimumHeight(350)
        self.scroll_area_tonos.setMaximumHeight(550)
        
        self.widget_contenedor_tonos = QWidget()
        self.widget_contenedor_tonos.setObjectName("widget_contenedor_tonos")  # CORRECCIÓN: ID para estilos
        self.layout_tonos = QVBoxLayout(self.widget_contenedor_tonos)
        self.layout_tonos.setSpacing(12)
        self.layout_tonos.setContentsMargins(10, 10, 10, 10)
        self.layout_tonos.addStretch()
        
        self.scroll_area_tonos.setWidget(self.widget_contenedor_tonos)
        layout_grupo_tonos.addWidget(self.scroll_area_tonos, 1)
        
        layout_controles.addWidget(grupo_tonos, 1)
        
        # Controles globales
        grupo_audio = QGroupBox("🎛 Controles Globales")
        layout_audio = QVBoxLayout(grupo_audio)
        
        # Primera fila de botones
        botones_audio = QHBoxLayout()
        
        self.btn_audio_global = QPushButton("🔊 Iniciar Audio")
        self.btn_audio_global.setFixedHeight(45)
        self.btn_audio_global.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.btn_audio_global.clicked.connect(self.alternar_audio_global)
        botones_audio.addWidget(self.btn_audio_global)
        
        btn_limpiar_tonos = QPushButton("🗑 Eliminar Todos")
        btn_limpiar_tonos.setFixedHeight(45)
        btn_limpiar_tonos.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_limpiar_tonos.clicked.connect(self.eliminar_todos_los_tonos)
        botones_audio.addWidget(btn_limpiar_tonos)
        
        layout_audio.addLayout(botones_audio)
        
        # Botón de tema
        btn_tema = QPushButton("🌓 Alternar Tema")
        btn_tema.setObjectName("btn_tema_oscuro")  # NUEVO: ID específico para estilos
        btn_tema.setFixedHeight(40)
        btn_tema.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a359a;
            }
        """)
        btn_tema.clicked.connect(self.theme_manager.toggle_theme)
        layout_audio.addWidget(btn_tema)
        
        layout_controles.addWidget(grupo_audio)
        layout_padre.addWidget(panel_controles, 2)
        
    def crear_panel_informacion(self, layout_padre):
        """Crea el panel derecho mejorado"""
        panel_info = QWidget()
        layout_info = QVBoxLayout(panel_info)
        
        # Información mejorada
        grupo_info = QGroupBox("📋 Información de la Aplicación")
        layout_grupo_info = QVBoxLayout(grupo_info)
        
        texto_informativo = QTextEdit()
        texto_informativo.setReadOnly(True)
        texto_informativo.setMaximumHeight(380)
        
        contenido_info = f"""
<h2>🔊 Sound Hz Emitter v2.0 VERSIÓN COMPLETA</h2>
<p><b>Generador Profesional de Frecuencias de Sonido con Pomodoro</b></p>

<h3>🆕 NUEVAS CARACTERÍSTICAS:</h3>
<ul>
<li><b>🎵 Nuevos Tipos de Onda:</b> Ruido Blanco, Rosa, Marrón + Onda Pulsar</li>
<li><b>🍅 Técnica Pomodoro:</b> Sistema completo de productividad personalizable</li>
<li><b>🎨 Colores Perfectos:</b> Modo oscuro completamente consistente</li>
<li><b>⚙ Configuraciones Predefinidas:</b> Clásico, Estudio Intensivo, Trabajo Creativo, etc.</li>
</ul>

<h3>✅ CORRECCIONES APLICADAS:</h3>
<ul>
<li><b>🔄 Reactivación Automática:</b> Los tonos habilitados ✓ se reactivan automáticamente</li>
<li><b>🔇 Sin Alertas:</b> Solo notificación silenciosa en estadísticas (15s)</li>
<li><b>🎨 Estilos Consistentes:</b> Todos los elementos perfectamente compatibles</li>
<li><b>🎯 Detención Inteligente:</b> Todos los controles funcionan correctamente</li>
<li><b>💾 Preservación de Estados:</b> Los checkboxes ✓ nunca se modifican automáticamente</li>
</ul>

<h3>🍅 Sistema Pomodoro:</h3>
<ul>
<li><b>Clásico (25/5/15):</b> 25min trabajo, 5min descanso, 15min descanso largo cada 4 ciclos</li>
<li><b>Estudio Intensivo (50/10/30):</b> Para sesiones académicas profundas</li>
<li><b>Trabajo Creativo (90/20/60):</b> Para tareas que requieren flujo prolongado</li>
<li><b>Concentración Ultra (120/30/90):</b> Para proyectos de máxima concentración</li>
<li><b>Sesiones Cortas (15/3/10):</b> Para tareas ligeras y multitasking</li>
<li><b>Personalizado:</b> Configura tus propios tiempos según necesidades</li>
</ul>

<h3>🎵 Tipos de Onda EXPANDIDOS:</h3>
<ul>
<li><b>Seno:</b> Tono puro, ideal para concentración básica</li>
<li><b>Cuadrada:</b> Sonido fuerte, para enmascarar ruidos</li>
<li><b>Triangular:</b> Equilibrado, bueno para trabajo prolongado</li>
<li><b>Sierra:</b> Brillante, estimula alertas mental</li>
<li><b>🆕 Ruido Blanco:</b> Enmascara todos los ruidos ambiente</li>
<li><b>🆕 Ruido Rosa:</b> Más natural, relajante para el oído</li>
<li><b>🆕 Ruido Marrón:</b> Profundo y calmante, ideal para sueño</li>
<li><b>🆕 Pulsar:</b> Onda modulada, para estimulación rítmica</li>
</ul>

<h3>📋 Cómo usar Pomodoro:</h3>
<ol>
<li><b>Seleccionar Modo:</b> Elige configuración predefinida o personalizada</li>
<li><b>Configurar Tonos:</b> Marca ✓ "Tono Habilitado" en tonos deseados</li>
<li><b>Iniciar Sesión:</b> ▶ Iniciar en el panel Pomodoro</li>
<li><b>Trabajo:</b> Los tonos se activan automáticamente para concentración</li>
<li><b>Descanso:</b> Los tonos se pausan para permitir relajación</li>
<li><b>Repetir:</b> El ciclo continúa automáticamente</li>
<li><b>Estadísticas:</b> Seguimiento de ciclos y sesiones completadas</li>
</ol>

<h3>🔧 Estado del Sistema:</h3>
<p><b>Audio:</b> {'🟢 Real EXPANDIDO' if AUDIO_DISPONIBLE else '🟡 Simulado EXPANDIDO'}</p>
<p><b>Tema:</b> {'🌙 Oscuro PERFECTO' if self.theme_manager.is_dark else '☀ Claro PERFECTO'}</p>
<p><b>Comportamiento:</b> 🤖 Gestión automática CORREGIDA</p>
<p><b>Temporizador:</b> ⏱ v4 DEFINITIVO + 🍅 Pomodoro v1.0</p>
<p><b>Tipos de Onda:</b> 🎵 8 tipos disponibles (4 tradicionales + 4 nuevos)</p>
<p><b>Productividad:</b> 🍅 Sistema Pomodoro completo integrado</p>
"""
        
        texto_informativo.setHtml(contenido_info)
        layout_grupo_info.addWidget(texto_informativo)
        layout_info.addWidget(grupo_info)
        
        # Estadísticas mejoradas
        grupo_stats = QGroupBox("📊 Estadísticas en Tiempo Real")
        layout_stats = QVBoxLayout(grupo_stats)
        
        self.etiqueta_stats = QLabel("🎵 Tonos configurados: 0\n▶ Tonos reproduciendo: 0\n🔊 Audio global: Detenido")
        self.etiqueta_stats.setObjectName("estadisticas_label")
        self.etiqueta_stats.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 15px;
                background-color: #e8f4fd;
                color: #0078d4;
                border-radius: 8px;
                border-left: 4px solid #0078d4;
            }
        """)
        layout_stats.addWidget(self.etiqueta_stats)
        
        layout_info.addWidget(grupo_stats)
        layout_info.addStretch()
        
        layout_padre.addWidget(panel_info, 1)
        
    def agregar_nuevo_tono(self):
        """Agrega un nuevo tono mejorado"""
        id_tono = self.siguiente_id_tono
        self.siguiente_id_tono += 1
        
        control_tono = ControlTonoMejorado(id_tono)
        control_tono.tono_modificado.connect(self.al_modificar_tono)
        control_tono.tono_eliminado.connect(self.eliminar_tono)
        
        spacer_index = self.layout_tonos.count() - 1
        self.layout_tonos.insertWidget(spacer_index, control_tono)
        self.controles_tonos[id_tono] = control_tono
        
        # Agregar al motor de audio (pero sin activar automáticamente)
        self.motor_audio.agregar_tono(id_tono, 440, 0.3, "seno", 0.0)
        
        # Asegurar que el control tenga referencia a la ventana principal
        control_tono.ventana_principal = self
        
        self.actualizar_estadisticas()
        self.barra_estado.showMessage(f"✅ Tono {id_tono} agregado - Total: {len(self.controles_tonos)} (Presiona ▶ para reproducir)")
        
        # Auto-scroll
        QTimer.singleShot(100, lambda: self.scroll_area_tonos.verticalScrollBar().setValue(
            self.scroll_area_tonos.verticalScrollBar().maximum()
        ))
        
    def iniciar_audio_global(self):
        """Inicia el audio global (función específica para los controles)"""
        if not self.motor_audio.reproduciendo:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("🔇 Detener Audio")
            self.barra_estado.showMessage("🔊 Audio global iniciado automáticamente")
            self.actualizar_estadisticas()
        
    def eliminar_tono(self, id_tono):
        """Elimina un tono"""
        if id_tono in self.controles_tonos:
            control = self.controles_tonos[id_tono]
            self.layout_tonos.removeWidget(control)
            control.deleteLater()
            del self.controles_tonos[id_tono]
            self.motor_audio.eliminar_tono(id_tono)
            self.actualizar_estadisticas()
            self.barra_estado.showMessage(f"🗑 Tono {id_tono} eliminado")

    def play_all_tones(self):
        """Reproduce todos los tonos"""
        tonos_iniciados = 0
        for control in self.controles_tonos.values():
            if not control.esta_reproduciendo:
                control.toggle_play_pause()
                tonos_iniciados += 1
        
        if tonos_iniciados > 0:
            self.barra_estado.showMessage(f"▶ {tonos_iniciados} tonos iniciados")
        else:
            self.barra_estado.showMessage("▶ Todos los tonos ya están reproduciendo")
        
    def stop_all_tones(self):
        """Detiene todos los tonos"""
        tonos_detenidos = 0
        for control in self.controles_tonos.values():
            if control.esta_reproduciendo:
                control.stop_tone()
                tonos_detenidos += 1
        
        if tonos_detenidos > 0:
            self.barra_estado.showMessage(f"⏹ {tonos_detenidos} tonos detenidos")
        else:
            self.barra_estado.showMessage("⏹ Todos los tonos ya están detenidos")
        # Verificar y detener audio global si es necesario
        self.verificar_y_gestionar_audio_global()
        
    def eliminar_todos_los_tonos(self):
        """Elimina todos los tonos con confirmación"""
        if not self.controles_tonos:
            return
        respuesta = QMessageBox.question(
            self, "Confirmar Eliminación", 
            f"¿Eliminar todos los {len(self.controles_tonos)} tonos?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            ids_tonos = list(self.controles_tonos.keys())
            for id_tono in ids_tonos:
                self.eliminar_tono(id_tono)
            self.barra_estado.showMessage("🗑 Todos los tonos eliminados")

    def al_modificar_tono(self, id_tono, configuracion):
        """CORREGIDO: Maneja modificaciones de tonos con actualización en tiempo real"""
        # IMPORTANTE: Actualizar inmediatamente en el motor de audio
        if AUDIO_DISPONIBLE and self.motor_audio.reproduciendo:
            # Forzar actualización inmediata en el hilo de audio
            self.motor_audio.actualizar_tono(id_tono, **configuracion)
            # NUEVO: Verificar que el tono esté activo en el motor si debe estarlo
            if configuracion.get('activo', False):
                self.motor_audio.set_tono_activo(id_tono, True)
            else:
                self.motor_audio.set_tono_activo(id_tono, False)
        else:
            # Modo simulación o audio detenido
            self.motor_audio.actualizar_tono(id_tono, **configuracion)
        
        self.actualizar_estadisticas()
        
        # Verificar si hay tonos activos para gestionar el audio global
        self.verificar_y_gestionar_audio_global()
        
        # Mensaje detallado en barra de estado
        freq = configuracion['frecuencia']
        vol = int(configuracion['volumen'] * 100)
        pan = configuracion['panning']
        pan_texto = f"L{abs(pan)*100:.0f}" if pan < -0.2 else f"R{pan*100:.0f}" if pan > 0.2 else "C"
        estado = "▶" if configuracion['activo'] else "⏸"
        tipo = configuracion.get('tipo_onda', 'seno').title()
        
        self.barra_estado.showMessage(f"{estado} Tono {id_tono}: {freq}Hz, {vol}%, {pan_texto}, {tipo} - Actualizado en tiempo real")
        
    def verificar_y_gestionar_audio_global(self):
        """Verifica si hay tonos activos y gestiona el audio global automáticamente"""
        tonos_activos = sum(1 for control in self.controles_tonos.values() 
                           if control.esta_reproduciendo and control.check_activo.isChecked())
        tonos_habilitados = sum(1 for control in self.controles_tonos.values() 
                               if control.check_activo.isChecked())
        tonos_configurados = len(self.controles_tonos)
        
        # Si no hay tonos activos pero el audio está corriendo, detenerlo automáticamente
        if tonos_activos == 0 and self.motor_audio.reproduciendo:
            self.motor_audio.detener()
            self.btn_audio_global.setText("🔊 Iniciar Audio")
            if tonos_habilitados > 0:
                self.barra_estado.showMessage(f"🔇 Audio detenido automáticamente - {tonos_habilitados} tonos habilitados (listos para reactivar)")
            elif tonos_configurados > 0:
                self.barra_estado.showMessage(f"🔇 Audio detenido automáticamente - {tonos_configurados} tonos pausados")
            else:
                self.barra_estado.showMessage("🔇 Audio detenido automáticamente - Sin tonos activos")
            self.actualizar_estadisticas()
        # Si hay tonos activos pero el audio no está corriendo, iniciarlo automáticamente
        elif tonos_activos > 0 and not self.motor_audio.reproduciendo:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("🔇 Detener Audio")
            self.barra_estado.showMessage(f"🔊 Audio iniciado automáticamente - {tonos_activos} tonos reproduciéndose")
            self.actualizar_estadisticas()
        
    def al_iniciar_temporizador(self):
        """CORRECCIÓN DEFINITIVA: Inicia temporizador con reactivación inteligente mejorada"""
        # Verificar estados de tonos
        tonos_disponibles = len(self.controles_tonos)
        tonos_activos = sum(1 for control in self.controles_tonos.values() 
                           if control.esta_reproduciendo and control.check_activo.isChecked())
        tonos_habilitados = sum(1 for control in self.controles_tonos.values() 
                               if control.check_activo.isChecked())
        
        print(f"DEBUG INICIAL: Tonos disponibles: {tonos_disponibles}, activos: {tonos_activos}, habilitados: {tonos_habilitados}")
        
        # CORRECCIÓN RADICAL: SIEMPRE intentar reactivar tonos habilitados, sin importar estado anterior
        if tonos_habilitados > 0:
            tonos_reactivados = 0
            for control in self.controles_tonos.values():
                if control.check_activo.isChecked() and not control.esta_reproduciendo:
                    print(f"DEBUG: Intentando reactivar tono {control.id_tono}")
                    if hasattr(control, 'reactivar_si_habilitado'):
                        if control.reactivar_si_habilitado():
                            tonos_reactivados += 1
                            print(f"DEBUG: Tono {control.id_tono} reactivado con éxito")
                    else:
                        # Fallback manual si no existe el método
                        control.esta_reproduciendo = True
                        control.btn_play_pause.setText("⏸")
                        control.btn_play_pause.setStyleSheet("""
                            QPushButton {
                                background-color: #ffc107;
                                color: black;
                                border: none;
                                border-radius: 17px;
                                font-weight: bold;
                                font-size: 14px;
                            }
                            QPushButton:hover {
                                background-color: #e0a800;
                            }
                        """)
                        control.etiqueta_estado.setText("▶ Reproduciendo")
                        control.etiqueta_estado.setStyleSheet("font-size: 11px; color: #28a745; font-weight: bold;")
                        control.emitir_cambios()
                        tonos_reactivados += 1
                        print(f"DEBUG: Tono {control.id_tono} reactivado con fallback manual")

            # Actualizar contadores después de reactivación
            tonos_activos = tonos_reactivados
            if tonos_reactivados > 0:
                self.barra_estado.showMessage(f"⏱ Temporizador iniciado - {tonos_reactivados} tonos reactivados automáticamente")
                print(f"DEBUG FINAL: {tonos_reactivados} tonos reactivados exitosamente")
            else:
                self.barra_estado.showMessage(f"⏱ Temporizador iniciado - {tonos_habilitados} tonos habilitados disponibles")
        
        # Iniciar audio global si no está activo y hay tonos disponibles
        if tonos_disponibles > 0 and not self.motor_audio.reproduciendo:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("🔇 Detener Audio")
            print("DEBUG: Motor de audio iniciado")
        
        # Mensajes informativos mejorados
        if tonos_activos == 0 and tonos_disponibles > 0:
            self.barra_estado.showMessage(f"⏱ Temporizador iniciado - {tonos_disponibles} tonos disponibles (marca ✓ para habilitar)")
        elif tonos_disponibles == 0:
            self.barra_estado.showMessage("⏱ Temporizador iniciado - Agrega tonos para comenzar")

        # Actualizar estadísticas
        self.actualizar_estadisticas()
        
    def al_detener_temporizador(self):
        """CORRECCIÓN: Detiene temporizador y todos los tonos activos"""
        # NUEVO: Detener todos los tonos activos al detener temporizador manualmente
        tonos_detenidos = 0
        for control in self.controles_tonos.values():
            if control.esta_reproduciendo:
                control.stop_tone(desde_temporizador=True)  # Preservar checkbox para próxima sesión
                tonos_detenidos += 1
        
        # Detener motor de audio si estaba activo
        if self.motor_audio.reproduciendo:
            self.motor_audio.detener()
            self.btn_audio_global.setText("🔊 Iniciar Audio")
        
        if tonos_detenidos > 0:
            self.barra_estado.showMessage(f"⏹ Temporizador detenido manualmente - {tonos_detenidos} tonos detenidos")
        else:
            self.barra_estado.showMessage("⏹ Temporizador detenido manualmente")

        # Actualizar estadísticas
        self.actualizar_estadisticas()

    def al_pausar_temporizador(self):
        """NUEVO: Maneja la pausa del temporizador - pausa tonos activos"""
        tonos_pausados = 0
        for control in self.controles_tonos.values():
            if hasattr(control, 'pausar_si_reproduciendose'):
                if control.pausar_si_reproduciendose():
                    tonos_pausados += 1
        
        if tonos_pausados > 0:
            self.barra_estado.showMessage(f"⏸ Temporizador pausado - {tonos_pausados} tonos pausados")
        else:
            self.barra_estado.showMessage("⏸ Temporizador pausado")

    def al_reanudar_temporizador(self):
        """NUEVO: Maneja la reanudación del temporizador - reanuda tonos pausados"""
        tonos_reanudados = 0
        for control in self.controles_tonos.values():
            if hasattr(control, 'reanudar_si_estaba_pausado_por_temporizador'):
                if control.reanudar_si_estaba_pausado_por_temporizador():
                    tonos_reanudados += 1
        
        if tonos_reanudados > 0:
            self.barra_estado.showMessage(f"▶ Temporizador reanudado - {tonos_reanudados} tonos reanudados")
        else:
            self.barra_estado.showMessage("▶ Temporizador reanudado")
        
        # Asegurar que el audio global esté activo
        self.verificar_y_gestionar_audio_global()
        
    def al_finalizar_temporizador(self):
        """CORRECCIÓN: Finaliza temporizador sin alertas y con mensaje en estadísticas"""
        # INMEDIATAMENTE detener todos los tonos activos
        tonos_detenidos = 0
        for control in self.controles_tonos.values():
            if control.esta_reproduciendo:
                control.esta_reproduciendo = False  # Detener estado interno inmediatamente
                control.stop_tone(desde_temporizador=True)  # CORRECCIÓN: Pasar flag para preservar checkbox
                tonos_detenidos += 1
        
        # Detener motor de audio inmediatamente
        if self.motor_audio.reproduciendo:
            self.motor_audio.detener()
            self.btn_audio_global.setText("🔊 Iniciar Audio")
        
        # CORRECCIÓN: Mostrar mensaje SOLO en estadísticas, sin QMessageBox
        self.actualizar_estadisticas_con_mensaje_finalizacion(tonos_detenidos)
        
        # Mensaje en barra de estado (silencioso)
        if tonos_detenidos > 0:
            self.barra_estado.showMessage(f"✅ Sesión completada - {tonos_detenidos} tonos detenidos automáticamente")
        else:
            self.barra_estado.showMessage("✅ ¡Sesión completada!")

        # Sincronizar estados para próxima ejecución (con delay corto)
        QTimer.singleShot(100, self.sincronizar_estados_tonos)
        
    def actualizar_estadisticas_con_mensaje_finalizacion(self, tonos_detenidos):
        """CORRECCIÓN: Actualiza estadísticas mostrando mensaje de finalización silencioso"""
        total_tonos = len(self.controles_tonos)
        tonos_reproduciendo = 0  # Todos se detuvieron
        tonos_habilitados = sum(1 for control in self.controles_tonos.values() 
                               if control.check_activo.isChecked())
        
        estado_audio = "🔇 Detenido"
        # CORRECCIÓN: Mensaje más claro y directo en las estadísticas
        mensaje_finalizacion = "⏰ ¡El tiempo configurado ha finalizado!"
        if tonos_detenidos > 0:
            mensaje_finalizacion += f" - {tonos_detenidos} tonos detenidos"
        
        # Mostrar en estadísticas el estado especial de finalización
        self.etiqueta_stats.setText(
            f"🎵 Tonos configurados: {total_tonos}\n"
            f"▶ Tonos reproduciendo: {tonos_reproduciendo}\n"
            f"✓ Tonos habilitados: {tonos_habilitados}\n"
            f"🔊 Audio global: {estado_audio}\n"
            f"📊 Estado: {mensaje_finalizacion}"
        )
        
        # CORRECCIÓN: Restaurar estadísticas normales después de 15 segundos (más tiempo)
        QTimer.singleShot(15000, self.actualizar_estadisticas)
        
    def alternar_audio_global(self):
        """Alterna audio global"""
        if self.motor_audio.reproduciendo:
            self.motor_audio.detener()
            self.btn_audio_global.setText("🔊 Iniciar Audio")
            self.barra_estado.showMessage("🔇 Audio global detenido")
        else:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("🔇 Detener Audio")
            self.barra_estado.showMessage("🔊 Audio global iniciado")
        self.actualizar_estadisticas()

    def sincronizar_estados_tonos(self):
        """CORRECCIÓN: Sincroniza los estados visuales preservando checkboxes para reactivación"""
        for control in self.controles_tonos.values():
            # Verificar consistencia entre estado visual y audio real
            if hasattr(control, 'esta_reproduciendo'):
                if not control.esta_reproduciendo:
                    # Asegurar que el botón esté en estado de play
                    control.btn_play_pause.setText("▶")
                    control.btn_play_pause.setStyleSheet("""
                        QPushButton {
                            background-color: #28a745;
                            color: white;
                            border: none;
                            border-radius: 17px;
                            font-weight: bold;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #218838;
                        }
                    """)
                    control.etiqueta_estado.setText("⏹ Detenido")
                    control.etiqueta_estado.setStyleSheet("font-size: 11px; color: #dc3545; font-weight: bold;")
                    # CORRECCIÓN CRÍTICA: NO desmarcar check_activo para permitir reactivación automática
                    # Los checkboxes se mantienen para la próxima sesión del temporizador
        
        # Actualizar estadísticas después de sincronizar
        self.actualizar_estadisticas()
        
    def actualizar_estadisticas(self):
        """Actualiza estadísticas (versión mejorada)"""
        total_tonos = len(self.controles_tonos)
        tonos_reproduciendo = sum(1 for control in self.controles_tonos.values() 
                                 if control.esta_reproduciendo and control.check_activo.isChecked())
        tonos_habilitados = sum(1 for control in self.controles_tonos.values() 
                               if control.check_activo.isChecked())
        
        estado_audio = "🔊 Activo" if self.motor_audio.reproduciendo else "🔇 Detenido"
        
        # Mostrar información más detallada
        texto_stats = f"🎵 Tonos configurados: {total_tonos}\n"
        texto_stats += f"▶ Tonos reproduciendo: {tonos_reproduciendo}\n"
        if tonos_habilitados > tonos_reproduciendo and tonos_habilitados > 0:
            texto_stats += f"✓ Tonos habilitados: {tonos_habilitados}\n"
        texto_stats += f"🔊 Audio global: {estado_audio}"
        
        self.etiqueta_stats.setText(texto_stats)
    
    def al_iniciar_pomodoro(self):
        """NUEVO: Maneja el inicio del Pomodoro - reactivación automática mejorada"""
        # Verificar estados de tonos
        tonos_disponibles = len(self.controles_tonos)
        tonos_activos = sum(1 for control in self.controles_tonos.values()
                           if control.esta_reproduciendo and control.check_activo.isChecked())
        tonos_habilitados = sum(1 for control in self.controles_tonos.values()
                               if control.check_activo.isChecked())
        
        print(f"DEBUG POMODORO: Tonos disponibles: {tonos_disponibles}, activos: {tonos_activos}, habilitados: {tonos_habilitados}")
        
        # REACTIVAR tonos habilitados para sesión de trabajo
        if tonos_habilitados > 0:
            tonos_reactivados = 0
            for control in self.controles_tonos.values():
                if control.check_activo.isChecked() and not control.esta_reproduciendo:
                    print(f"DEBUG: Reactivando tono {control.id_tono} para Pomodoro")
                    if hasattr(control, 'reactivar_si_habilitado'):
                        if control.reactivar_si_habilitado():
                            tonos_reactivados += 1
                    else:
                        # Fallback manual
                        control.esta_reproduciendo = True
                        control.btn_play_pause.setText("⏸")
                        control.btn_play_pause.setStyleSheet("""
                            QPushButton {
                                background-color: #ffc107;
                                color: black;
                                border: none;
                                border-radius: 17px;
                                font-weight: bold;
                                font-size: 14px;
                            }
                            QPushButton:hover {
                                background-color: #e0a800;
                            }
                        """)
                        control.etiqueta_estado.setText("▶ Reproduciendo")
                        control.etiqueta_estado.setStyleSheet("font-size: 11px; color: #28a745; font-weight: bold;")
                        control.emitir_cambios()
                        tonos_reactivados += 1
            
            if tonos_reactivados > 0:
                self.barra_estado.showMessage(f"🍅 Pomodoro iniciado - {tonos_reactivados} tonos reactivados para concentración")
            else:
                self.barra_estado.showMessage(f"🍅 Pomodoro iniciado - {tonos_habilitados} tonos habilitados disponibles")
        
        # Iniciar audio global si no está activo
        if tonos_disponibles > 0 and not self.motor_audio.reproduciendo:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("🔇 Detener Audio")
        
        # Mensaje informativo si no hay tonos
        if tonos_disponibles == 0:
            self.barra_estado.showMessage("🍅 Pomodoro iniciado - Agrega tonos para acompañar el trabajo")
        
        self.actualizar_estadisticas()
    
    def al_pausar_pomodoro(self):
        """NUEVO: Maneja la pausa del Pomodoro"""
        tonos_pausados = 0
        for control in self.controles_tonos.values():
            if control.esta_reproduciendo:
                control.stop_tone(desde_pausa_temporizador=True)
                tonos_pausados += 1
        
        if tonos_pausados > 0:
            self.barra_estado.showMessage(f"🍅 Pomodoro pausado - {tonos_pausados} tonos pausados")
        else:
            self.barra_estado.showMessage("🍅 Pomodoro pausado")
        
        self.actualizar_estadisticas()
    
    def al_finalizar_pomodoro(self):
        """NUEVO: Maneja la finalización del Pomodoro"""
        tonos_detenidos = 0
        for control in self.controles_tonos.values():
            if control.esta_reproduciendo:
                control.stop_tone(desde_temporizador=True)
                tonos_detenidos += 1
        
        # Detener motor de audio
        if self.motor_audio.reproduciendo:
            self.motor_audio.detener()
            self.btn_audio_global.setText("🔊 Iniciar Audio")
        
        if tonos_detenidos > 0:
            self.barra_estado.showMessage(f"🍅 Pomodoro finalizado - {tonos_detenidos} tonos detenidos")
        else:
            self.barra_estado.showMessage("🍅 Pomodoro finalizado")
        
        self.actualizar_estadisticas()
    
    def al_completar_ciclo_pomodoro(self, tipo_ciclo):
        """NUEVO: Maneja la completación de un ciclo de Pomodoro"""
        if tipo_ciclo == "trabajo":
            # Al terminar trabajo, pasar a descanso - PAUSAR tonos
            tonos_pausados = 0
            for control in self.controles_tonos.values():
                if control.esta_reproduciendo:
                    control.stop_tone(desde_pausa_temporizador=True)
                    tonos_pausados += 1
            
            self.barra_estado.showMessage(f"🍅 Trabajo completado - Tiempo de descanso (tonos pausados)")
            
        elif tipo_ciclo == "descanso":
            # Al terminar descanso, volver a trabajo - REACTIVAR tonos habilitados
            tonos_reactivados = 0
            for control in self.controles_tonos.values():
                if control.check_activo.isChecked() and not control.esta_reproduciendo:
                    if hasattr(control, 'reactivar_si_habilitado'):
                        if control.reactivar_si_habilitado():
                            tonos_reactivados += 1
                    else:
                        # Fallback manual
                        control.esta_reproduciendo = True
                        control.btn_play_pause.setText("⏸")
                        control.etiqueta_estado.setText("▶ Reproduciendo")
                        control.emitir_cambios()
                        tonos_reactivados += 1
            
            if tonos_reactivados > 0:
                self.barra_estado.showMessage(f"🍅 Descanso completado - Volviendo al trabajo ({tonos_reactivados} tonos reactivados)")
            else:
                self.barra_estado.showMessage("🍅 Descanso completado - Volviendo al trabajo")
            
            # Asegurar audio global activo
            self.verificar_y_gestionar_audio_global()
        
        self.actualizar_estadisticas()
    
    def closeEvent(self, event):
        """Cierre de aplicación"""
        # Detener todos los tonos primero
        for control in self.controles_tonos.values():
            if control.esta_reproduciendo:
                control.stop_tone()
        
        # Detener motor de audio
        self.motor_audio.detener()
        
        # Detener temporizador
        if hasattr(self, 'control_temporizador'):
            self.control_temporizador.timer_qt.stop()
        print("🔊 Sound Hz Emitter cerrado correctamente")
        event.accept()
        
    def forzar_sincronizacion_completa(self):
        """Fuerza la sincronización completa de todos los estados (método de emergencia)"""
        print("🔄 Forzando sincronización completa de estados...")
        
        # Sincronizar cada tono
        self.sincronizar_estados_tonos()
        
        # Verificar y corregir audio global
        self.verificar_y_gestionar_audio_global()
        
        # Actualizar estadísticas
        self.actualizar_estadisticas()
        
        print("✅ Sincronización completa finalizada")