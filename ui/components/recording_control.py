"""
Sistema de grabación de audio para sesiones de timer y pomodoro
"""

import os
import numpy as np
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QComboBox, QSpinBox, QCheckBox,
                              QFileDialog, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, Signal, QThread, QTimer

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

class AudioRecorder(QThread):
    """Hilo para grabación de audio"""
    
    recording_progress = Signal(int)  # Progreso en segundos
    recording_finished = Signal(str)  # Archivo generado
    recording_error = Signal(str)     # Error en grabación
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.output_file = ""
        self.format = "wav"
        self.duration = 0
        self.audio_callback = None
    
    def start_recording(self, output_file, format_type, expected_duration, audio_callback):
        """Inicia la grabación"""
        self.output_file = output_file
        self.format = format_type.lower()
        self.duration = expected_duration
        self.audio_callback = audio_callback
        self.audio_data = []
        self.is_recording = True
        self.start()
    
    def stop_recording(self):
        """Detiene la grabación"""
        self.is_recording = False
        self.wait()
    
    def run(self):
        """Loop de grabación"""
        start_time = datetime.now()
        
        try:
            while self.is_recording:
                # Capturar audio del callback
                if self.audio_callback:
                    audio_chunk = self.audio_callback()
                    if audio_chunk is not None:
                        self.audio_data.append(audio_chunk)
                
                # Calcular progreso
                elapsed = (datetime.now() - start_time).total_seconds()
                self.recording_progress.emit(int(elapsed))
                
                # Verificar si se alcanzó la duración esperada
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                self.msleep(100)  # 100ms entre capturas
            
            # Guardar archivo
            if self.audio_data:
                self._save_audio_file()
                self.recording_finished.emit(self.output_file)
            else:
                self.recording_error.emit("No se capturó audio")
                
        except Exception as e:
            self.recording_error.emit(f"Error en grabación: {str(e)}")
    
    def _save_audio_file(self):
        """Guarda el archivo de audio"""
        if not self.audio_data:
            raise Exception("No hay datos de audio para guardar")
        
        # Concatenar todos los chunks de audio
        audio_array = np.concatenate(self.audio_data, axis=0)
        
        if SOUNDFILE_AVAILABLE:
            # Usar soundfile para guardar
            sf.write(self.output_file, audio_array, self.sample_rate)
        else:
            # Implementación básica para WAV sin dependencias
            self._save_wav_basic(audio_array)
    
    def _save_wav_basic(self, audio_data):
        """Guarda WAV básico sin soundfile"""
        import struct
        import wave
        
        # Normalizar y convertir a 16-bit
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_16bit = (audio_data * 32767).astype(np.int16)
        
        with wave.open(self.output_file, 'wb') as wav_file:
            wav_file.setnchannels(2 if len(audio_16bit.shape) > 1 else 1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())

class RecordingControl(QGroupBox):
    """Control de grabación para timer y pomodoro"""
    
    recording_started = Signal()
    recording_stopped = Signal()
    
    def __init__(self, audio_engine):
        super().__init__("🎙️ Sistema de Grabación")
        self.audio_engine = audio_engine
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.timer_active = False
        self.pomodoro_active = False
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Configuración de grabación
        config_frame = QGroupBox("⚙️ Configuración")
        config_layout = QGridLayout(config_frame)
        
        # Formato de archivo
        config_layout.addWidget(QLabel("Formato:"), 0, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["WAV", "MP3", "FLAC"])
        self.format_combo.setCurrentText("WAV")
        config_layout.addWidget(self.format_combo, 0, 1)
        
        # Calidad/Bitrate
        config_layout.addWidget(QLabel("Calidad:"), 0, 2)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Estándar", "Alta", "Máxima"])
        config_layout.addWidget(self.quality_combo, 0, 3)
        
        # Directorio de salida
        config_layout.addWidget(QLabel("Carpeta:"), 1, 0)
        self.output_dir_label = QLabel("./recordings")
        self.output_dir_label.setStyleSheet("border: 1px solid #ccc; padding: 4px; background: #f9f9f9;")
        config_layout.addWidget(self.output_dir_label, 1, 1, 1, 2)
        
        self.browse_button = QPushButton("📁 Examinar")
        self.browse_button.clicked.connect(self.browse_output_dir)
        config_layout.addWidget(self.browse_button, 1, 3)
        
        layout.addWidget(config_frame)
        
        # Opciones de grabación automática
        auto_frame = QGroupBox("🤖 Grabación Automática")
        auto_layout = QVBoxLayout(auto_frame)
        
        self.auto_timer_checkbox = QCheckBox("📝 Grabar automáticamente durante Timer")
        self.auto_timer_checkbox.setChecked(True)
        auto_layout.addWidget(self.auto_timer_checkbox)
        
        self.auto_pomodoro_checkbox = QCheckBox("🍅 Grabar automáticamente durante Pomodoro")
        self.auto_pomodoro_checkbox.setChecked(True)
        auto_layout.addWidget(self.auto_pomodoro_checkbox)
        
        layout.addWidget(auto_frame)
        
        # Controles manuales
        manual_frame = QGroupBox("🎛️ Control Manual")
        manual_layout = QVBoxLayout(manual_frame)
        
        # Estado actual
        self.status_label = QLabel("🔴 No grabando")
        self.status_label.setStyleSheet("font-weight: bold; color: #dc3545; padding: 8px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        manual_layout.addWidget(self.status_label)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🎙️ Iniciar Grabación")
        self.stop_button = QPushButton("⏹ Detener Grabación")
        self.stop_button.setEnabled(False)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        
        manual_layout.addLayout(buttons_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        manual_layout.addWidget(self.progress_bar)
        
        # Información de archivo
        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        manual_layout.addWidget(self.file_info_label)
        
        layout.addWidget(manual_frame)
    
    def connect_signals(self):
        """Conecta señales de la interfaz y grabadora"""
        self.start_button.clicked.connect(self.start_manual_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        
        # Señales de la grabadora
        self.recorder.recording_progress.connect(self.update_progress)
        self.recorder.recording_finished.connect(self.on_recording_finished)
        self.recorder.recording_error.connect(self.on_recording_error)
    
    def browse_output_dir(self):
        """Selecciona directorio de salida"""
        directory = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta de Grabaciones"
        )
        if directory:
            self.output_dir_label.setText(directory)
    
    def start_manual_recording(self):
        """Inicia grabación manual"""
        self.start_recording("manual")
    
    def start_recording(self, session_type):
        """Inicia grabación"""
        if self.is_recording:
            return
        
        try:
            # Crear directorio si no existe
            output_dir = Path(self.output_dir_label.text())
            output_dir.mkdir(exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            format_ext = self.format_combo.currentText().lower()
            filename = f"{session_type}_{timestamp}.{format_ext}"
            output_file = output_dir / filename
            
            # Configurar callback de audio
            audio_callback = self.create_audio_callback()
            
            # Iniciar grabación
            expected_duration = 0  # 0 = duración indefinida para manual
            self.recorder.start_recording(str(output_file), format_ext, expected_duration, audio_callback)
            
            self.is_recording = True
            self.update_ui_recording_state(True)
            self.file_info_label.setText(f"Grabando: {filename}")
            self.recording_started.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar grabación: {str(e)}")
    
    def stop_recording(self):
        """Detiene grabación"""
        if not self.is_recording:
            return
        
        self.recorder.stop_recording()
        self.is_recording = False
        self.update_ui_recording_state(False)
        self.recording_stopped.emit()
    
    def create_audio_callback(self):
        """Crea callback para capturar audio del motor"""
        def audio_callback():
            if self.audio_engine and hasattr(self.audio_engine, 'audio_thread'):
                # Obtener buffer actual del hilo de audio
                thread = self.audio_engine.audio_thread
                if hasattr(thread, 'current_buffer'):
                    return thread.current_buffer.copy()
            return np.zeros((512, 2), dtype=np.float32)  # Silencio si no hay audio
        
        return audio_callback
    
    def update_ui_recording_state(self, recording):
        """Actualiza UI según estado de grabación"""
        if recording:
            self.status_label.setText("🔴 GRABANDO")
            self.status_label.setStyleSheet("font-weight: bold; color: #dc3545; padding: 8px; background-color: rgba(220, 53, 69, 0.1);")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setVisible(True)
        else:
            self.status_label.setText("🔴 No grabando")
            self.status_label.setStyleSheet("font-weight: bold; color: #6c757d; padding: 8px;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.progress_bar.setVisible(False)
    
    def update_progress(self, seconds):
        """Actualiza progreso de grabación"""
        minutes, secs = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        self.status_label.setText(f"🔴 GRABANDO - {time_str}")
    
    def on_recording_finished(self, output_file):
        """Maneja finalización de grabación"""
        self.update_ui_recording_state(False)
        file_size = Path(output_file).stat().st_size / (1024 * 1024)  # MB
        self.file_info_label.setText(f"✅ Guardado: {Path(output_file).name} ({file_size:.1f} MB)")
        
        QMessageBox.information(self, "Grabación Completa", 
                               f"Archivo guardado:{output_file}")
    
    def on_recording_error(self, error_msg):
        """Maneja errores de grabación"""
        self.update_ui_recording_state(False)
        self.file_info_label.setText(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Error de Grabación", error_msg)
    
    def on_timer_started(self):
        """Maneja inicio de timer"""
        self.timer_active = True
        if self.auto_timer_checkbox.isChecked() and not self.is_recording:
            self.start_recording("timer")
    
    def on_timer_stopped(self):
        """Maneja detención de timer"""
        self.timer_active = False
        if self.is_recording and self.auto_timer_checkbox.isChecked():
            self.stop_recording()
    
    def on_pomodoro_started(self):
        """Maneja inicio de pomodoro"""
        self.pomodoro_active = True
        if self.auto_pomodoro_checkbox.isChecked() and not self.is_recording:
            self.start_recording("pomodoro")
    
    def on_pomodoro_stopped(self):
        """Maneja detención de pomodoro"""
        self.pomodoro_active = False
        if self.is_recording and self.auto_pomodoro_checkbox.isChecked():
            self.stop_recording()
