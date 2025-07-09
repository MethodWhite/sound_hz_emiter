#!/usr/bin/env python3
"""
Generador Sound Hz Emitter v2.0 - Compatible con Windows
Soluciona problemas de codificación de caracteres
"""

import os
import sys
from pathlib import Path

def print_header():
    print("Sound Hz Emitter v2.0 - Generador")
    print("=" * 40)

def crear_directorios():
    """Crea la estructura de directorios"""
    dirs = ["config", "core", "ui", "ui/components", "ui/styles", "utils", "tests"]
    
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Crear __init__.py
        init_file = Path(directory) / "__init__.py"
        init_file.write_text("# Paquete Python\n", encoding='utf-8')
        print(f"Carpeta: {directory}/")

def crear_main_py():
    """Crea main.py principal"""
    content = '''#!/usr/bin/env python3
"""Sound Hz Emitter - Aplicacion principal"""

import sys
import os
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

def verificar_dependencias():
    """Verifica que las dependencias esten disponibles"""
    faltantes = []
    
    try:
        import PySide6
        print("PySide6: OK")
    except ImportError:
        print("PySide6: NO DISPONIBLE")
        faltantes.append("PySide6")
        return False, faltantes
    
    try:
        import numpy
        print("NumPy: OK")
    except ImportError:
        print("NumPy: No disponible (funcionalidad limitada)")
        faltantes.append("numpy")
    
    try:
        import sounddevice
        print("SoundDevice: OK")
    except ImportError:
        print("SoundDevice: No disponible (audio simulado)")
        faltantes.append("sounddevice")
    
    return True, faltantes

def main():
    print("=== Sound Hz Emitter v2.0 ===")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("Error: Se requiere Python 3.8 o superior")
        return 1
    
    # Verificar dependencias
    deps_ok, faltantes = verificar_dependencias()
    
    if not deps_ok:
        print("\\nError: PySide6 es requerido")
        print("Instala con: pip install PySide6")
        return 1
    
    # Crear aplicacion Qt
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        app = QApplication(sys.argv)
        app.setApplicationName("Sound Hz Emitter")
        app.setStyle('Fusion')
        
        # Crear directorios si no existen
        for d in ['config', 'ui']:
            os.makedirs(d, exist_ok=True)
            init_path = Path(d) / '__init__.py'
            if not init_path.exists():
                init_path.write_text('# Paquete Python\\n', encoding='utf-8')
        
        # Cargar ventana principal
        try:
            from ui.ventana_principal import VentanaPrincipal
            ventana = VentanaPrincipal()
            
            # Mostrar advertencia si faltan dependencias
            if faltantes:
                from PySide6.QtWidgets import QMessageBox
                deps_texto = ", ".join(faltantes)
                QMessageBox.information(
                    ventana, "Dependencias", 
                    f"Dependencias opcionales no encontradas: {deps_texto}\\n"
                    f"La aplicacion funcionara en modo basico.\\n\\n"
                    f"Para funcionalidad completa instala:\\n"
                    f"pip install {' '.join(faltantes)}"
                )
            
            ventana.show()
            return app.exec()
            
        except ImportError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None, "Error", 
                f"No se pudo cargar la interfaz: {e}\\n\\n"
                f"Verifica que el archivo ui/ventana_principal.py exista."
            )
            return 1
    
    except ImportError:
        print("\\nError: PySide6 no esta instalado")
        print("Instala con: pip install PySide6")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    Path("main.py").write_text(content, encoding='utf-8')
    print("Archivo: main.py")

def crear_ventana_principal():
    """Crea la ventana principal"""
    content = '''"""Ventana principal de la aplicacion Sound Hz Emitter"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QSlider, QComboBox, QCheckBox,
    QFrame, QGroupBox, QStatusBar, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

class MotorAudioBasico:
    """Motor de audio basico para simulacion"""
    
    def __init__(self):
        self.tonos_activos = {}
        self.reproduciendo = False
        
    def iniciar(self):
        """Inicia la reproduccion de audio"""
        print("Audio iniciado (modo simulacion)")
        self.reproduciendo = True
        return True
        
    def detener(self):
        """Detiene la reproduccion de audio"""
        print("Audio detenido")
        self.reproduciendo = False
        
    def agregar_tono(self, id_tono, frecuencia, volumen, tipo_onda="seno"):
        """Agrega un nuevo tono"""
        self.tonos_activos[id_tono] = {
            'frecuencia': frecuencia,
            'volumen': volumen,
            'tipo_onda': tipo_onda,
            'activo': True
        }
        print(f"Tono agregado - ID: {id_tono}, Freq: {frecuencia} Hz, Vol: {volumen}")
        return True
        
    def eliminar_tono(self, id_tono):
        """Elimina un tono"""
        if id_tono in self.tonos_activos:
            del self.tonos_activos[id_tono]
            print(f"Tono {id_tono} eliminado")
            
    def actualizar_tono(self, id_tono, **parametros):
        """Actualiza los parametros de un tono"""
        if id_tono in self.tonos_activos:
            self.tonos_activos[id_tono].update(parametros)
            print(f"Tono {id_tono} actualizado")

class ControlTono(QFrame):
    """Widget para controlar un tono individual"""
    
    # Senales para comunicacion
    tono_modificado = Signal(int, dict)
    tono_eliminado = Signal(int)
    
    def __init__(self, id_tono, frecuencia_inicial=440):
        super().__init__()
        self.id_tono = id_tono
        self.configurar_interfaz(frecuencia_inicial)
        
    def configurar_interfaz(self, frecuencia_inicial):
        """Configura la interfaz del control de tono"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Cabecera con titulo y boton eliminar
        cabecera = QHBoxLayout()
        
        titulo = QLabel(f"Tono {self.id_tono}")
        titulo.setStyleSheet("font-weight: bold; font-size: 12px; color: #0078d4;")
        cabecera.addWidget(titulo)
        
        cabecera.addStretch()
        
        btn_eliminar = QPushButton("X")
        btn_eliminar.setMaximumSize(25, 25)
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.tono_eliminado.emit(self.id_tono))
        cabecera.addWidget(btn_eliminar)
        
        layout.addLayout(cabecera)
        
        # Controles principales en fila
        controles = QHBoxLayout()
        
        # Control de frecuencia
        grupo_freq = QVBoxLayout()
        etiqueta_freq = QLabel("Frecuencia")
        etiqueta_freq.setStyleSheet("font-weight: bold; font-size: 10px;")
        grupo_freq.addWidget(etiqueta_freq)
        
        self.spin_frecuencia = QSpinBox()
        self.spin_frecuencia.setRange(20, 20000)
        self.spin_frecuencia.setValue(frecuencia_inicial)
        self.spin_frecuencia.setSuffix(" Hz")
        self.spin_frecuencia.setMinimumWidth(80)
        self.spin_frecuencia.valueChanged.connect(self.emitir_cambios)
        grupo_freq.addWidget(self.spin_frecuencia)
        
        controles.addLayout(grupo_freq)
        
        # Control de volumen
        grupo_vol = QVBoxLayout()
        etiqueta_vol = QLabel("Volumen")
        etiqueta_vol.setStyleSheet("font-weight: bold; font-size: 10px;")
        grupo_vol.addWidget(etiqueta_vol)
        
        self.slider_volumen = QSlider(Qt.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(50)
        self.slider_volumen.setMinimumWidth(80)
        self.slider_volumen.valueChanged.connect(self.emitir_cambios)
        grupo_vol.addWidget(self.slider_volumen)
        
        self.etiqueta_volumen = QLabel("50%")
        self.etiqueta_volumen.setAlignment(Qt.AlignCenter)
        self.etiqueta_volumen.setStyleSheet("font-size: 9px;")
        grupo_vol.addWidget(self.etiqueta_volumen)
        
        controles.addLayout(grupo_vol)
        
        # Selector de tipo de onda
        grupo_onda = QVBoxLayout()
        etiqueta_onda = QLabel("Tipo de Onda")
        etiqueta_onda.setStyleSheet("font-weight: bold; font-size: 10px;")
        grupo_onda.addWidget(etiqueta_onda)
        
        self.combo_onda = QComboBox()
        self.combo_onda.addItems(["Seno", "Cuadrada", "Triangular", "Sierra"])
        self.combo_onda.setMinimumWidth(90)
        self.combo_onda.currentTextChanged.connect(self.emitir_cambios)
        grupo_onda.addWidget(self.combo_onda)
        
        controles.addLayout(grupo_onda)
        
        layout.addLayout(controles)
        
        # Checkbox para activar/desactivar
        self.check_activo = QCheckBox("Tono Activo")
        self.check_activo.setChecked(True)
        self.check_activo.setStyleSheet("font-weight: bold; color: #28a745;")
        self.check_activo.toggled.connect(self.emitir_cambios)
        layout.addWidget(self.check_activo)
        
        # Estilo del frame
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
    def emitir_cambios(self):
        """Emite los cambios realizados en el control"""
        # Actualizar etiqueta de volumen
        volumen_porcentaje = self.slider_volumen.value()
        self.etiqueta_volumen.setText(f"{volumen_porcentaje}%")
        
        # Crear diccionario con configuracion
        configuracion = {
            'frecuencia': self.spin_frecuencia.value(),
            'volumen': volumen_porcentaje / 100.0,
            'tipo_onda': self.combo_onda.currentText().lower(),
            'activo': self.check_activo.isChecked()
        }
        
        # Emitir senal
        self.tono_modificado.emit(self.id_tono, configuracion)

class ControlTemporizador(QFrame):
    """Widget para control del temporizador"""
    
    temporizador_iniciado = Signal()
    temporizador_detenido = Signal()
    temporizador_finalizado = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Configuracion del temporizador
        self.timer_qt = QTimer()
        self.timer_qt.timeout.connect(self.actualizar_display)
        self.tiempo_restante_segundos = 0
        self.tiempo_total_segundos = 0
        
        self.configurar_interfaz()
        
    def configurar_interfaz(self):
        """Configura la interfaz del temporizador"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Titulo
        titulo = QLabel("Temporizador de Sesion")
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
        
        # Configuracion del tiempo
        config_tiempo = QHBoxLayout()
        
        # Minutos
        config_tiempo.addWidget(QLabel("Minutos:"))
        self.spin_minutos = QSpinBox()
        self.spin_minutos.setRange(0, 999)
        self.spin_minutos.setValue(5)
        self.spin_minutos.setMinimumWidth(60)
        config_tiempo.addWidget(self.spin_minutos)
        
        # Segundos
        config_tiempo.addWidget(QLabel("Segundos:"))
        self.spin_segundos = QSpinBox()
        self.spin_segundos.setRange(0, 59)
        self.spin_segundos.setValue(0)
        self.spin_segundos.setMinimumWidth(60)
        config_tiempo.addWidget(self.spin_segundos)
        
        layout.addLayout(config_tiempo)
        
        # Display digital del tiempo
        self.display_tiempo = QLabel("05:00")
        self.display_tiempo.setAlignment(Qt.AlignCenter)
        self.display_tiempo.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', 'Monaco', monospace;
                font-size: 28px;
                font-weight: bold;
                color: #6f42c1;
                background-color: #f8f9fa;
                border: 3px solid #6f42c1;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        layout.addWidget(self.display_tiempo)
        
        # Botones de control
        botones = QHBoxLayout()
        
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_iniciar.clicked.connect(self.iniciar_temporizador)
        botones.addWidget(self.btn_iniciar)
        
        self.btn_detener = QPushButton("Detener")
        self.btn_detener.setEnabled(False)
        self.btn_detener.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
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
        
        # Estado del temporizador
        self.etiqueta_estado = QLabel("Listo para iniciar")
        self.etiqueta_estado.setAlignment(Qt.AlignCenter)
        self.etiqueta_estado.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.etiqueta_estado)
        
        # Estilo del frame
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #6f42c1;
                border-radius: 10px;
                background-color: white;
            }
        """)
        
    def iniciar_temporizador(self):
        """Inicia el temporizador"""
        # Calcular tiempo total en segundos
        minutos = self.spin_minutos.value()
        segundos = self.spin_segundos.value()
        tiempo_total = minutos * 60 + segundos
        
        if tiempo_total <= 0:
            QMessageBox.warning(self, "Error", "Por favor configura un tiempo mayor a 0")
            return
        
        # Configurar temporizador
        self.tiempo_total_segundos = tiempo_total
        self.tiempo_restante_segundos = tiempo_total
        
        # Iniciar timer de Qt
        self.timer_qt.start(1000)  # Actualizar cada segundo
        
        # Actualizar interfaz
        self.btn_iniciar.setText("Pausar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.pausar_temporizador)
        
        self.btn_detener.setEnabled(True)
        self.spin_minutos.setEnabled(False)
        self.spin_segundos.setEnabled(False)
        self.etiqueta_estado.setText("Temporizador en ejecucion...")
        
        # Emitir senal
        self.temporizador_iniciado.emit()
        
    def pausar_temporizador(self):
        """Pausa el temporizador"""
        self.timer_qt.stop()
        
        self.btn_iniciar.setText("Continuar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.continuar_temporizador)
        
        self.etiqueta_estado.setText("Temporizador pausado")
        
    def continuar_temporizador(self):
        """Continua el temporizador"""
        self.timer_qt.start(1000)
        
        self.btn_iniciar.setText("Pausar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.pausar_temporizador)
        
        self.etiqueta_estado.setText("Temporizador en ejecucion...")
        
    def detener_temporizador(self):
        """Detiene completamente el temporizador"""
        self.timer_qt.stop()
        
        # Resetear interfaz
        self.btn_iniciar.setText("Iniciar")
        self.btn_iniciar.clicked.disconnect()
        self.btn_iniciar.clicked.connect(self.iniciar_temporizador)
        
        self.btn_detener.setEnabled(False)
        self.spin_minutos.setEnabled(True)
        self.spin_segundos.setEnabled(True)
        self.etiqueta_estado.setText("Temporizador detenido")
        
        # Emitir senal
        self.temporizador_detenido.emit()
        
    def actualizar_display(self):
        """Actualiza el display del tiempo restante"""
        self.tiempo_restante_segundos -= 1
        
        if self.tiempo_restante_segundos <= 0:
            # Tiempo completado
            self.detener_temporizador()
            self.etiqueta_estado.setText("Tiempo completado!")
            
            # Mostrar mensaje
            QMessageBox.information(self, "Temporizador", "El tiempo configurado ha terminado!")
            
            # Emitir senal de finalizacion
            self.temporizador_finalizado.emit()
            return
        
        # Convertir segundos a formato MM:SS
        minutos = self.tiempo_restante_segundos // 60
        segundos = self.tiempo_restante_segundos % 60
        tiempo_formateado = f"{minutos:02d}:{segundos:02d}"
        
        self.display_tiempo.setText(tiempo_formateado)

class VentanaPrincipal(QMainWindow):
    """Ventana principal de la aplicacion Sound Hz Emitter"""
    
    def __init__(self):
        super().__init__()
        
        # Configuracion de la ventana
        self.setWindowTitle("Sound Hz Emitter v2.0 - Generador de Frecuencias")
        self.setGeometry(100, 100, 1100, 700)
        self.setMinimumSize(900, 600)
        
        # Motor de audio
        self.motor_audio = MotorAudioBasico()
        
        # Control de tonos
        self.controles_tonos = {}
        self.siguiente_id_tono = 1
        
        # Configurar interfaz
        self.configurar_interfaz()
        
        # Agregar tono inicial
        self.agregar_nuevo_tono()
        
    def configurar_interfaz(self):
        """Configura toda la interfaz de usuario"""
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal horizontal
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(10, 10, 10, 10)
        layout_principal.setSpacing(15)
        
        # Panel izquierdo - Controles
        self.crear_panel_controles(layout_principal)
        
        # Panel derecho - Informacion
        self.crear_panel_informacion(layout_principal)
        
        # Barra de estado
        self.barra_estado = QStatusBar()
        self.setStatusBar(self.barra_estado)
        self.barra_estado.showMessage("Sound Hz Emitter v2.0 - Listo para usar")
        
    def crear_panel_controles(self, layout_padre):
        """Crea el panel izquierdo con controles"""
        panel_controles = QWidget()
        layout_controles = QVBoxLayout(panel_controles)
        layout_controles.setSpacing(15)
        
        # Control del temporizador
        self.control_temporizador = ControlTemporizador()
        self.control_temporizador.temporizador_iniciado.connect(self.al_iniciar_temporizador)
        self.control_temporizador.temporizador_detenido.connect(self.al_detener_temporizador)
        self.control_temporizador.temporizador_finalizado.connect(self.al_finalizar_temporizador)
        layout_controles.addWidget(self.control_temporizador)
        
        # Grupo de control de tonos
        grupo_tonos = QGroupBox("Control de Tonos")
        grupo_tonos.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #0078d4;
                border: 2px solid #0078d4;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        layout_grupo_tonos = QVBoxLayout(grupo_tonos)
        
        # Boton para agregar tonos
        btn_agregar_tono = QPushButton("Agregar Nuevo Tono")
        btn_agregar_tono.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        btn_agregar_tono.clicked.connect(self.agregar_nuevo_tono)
        layout_grupo_tonos.addWidget(btn_agregar_tono)
        
        # Contenedor scrolleable para controles de tonos
        self.widget_contenedor_tonos = QWidget()
        self.layout_tonos = QVBoxLayout(self.widget_contenedor_tonos)
        self.layout_tonos.setSpacing(10)
        layout_grupo_tonos.addWidget(self.widget_contenedor_tonos)
        
        layout_controles.addWidget(grupo_tonos)
        
        # Controles globales de audio
        grupo_audio = QGroupBox("Controles de Audio")
        grupo_audio.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #28a745;
                border: 2px solid #28a745;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        layout_audio = QHBoxLayout(grupo_audio)
        
        self.btn_audio_global = QPushButton("Iniciar Audio")
        self.btn_audio_global.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_audio_global.clicked.connect(self.alternar_audio_global)
        layout_audio.addWidget(self.btn_audio_global)
        
        btn_limpiar_tonos = QPushButton("Eliminar Todos")
        btn_limpiar_tonos.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_limpiar_tonos.clicked.connect(self.eliminar_todos_los_tonos)
        layout_audio.addWidget(btn_limpiar_tonos)
        
        layout_controles.addWidget(grupo_audio)
        layout_controles.addStretch()
        
        layout_padre.addWidget(panel_controles, 2)  # 2/3 del espacio
        
    def crear_panel_informacion(self, layout_padre):
        """Crea el panel derecho con informacion"""
        panel_info = QWidget()
        layout_info = QVBoxLayout(panel_info)
        
        # Informacion de la aplicacion
        grupo_info = QGroupBox("Informacion de la Aplicacion")
        grupo_info.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #6f42c1;
                border: 2px solid #6f42c1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        layout_grupo_info = QVBoxLayout(grupo_info)
        
        texto_informativo = QTextEdit()
        texto_informativo.setReadOnly(True)
        texto_informativo.setMaximumHeight(300)
        contenido_info = """
<h2>Sound Hz Emitter v2.0</h2>
<p><b>Generador Profesional de Frecuencias de Sonido</b></p>

<h3>Como usar:</h3>
<ol>
<li><b>Agregar Tonos:</b> Usa el boton "Agregar Nuevo Tono"</li>
<li><b>Configurar Frecuencias:</b> Ajusta entre 20 y 20,000 Hz</li>
<li><b>Controlar Volumen:</b> Usa los sliders (0-100%)</li>
<li><b>Seleccionar Tipo de Onda:</b> Seno, Cuadrada, Triangular, Sierra</li>
<li><b>Activar/Desactivar:</b> Usa los checkboxes individuales</li>
<li><b>Iniciar Audio:</b> Presiona "Iniciar Audio"</li>
<li><b>Usar Temporizador:</b> Para sesiones con duracion especifica</li>
</ol>

<h3>Tipos de Onda:</h3>
<ul>
<li><b>Seno:</b> Tono puro y suave, ideal para relajacion</li>
<li><b>Cuadrada:</b> Sonido mas fuerte y aspero</li>
<li><b>Triangular:</b> Sonido intermedio entre seno y cuadrada</li>
<li><b>Sierra:</b> Sonido brillante con armonicos</li>
</ul>

<h3>Estado Actual:</h3>
<p><b>Modo:</b> Basico (Simulacion)</p>
<p><b>Audio:</b> Para audio real, instala: <code>pip install sounddevice</code></p>
        """
        texto_informativo.setHtml(contenido_info)
        layout_grupo_info.addWidget(texto_informativo)
        
        layout_info.addWidget(grupo_info)
        
        # Estadisticas
        grupo_stats = QGroupBox("Estadisticas")
        grupo_stats.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #fd7e14;
                border: 2px solid #fd7e14;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        layout_stats = QVBoxLayout(grupo_stats)
        
        self.etiqueta_stats = QLabel("Tonos configurados: 0\\nTonos activos: 0")
        self.etiqueta_stats.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 10px;
                background-color: #fff3cd;
                border-radius: 5px;
            }
        """)
        layout_stats.addWidget(self.etiqueta_stats)
        
        layout_info.addWidget(grupo_stats)
        layout_info.addStretch()
        
        layout_padre.addWidget(panel_info, 1)  # 1/3 del espacio
        
    def agregar_nuevo_tono(self):
        """Agrega un nuevo control de tono"""
        id_tono = self.siguiente_id_tono
        self.siguiente_id_tono += 1
        
        # Crear control de tono
        control_tono = ControlTono(id_tono)
        control_tono.tono_modificado.connect(self.al_modificar_tono)
        control_tono.tono_eliminado.connect(self.eliminar_tono)
        
        # Agregar a la interfaz
        self.layout_tonos.addWidget(control_tono)
        self.controles_tonos[id_tono] = control_tono
        
        # Agregar al motor de audio
        self.motor_audio.agregar_tono(id_tono, 440, 0.5)
        
        # Actualizar estadisticas
        self.actualizar_estadisticas()
        
        # Actualizar barra de estado
        self.barra_estado.showMessage(f"Tono {id_tono} agregado - Total: {len(self.controles_tonos)}")
        
    def eliminar_tono(self, id_tono):
        """Elimina un tono especifico"""
        if id_tono in self.controles_tonos:
            # Eliminar de la interfaz
            control = self.controles_tonos[id_tono]
            self.layout_tonos.removeWidget(control)
            control.deleteLater()
            del self.controles_tonos[id_tono]
            
            # Eliminar del motor de audio
            self.motor_audio.eliminar_tono(id_tono)
            
            # Actualizar estadisticas
            self.actualizar_estadisticas()
            
            # Actualizar barra de estado
            self.barra_estado.showMessage(f"Tono {id_tono} eliminado - Total: {len(self.controles_tonos)}")
            
    def eliminar_todos_los_tonos(self):
        """Elimina todos los tonos"""
        # Confirmar accion
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            "¿Estas seguro de que quieres eliminar todos los tonos?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            # Eliminar todos los tonos
            ids_tonos = list(self.controles_tonos.keys())
            for id_tono in ids_tonos:
                self.eliminar_tono(id_tono)
                
            self.barra_estado.showMessage("Todos los tonos eliminados")
            
    def al_modificar_tono(self, id_tono, configuracion):
        """Maneja la modificacion de un tono"""
        # Actualizar motor de audio
        self.motor_audio.actualizar_tono(id_tono, **configuracion)
        
        # Actualizar estadisticas
        self.actualizar_estadisticas()
        
        # Mensaje en barra de estado
        freq = configuracion['frecuencia']
        vol = int(configuracion['volumen'] * 100)
        self.barra_estado.showMessage(f"Tono {id_tono}: {freq} Hz, {vol}%")
        
    def al_iniciar_temporizador(self):
        """Maneja el inicio del temporizador"""
        # Iniciar audio automaticamente si no esta activo
        if not self.motor_audio.reproduciendo:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("Detener Audio")
            
        self.barra_estado.showMessage("Temporizador iniciado - Audio activo")
        
    def al_detener_temporizador(self):
        """Maneja la detencion del temporizador"""
        self.barra_estado.showMessage("Temporizador detenido")
        
    def al_finalizar_temporizador(self):
        """Maneja la finalizacion del temporizador"""
        self.barra_estado.showMessage("Sesion completada - Temporizador finalizado")
        
    def alternar_audio_global(self):
        """Alterna el estado global del audio"""
        if self.motor_audio.reproduciendo:
            self.motor_audio.detener()
            self.btn_audio_global.setText("Iniciar Audio")
            self.barra_estado.showMessage("Audio detenido")
        else:
            self.motor_audio.iniciar()
            self.btn_audio_global.setText("Detener Audio")
            self.barra_estado.showMessage("Audio iniciado")
            
    def actualizar_estadisticas(self):
        """Actualiza las estadisticas mostradas"""
        total_tonos = len(self.controles_tonos)
        tonos_activos = sum(1 for control in self.controles_tonos.values() 
                           if control.check_activo.isChecked())
        
        self.etiqueta_stats.setText(
            f"Tonos configurados: {total_tonos}\\n"
            f"Tonos activos: {tonos_activos}"
        )
        
    def closeEvent(self, event):
        """Maneja el cierre de la aplicacion"""
        # Detener audio y temporizador
        self.motor_audio.detener()
        if hasattr(self, 'control_temporizador'):
            self.control_temporizador.timer_qt.stop()
            
        print("Sound Hz Emitter cerrado correctamente")
        event.accept()
'''
    
    Path("ui/ventana_principal.py").write_text(content, encoding='utf-8')
    print("Archivo: ui/ventana_principal.py")

def crear_archivos_extra():
    """Crea archivos adicionales"""
    
    # requirements.txt
    req_content = '''# Sound Hz Emitter v2.0 - Lista de Dependencias

# OBLIGATORIO - Interfaz grafica
PySide6>=6.5.0

# RECOMENDADO - Audio real y calculos matematicos  
numpy>=1.21.0
sounddevice>=0.4.6
scipy>=1.9.0

# OPCIONAL - Visualizacion avanzada
pyqtgraph>=0.13.3

# DESARROLLO - Herramientas de desarrollo
pytest>=7.0.0
black>=22.0.0
isort>=5.10.0
'''
    
    Path("requirements.txt").write_text(req_content, encoding='utf-8')
    print("Archivo: requirements.txt")
    
    # install.py
    install_content = '''#!/usr/bin/env python3
"""
Instalador automatico para Sound Hz Emitter v2.0
Instala todas las dependencias necesarias
"""

import subprocess
import sys
import os

def mostrar_banner():
    print("=" * 50)
    print("  INSTALADOR SOUND HZ EMITTER v2.0")
    print("=" * 50)
    print()

def instalar_dependencia(nombre_paquete, descripcion, obligatorio=False):
    """Instala una dependencia especifica"""
    print(f"Instalando {nombre_paquete} - {descripcion}")
    
    try:
        # Intentar instalacion
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", nombre_paquete],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if resultado.returncode == 0:
            print(f"  -> {nombre_paquete} instalado correctamente")
            return True
        else:
            print(f"  -> Error instalando {nombre_paquete}: {resultado.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  -> Timeout instalando {nombre_paquete}")
        return False
    except Exception as e:
        print(f"  -> Excepcion instalando {nombre_paquete}: {e}")
        return False

def verificar_instalacion():
    """Verifica que las dependencias esten instaladas"""
    print("\\nVerificando instalacion...")
    
    dependencias = [
        ("PySide6", "Interfaz grafica"),
        ("numpy", "Calculos matematicos"),
        ("sounddevice", "Audio en tiempo real"),
        ("scipy", "Procesamiento de senales"),
    ]
    
    instaladas = 0
    
    for paquete, descripcion in dependencias:
        try:
            __import__(paquete)
            print(f"  {paquete}: OK")
            instaladas += 1
        except ImportError:
            print(f"  {paquete}: NO DISPONIBLE")
    
    return instaladas, len(dependencias)

def main():
    """Funcion principal del instalador"""
    mostrar_banner()
    
    print("Este instalador configurara Sound Hz Emitter v2.0")
    print("Se instalaran las siguientes dependencias:")
    print("  - PySide6 (OBLIGATORIO): Interfaz grafica")
    print("  - numpy (RECOMENDADO): Calculos matematicos")
    print("  - sounddevice (RECOMENDADO): Audio real")
    print("  - scipy (OPCIONAL): Procesamiento avanzado")
    print()
    
    continuar = input("¿Continuar con la instalacion? (s/n): ").lower()
    if continuar not in ['s', 'si', 'y', 'yes', '']:
        print("Instalacion cancelada")
        return
    
    print("\\nIniciando instalacion...")
    print("-" * 30)
    
    # Lista de dependencias a instalar
    dependencias = [
        ("PySide6", "Interfaz grafica (OBLIGATORIO)", True),
        ("numpy", "Calculos matematicos", False),
        ("sounddevice", "Audio en tiempo real", False),
        ("scipy", "Procesamiento de senales", False),
    ]
    
    instalaciones_exitosas = 0
    
    for paquete, descripcion, obligatorio in dependencias:
        exito = instalar_dependencia(paquete, descripcion, obligatorio)
        if exito:
            instalaciones_exitosas += 1
        elif obligatorio:
            print(f"\\nERROR: {paquete} es obligatorio y no se pudo instalar")
            print("La aplicacion no funcionara sin esta dependencia")
            return
    
    # Verificar instalacion
    instaladas, total = verificar_instalacion()
    
    print("\\n" + "=" * 50)
    print("  RESUMEN DE INSTALACION")
    print("=" * 50)
    
    if instaladas >= 1:  # Al menos PySide6
        print(f"EXITO: {instaladas}/{total} dependencias instaladas")
        print()
        print("Sound Hz Emitter esta listo para usar!")
        print()
        print("Para ejecutar la aplicacion:")
        print("  python main.py")
        print()
        
        if instaladas < total:
            print("NOTA: Algunas dependencias opcionales no se instalaron.")
            print("La aplicacion funcionara en modo basico.")
            print("Para funcionalidad completa, instala manualmente:")
            print("  pip install numpy sounddevice scipy")
    else:
        print("ERROR: No se pudieron instalar las dependencias criticas")
        print("Intenta instalar manualmente:")
        print("  pip install PySide6")
    
    print()
    input("Presiona Enter para finalizar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\nInstalacion interrumpida por el usuario")
    except Exception as e:
        print(f"\\n\\nError inesperado: {e}")
'''
    
    Path("install.py").write_text(install_content, encoding='utf-8')
    print("Archivo: install.py")
    
    # README.md
    readme_content = '''# Sound Hz Emitter v2.0

Generador profesional de frecuencias de sonido desarrollado con PySide6.

## Instalacion Rapida

### Opcion 1: Instalador Automatico
```bash
python install.py
```

### Opcion 2: Instalacion Manual
```bash
pip install PySide6 numpy sounddevice scipy
```

### Ejecutar la Aplicacion
```bash
python main.py
```

## Caracteristicas

- **Generacion de tonos multiples**: Hasta 10 tonos simultaneos
- **Tipos de onda variados**: Seno, cuadrada, triangular, sierra
- **Control de frecuencia**: Rango de 20 Hz a 20,000 Hz
- **Control de volumen**: Ajuste fino de 0% a 100%
- **Temporizador integrado**: Para sesiones de duracion especifica
- **Interfaz intuitiva**: Controles faciles de usar
- **Modo simulacion**: Funciona sin hardware de audio

## Casos de Uso

- **Terapia de sonido**: Frecuencias curativas y relajantes
- **Entrenamiento musical**: Afinacion de instrumentos
- **Investigacion cientifica**: Estudios psicoacusticos
- **Aplicaciones medicas**: Audiometria y terapia auditiva
- **Meditacion**: Generacion de tonos binaurales

## Requisitos del Sistema

- Python 3.8 o superior
- Windows, macOS, o Linux
- PySide6 (instalacion automatica)
- Dependencias opcionales: numpy, sounddevice, scipy

## Solucion de Problemas

### Error: "No module named 'PySide6'"
```bash
pip install PySide6
```

### La aplicacion no reproduce sonido
- Instala sounddevice: `pip install sounddevice`
- Verifica que tu dispositivo de audio funcione
- La aplicacion funciona en modo simulacion sin audio real

### Error de codificacion en Windows
- Asegurate de usar Python 3.8 o superior
- El generador maneja automaticamente la codificacion UTF-8

## Como Usar

1. **Ejecutar**: `python main.py`
2. **Agregar tonos**: Usar boton "Agregar Nuevo Tono"
3. **Configurar frecuencias**: Ajustar valor en Hz (20-20000)
4. **Controlar volumen**: Usar sliders (0-100%)
5. **Seleccionar tipo de onda**: Elegir entre opciones disponibles
6. **Activar tonos**: Usar checkboxes individuales
7. **Iniciar audio**: Presionar "Iniciar Audio"
8. **Usar temporizador**: Para sesiones programadas

## Estructura del Proyecto

```
sound_hz_emitter/
├── main.py                    # Aplicacion principal
├── install.py                 # Instalador automatico
├── requirements.txt           # Lista de dependencias
├── README.md                  # Este archivo
├── ui/
│   └── ventana_principal.py   # Interfaz grafica
├── config/                    # Configuraciones
├── core/                      # Logica principal
├── utils/                     # Utilidades
└── tests/                     # Pruebas
```

## Desarrollo

Para contribuir al proyecto:

1. Clona el repositorio
2. Instala dependencias de desarrollo: `pip install -r requirements.txt`
3. Realiza tus cambios
4. Ejecuta pruebas: `python -m pytest tests/`
5. Envia un pull request

## Licencia

Este proyecto se distribuye bajo licencia MIT.

## Soporte

¿Problemas? ¿Sugerencias?
- Reporta issues en el repositorio
- Incluye informacion del sistema y mensaje de error completo

---

**¡Disfruta generando frecuencias de sonido profesionales!**
'''
    
    Path("README.md").write_text(readme_content, encoding='utf-8')
    print("Archivo: README.md")

def crear_lanzadores():
    """Crea scripts de lanzamiento"""
    
    # Lanzador para Windows (.bat)
    bat_content = '''@echo off
title Sound Hz Emitter v2.0
color 0B

echo.
echo ================================================
echo            SOUND HZ EMITTER v2.0
echo        Generador de Frecuencias de Sonido
echo ================================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Iniciando Sound Hz Emitter...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: No se pudo ejecutar la aplicacion
    echo ================================================
    echo.
    echo Posibles soluciones:
    echo 1. Instalar dependencias: python install.py
    echo 2. Instalar PySide6: pip install PySide6
    echo 3. Verificar que todos los archivos esten presentes
    echo.
    pause
) else (
    echo.
    echo Aplicacion cerrada correctamente.
)
'''
    
    Path("ejecutar.bat").write_text(bat_content, encoding='utf-8')
    print("Archivo: ejecutar.bat")
    
    # Lanzador para Unix/Linux/macOS (.sh)
    sh_content = '''#!/bin/bash

# Sound Hz Emitter v2.0 - Lanzador para Unix/Linux/macOS

clear
echo "================================================"
echo "            SOUND HZ EMITTER v2.0"
echo "        Generador de Frecuencias de Sonido"
echo "================================================"
echo ""

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Verificar Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no esta instalado"
    echo ""
    echo "Instala Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo "  Arch: sudo pacman -S python python-pip"
    echo ""
    read -p "Presiona Enter para continuar..."
    exit 1
fi

echo "Iniciando Sound Hz Emitter..."
echo ""

# Ejecutar aplicacion
if python3 main.py; then
    echo ""
    echo "Aplicacion cerrada correctamente."
else
    echo ""
    echo "================================================"
    echo "ERROR: No se pudo ejecutar la aplicacion"
    echo "================================================"
    echo ""
    echo "Posibles soluciones:"
    echo "1. Instalar dependencias: python3 install.py"
    echo "2. Instalar PySide6: pip3 install PySide6"
    echo "3. Verificar que todos los archivos esten presentes"
    echo ""
    read -p "Presiona Enter para continuar..."
fi
'''
    
    Path("ejecutar.sh").write_text(sh_content, encoding='utf-8')
    
    # Hacer ejecutable en sistemas Unix
    try:
        Path("ejecutar.sh").chmod(0o755)
    except:
        pass  # No es critico si falla en Windows
    
    print("Archivo: ejecutar.sh")

def main():
    """Funcion principal del generador"""
    print_header()
    
    directorio_actual = Path.cwd()
    print(f"Directorio: {directorio_actual}")
    print()
    
    respuesta = input("¿Crear proyecto aqui? (s/n): ").lower()
    if respuesta not in ['s', 'si', 'y', 'yes', '']:
        print("Operacion cancelada")
        return
    
    print()
    print("Creando proyecto...")
    print("-" * 25)
    
    try:
        crear_directorios()
        crear_main_py()
        crear_ventana_principal()
        crear_archivos_extra()
        crear_lanzadores()
        
        print()
        print("=" * 45)
        print("PROYECTO CREADO EXITOSAMENTE!")
        print("=" * 45)
        print()
        print("Archivos creados:")
        print("  main.py - Aplicacion principal")
        print("  ui/ventana_principal.py - Interfaz grafica")
        print("  install.py - Instalador automatico")
        print("  ejecutar.bat - Lanzador Windows")
        print("  ejecutar.sh - Lanzador Linux/macOS")
        print("  requirements.txt - Dependencias")
        print("  README.md - Documentacion")
        print()
        print("Proximos pasos:")
        print("  1. python install.py")
        print("  2. python main.py")
        print()
        print("Tu Sound Hz Emitter esta listo!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nSi el error persiste, reportalo con detalles.")
    
    input("\nPresiona Enter para finalizar...")

if __name__ == "__main__":
    main()
