"""Ventana principal mejorada con audio real, temas y controles individuales"""

import sys
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QSlider, QComboBox, QCheckBox,
    QFrame, QGroupBox, QStatusBar, QMessageBox, QTextEdit,
    QScrollArea, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QPalette, QColor

# Imports condicionales para audio
try:
    import sounddevice as sd
    AUDIO_DISPONIBLE = True
except ImportError:
    AUDIO_DISPONIBLE = False

class AudioThread(QThread):
    """Hilo para generación de audio en tiempo real"""
    
    def __init__(self, sample_rate=44100):
        super().__init__()
        self.sample_rate = sample_rate
        self.running = False
        self.tonos_activos = {}
        self.stream = None
        
    def add_tone(self, tone_id, frequency, volume, wave_type="sine", active=True):
        """Añade o actualiza un tono"""
        self.tonos_activos[tone_id] = {
            'frequency': frequency,
            'volume': volume,
            'wave_type': wave_type,
            'active': active,
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
        """Genera una forma de onda"""
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
        else:
            wave = np.sin(2 * np.pi * frequency * t)
            
        return wave, t[-1] if len(t) > 0 else 0
    
    def audio_callback(self, outdata, frames, time, status):
        """Callback para generación de audio"""
        if status:
            print(f"Audio status: {status}")
            
        # Inicializar buffer
        buffer = np.zeros(frames, dtype=np.float32)
        
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
                
                # Mezclar con buffer
                buffer += wave
                
                # Actualizar fase
                tone_data['phase'] = new_phase
        
        # Normalizar para evitar clipping
        if len(self.tonos_activos) > 0:
            max_amplitude = np.max(np.abs(buffer))
            if max_amplitude > 0.8:
                buffer = buffer * 0.8 / max_amplitude
        
        # Copiar a salida (mono a estéreo)
        outdata[:, 0] = buffer
        outdata[:, 1] = buffer
    
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
    """Motor de audio real usando sounddevice"""
    
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
        
    def agregar_tono(self, id_tono, frecuencia, volumen, tipo_onda="seno"):
        """Agrega un tono"""
        if AUDIO_DISPONIBLE:
            self.audio_thread.add_tone(id_tono, frecuencia, volumen, tipo_onda)
        print(f"Tono {id_tono} agregado: {frecuencia} Hz")
        
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
        
    def set_tono_activo(self, id_tono, activo):
        """Activa/desactiva un tono"""
        if AUDIO_DISPONIBLE:
            self.audio_thread.set_tone_active(id_tono, activo)

class ThemeManager:
    """Gestor de temas claro y oscuro"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.is_dark = False
        
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        self.is_dark = not self.is_dark
        self.apply_theme()
        
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
            }
            QScrollBar::handle:vertical {
                background-color: #0078d4;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #106ebe;
            }
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        
    def apply_dark_theme(self):
        """Aplica tema oscuro"""
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
            }
            QScrollBar::handle:vertical {
                background-color: #64b5f6;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #42a5f5;
            }
            QStatusBar {
                background-color: #505050;
                border-top: 1px solid #666666;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #404040;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QSpinBox, QSlider, QComboBox {
                background-color: #404040;
                border: 1px solid #555555;
                color: #ffffff;
            }
        """)

class ControlTonoMejorado(QFrame):
    """Widget mejorado para controlar un tono individual con play/pause/stop"""
    
    tono_modificado = Signal(int, dict)
    tono_eliminado = Signal(int)
    
    def __init__(self, id_tono, frecuencia_inicial=440):
        super().__init__()
        self.id_tono = id_tono
        self.esta_reproduciendo = False
        self.configurar_interfaz(frecuencia_inicial)
        
    def configurar_interfaz(self, frecuencia_inicial):
        """Configura la interfaz mejorada del control de tono"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Cabecera con titulo, controles y eliminar
        cabecera = QHBoxLayout()
        
        # Título
        titulo = QLabel(f"♪ Tono {self.id_tono}")
        titulo.setStyleSheet("font-weight: bold; font-size: 13px; color: #0078d4;")
        cabecera.addWidget(titulo)
        
        # Espaciador
        cabecera.addStretch()
        
        # Controles de reproducción individuales
        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setMaximumSize(30, 30)
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        cabecera.addWidget(self.btn_play_pause)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setMaximumSize(30, 30)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_tone)
        cabecera.addWidget(self.btn_stop)
        
        # Botón eliminar
        btn_eliminar = QPushButton("✕")
        btn_eliminar.setMaximumSize(30, 30)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.tono_eliminado.emit(self.id_tono))
        cabecera.addWidget(btn_eliminar)
        
        layout.addLayout(cabecera)
        
        # Primera fila de controles
        controles_1 = QHBoxLayout()
        
        # Frecuencia
        grupo_freq = QVBoxLayout()
        etiqueta_freq = QLabel("Frecuencia")
        etiqueta_freq.setStyleSheet("font-weight: bold; font-size: 10px;")
        grupo_freq.addWidget(etiqueta_freq)
        
        self.spin_frecuencia = QSpinBox()
        self.spin_frecuencia.setRange(20, 20000)
        self.spin_frecuencia.setValue(frecuencia_inicial)
        self.spin_frecuencia.setSuffix(" Hz")
        self.spin_frecuencia.setMinimumWidth(90)
        self.spin_frecuencia.valueChanged.connect(self.emitir_cambios)
        grupo_freq.addWidget(self.spin_frecuencia)
        
        controles_1.addLayout(grupo_freq)
        
        # Volumen
        grupo_vol = QVBoxLayout()
        etiqueta_vol = QLabel("Volumen")
        etiqueta_vol.setStyleSheet("font-weight: bold; font-size: 10px;")
        grupo_vol.addWidget(etiqueta_vol)
        
        self.slider_volumen = QSlider(Qt.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(30)  # Volumen inicial más bajo
        self.slider_volumen.setMinimumWidth(100)
        self.slider_volumen.valueChanged.connect(self.emitir_cambios)
        grupo_vol.addWidget(self.slider_volumen)
        
        self.etiqueta_volumen = QLabel("30%")
        self.etiqueta_volumen.setAlignment(Qt.AlignCenter)
        self.etiqueta_volumen.setStyleSheet("font-size: 9px;")
        grupo_vol.addWidget(self.etiqueta_volumen)
        
        controles_1.addLayout(grupo_vol)
        
        layout.addLayout(controles_1)
        
        # Segunda fila de controles
        controles_2 = QHBoxLayout()
        
        # Tipo de onda
        grupo_onda = QVBoxLayout()
        etiqueta_onda = QLabel("Tipo de Onda")
        etiqueta_onda.setStyleSheet("font-weight: bold; font-size: 10px;")
        grupo_onda.addWidget(etiqueta_onda)
        
        self.combo_onda = QComboBox()
        self.combo_onda.addItems(["Seno", "Cuadrada", "Triangular", "Sierra"])
        self.combo_onda.setMinimumWidth(100)
        self.combo_onda.currentTextChanged.connect(self.emitir_cambios)
        grupo_onda.addWidget(self.combo_onda)
        
        controles_2.addLayout(grupo_onda)
        
        # Estado
        grupo_estado = QVBoxLayout()
        etiqueta_estado = QLabel("Estado")
        etiqueta_estado.setStyleSheet("font-weight: bold; font-size: 10px;")
        grupo_estado.addWidget(etiqueta_estado)
        
        self.etiqueta_estado = QLabel("⏸ Pausado")
        self.etiqueta_estado.setStyleSheet("font-size: 10px; color: #666;")
        grupo_estado.addWidget(self.etiqueta_estado)
        
        controles_2.addLayout(grupo_estado)
        
        layout.addLayout(controles_2)
        
        # Checkbox master
        self.check_activo = QCheckBox("🔊 Tono Habilitado")
        self.check_activo.setChecked(True)
        self.check_activo.setStyleSheet("font-weight: bold; color: #28a745;")
        self.check_activo.toggled.connect(self.emitir_cambios)
        layout.addWidget(self.check_activo)
        
        # Estilo del frame
        self.setFrameStyle(QFrame.Box)
        self.setFixedHeight(180)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                background-color: #fafafa;
                margin: 2px;
            }
        """)
        
    def toggle_play_pause(self):
        """Alterna entre play y pause para este tono"""
        self.esta_reproduciendo = not self.esta_reproduciendo
        
        if self.esta_reproduciendo:
            self.btn_play_pause.setText("⏸")
            self.btn_play_pause.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
            """)
            self.etiqueta_estado.setText("▶ Reproduciendo")
            self.etiqueta_estado.setStyleSheet("font-size: 10px; color: #28a745; font-weight: bold;")
            # Activar el tono
            self.check_activo.setChecked(True)
        else:
            self.btn_play_pause.setText("▶")
            self.btn_play_pause.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.etiqueta_estado.setText("⏸ Pausado")
            self.etiqueta_estado.setStyleSheet("font-size: 10px; color: #ffc107; font-weight: bold;")
            
        self.emitir_cambios()
        
    def stop_tone(self):
        """Detiene completamente este tono"""
        self.esta_reproduciendo = False
        self.btn_play_pause.setText("▶")
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.etiqueta_estado.setText("⏹ Detenido")
        self.etiqueta_estado.setStyleSheet("font-size: 10px; color: #dc3545; font-weight: bold;")
        self.check_activo.setChecked(False)
        self.emitir_cambios()
        
    def emitir_cambios(self):
        """Emite los cambios realizados en el control"""
        volumen_porcentaje = self.slider_volumen.value()
        self.etiqueta_volumen.setText(f"{volumen_porcentaje}%")
        
        configuracion = {
            'frecuencia': self.spin_frecuencia.value(),
            'volumen': volumen_porcentaje / 100.0,
            'tipo_onda': self.combo_onda.currentText().lower(),
            'activo': self.check_activo.isChecked() and self.esta_reproduciendo
        }
        
        self.tono_modificado.emit(self.id_tono, configuracion)

class ControlTemporizador(QFrame):
    """Widget del temporizador (sin cambios)"""
    
    temporizador_iniciado = Signal()
    temporizador_detenido = Signal()
    temporizador_finalizado = Signal()
    
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
        self.spin_minutos.setMinimumWidth(60)
        config_tiempo.addWidget(self.spin_minutos)
        
        config_tiempo.addWidget(QLabel("Seg:"))
        self.spin_segundos = QSpinBox()
        self.spin_segundos.setRange(0, 59)
        self.spin_segundos.setValue(0)
        self.spin_segundos.setMinimumWidth(60)
        config_tiempo.addWidget(self.spin_segundos)
        layout.addLayout(config_tiempo)
        
        self.display_tiempo = QLabel("05:00")
        self.display_tiempo.setAlignment(Qt.AlignCenter)
        self.display_tiempo.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', 'Monaco', monospace;
                font-size: 32px;
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
        
    def iniciar_temporizador(self):
        minutos = self.spin_minutos.value()
        segundos = self.spin_segundos.value()
        tiempo_total = minutos * 60 + segundos
        
        if tiempo_total <= 0:
            QMessageBox.warning(self, "Error", "⚠ Configura un tiempo mayor a 0")
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
        self.temporizador_iniciado.emit()
        
    def pausar_temporizador(self):
        self.timer_qt.stop()
        self.btn_iniciar.setText("▶ Continuar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.continuar_temporizador)
        self.etiqueta_estado.setText("⏸ Temporizador pausado")
        
    def continuar_temporizador(self):
        self.timer_qt.start(1000)
        self.btn_iniciar.setText("⏸ Pausar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.pausar_temporizador)
        self.etiqueta_estado.setText("⏱ Temporizador activo...")
        
    def detener_temporizador(self):
        self.timer_qt.stop()
        self.btn_iniciar.setText("▶ Iniciar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.iniciar_temporizador)
        self.btn_detener.setEnabled(False)
        self.spin_minutos.setEnabled(True)
        self.spin_segundos.setEnabled(True)
        self.etiqueta_estado.setText("⏹ Temporizador detenido")
        self.temporizador_detenido.emit()
        
    def actualizar_display(self):
        self.tiempo_restante_segundos -= 1
        if self.tiempo_restante_segundos <= 0:
            self.detener_temporizador()
            self.etiqueta_estado.setText("✅ ¡Tiempo completado!")
            QMessageBox.information(self, "Temporizador", "⏰ ¡El tiempo configurado ha terminado!")
            self.temporizador_finalizado.emit()
            return
        
        minutos = self.tiempo_restante_segundos // 60
        segundos = self.tiempo_restante_segundos % 60
        self.display_tiempo.setText(f"{minutos:02d}:{segundos:02d}")

class VentanaPrincipal(QMainWindow):
    """Ventana principal mejorada con todas las correcciones"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("🔊 Sound Hz Emitter v2.0 - Generador de Frecuencias")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
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
        status_msg = "🔊 Sound Hz Emitter v2.0 - "
        if AUDIO_DISPONIBLE:
            status_msg += "Audio real disponible ✓"
        else:
            status_msg += "Modo simulación (instala sounddevice para audio real)"
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
        layout_controles.addWidget(self.control_temporizador)
        
        # Grupo de tonos mejorado
        grupo_tonos = QGroupBox("🎵 Control de Tonos")
        layout_grupo_tonos = QVBoxLayout(grupo_tonos)
        
        # Botones superiores
        botones_superiores = QHBoxLayout()
        
        btn_agregar_tono = QPushButton("➕ Agregar Nuevo Tono")
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
        btn_play_all.setMaximumWidth(80)
        btn_play_all.clicked.connect(self.play_all_tones)
        botones_superiores.addWidget(btn_play_all)
        
        btn_stop_all = QPushButton("⏹ Todo")
        btn_stop_all.setMaximumWidth(80)
        btn_stop_all.clicked.connect(self.stop_all_tones)
        botones_superiores.addWidget(btn_stop_all)
        
        layout_grupo_tonos.addLayout(botones_superiores)
        
        # Área de scroll mejorada
        self.scroll_area_tonos = QScrollArea()
        self.scroll_area_tonos.setWidgetResizable(True)
        self.scroll_area_tonos.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_tonos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_tonos.setMinimumHeight(250)
        self.scroll_area_tonos.setMaximumHeight(450)
        
        self.widget_contenedor_tonos = QWidget()
        self.layout_tonos = QVBoxLayout(self.widget_contenedor_tonos)
        self.layout_tonos.setSpacing(8)
        self.layout_tonos.setContentsMargins(8, 8, 8, 8)
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
        texto_informativo.setMaximumHeight(350)
        
        contenido_info = f"""
<h2>🔊 Sound Hz Emitter v2.0</h2>
<p><b>Generador Profesional de Frecuencias de Sonido</b></p>

<h3>✨ Nuevas Características:</h3>
<ul>
<li><b>🎮 Controles Individuales:</b> Play/Pause/Stop para cada tono</li>
<li><b>🎨 Temas:</b> Modo claro y oscuro</li>
<li><b>🔊 Audio Real:</b> {'Disponible' if AUDIO_DISPONIBLE else 'No disponible (instala sounddevice)'}</li>
<li><b>📱 Scroll Mejorado:</b> Navegación fluida entre tonos</li>
</ul>

<h3>📋 Cómo usar:</h3>
<ol>
<li><b>Agregar Tonos:</b> ➕ Agregar Nuevo Tono</li>
<li><b>Control Individual:</b> ▶ para reproducir, ⏸ pausar, ⏹ detener</li>
<li><b>Scroll en Tonos:</b> Rueda del mouse o barra lateral</li>
<li><b>Configurar:</b> Frecuencia (20-20,000 Hz), Volumen (0-100%)</li>
<li><b>Tipos de Onda:</b> Seno, Cuadrada, Triangular, Sierra</li>
<li><b>Control Global:</b> 🔊 Iniciar/Detener todo el audio</li>
<li><b>Temporizador:</b> ⏱ Para sesiones programadas</li>
<li><b>Cambiar Tema:</b> 🌓 Alternar entre claro y oscuro</li>
</ol>

<h3>🎵 Tipos de Onda:</h3>
<ul>
<li><b>Seno:</b> Tono puro, ideal para relajación y terapia</li>
<li><b>Cuadrada:</b> Sonido fuerte con armónicos, energético</li>
<li><b>Triangular:</b> Suave pero con carácter, equilibrado</li>
<li><b>Sierra:</b> Brillante con muchos armónicos</li>
</ul>

<h3>🔧 Estado del Sistema:</h3>
<p><b>Audio:</b> {'🟢 Real (SoundDevice)' if AUDIO_DISPONIBLE else '🟡 Simulado'}</p>
<p><b>Tema:</b> {'🌙 Oscuro' if hasattr(self, 'theme_manager') and self.theme_manager.is_dark else '☀ Claro'}</p>
"""
        
        texto_informativo.setHtml(contenido_info)
        layout_grupo_info.addWidget(texto_informativo)
        layout_info.addWidget(grupo_info)
        
        # Estadísticas mejoradas
        grupo_stats = QGroupBox("📊 Estadísticas en Tiempo Real")
        layout_stats = QVBoxLayout(grupo_stats)
        
        self.etiqueta_stats = QLabel("🎵 Tonos configurados: 0\n▶ Tonos reproduciendo: 0\n🔊 Audio global: Detenido")
        self.etiqueta_stats.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 15px;
                background-color: #e8f4fd;
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
        
        self.motor_audio.agregar_tono(id_tono, 440, 0.3)
        self.actualizar_estadisticas()
        self.barra_estado.showMessage(f"✅ Tono {id_tono} agregado - Total: {len(self.controles_tonos)}")
        
        # Auto-scroll
        QTimer.singleShot(100, lambda: self.scroll_area_tonos.verticalScrollBar().setValue(
            self.scroll_area_tonos.verticalScrollBar().maximum()
        ))
        
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
        for control in self.controles_tonos.values():
            if not control.esta_reproduciendo:
                control.toggle_play_pause()
        self.barra_estado.showMessage("▶ Todos los tonos iniciados")
        
    def stop_all_tones(self):
        """Detiene todos los tonos"""
        for control in self.controles_tonos.values():
            if control.esta_reproduciendo:
                control.stop_tone()
        self.barra_estado.showMessage("⏹ Todos los tonos detenidos")
        
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
        """Maneja modificaciones de tonos"""
        self.motor_audio.actualizar_tono(id_tono, **configuracion)
        self.actualizar_estadisticas()
        
        freq = configuracion['frecuencia']
        vol = int(configuracion['volumen'] * 100)
        estado = "▶" if configuracion['activo'] else "⏸"
        self.barra_estado.showMessage(f"{estado} Tono {id_tono}: {freq} Hz, {vol}%")
        
    def al_iniciar_temporizador(self):
        """Inicia temporizador"""
        if not self.motor_audio.reproduciendo:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("🔇 Detener Audio")
        self.barra_estado.showMessage("⏱ Temporizador iniciado - Audio activo")
        
    def al_detener_temporizador(self):
        """Detiene temporizador"""
        self.barra_estado.showMessage("⏱ Temporizador detenido")
        
    def al_finalizar_temporizador(self):
        """Finaliza temporizador"""
        self.barra_estado.showMessage("✅ ¡Sesión completada!")
        
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
            
    def actualizar_estadisticas(self):
        """Actualiza estadísticas"""
        total_tonos = len(self.controles_tonos)
        tonos_reproduciendo = sum(1 for control in self.controles_tonos.values() 
                                 if control.esta_reproduciendo and control.check_activo.isChecked())
        
        estado_audio = "🔊 Activo" if self.motor_audio.reproduciendo else "🔇 Detenido"
        
        self.etiqueta_stats.setText(
            f"🎵 Tonos configurados: {total_tonos}\n"
            f"▶ Tonos reproduciendo: {tonos_reproduciendo}\n"
            f"🔊 Audio global: {estado_audio}"
        )
        
    def closeEvent(self, event):
        """Cierre de aplicación"""
        self.motor_audio.detener()
        if hasattr(self, 'control_temporizador'):
            self.control_temporizador.timer_qt.stop()
        print("🔊 Sound Hz Emitter cerrado correctamente")
        event.accept()