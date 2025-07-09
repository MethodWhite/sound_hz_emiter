"""Ventana principal de la aplicacion Sound Hz Emitter - VERSION CORREGIDA CON SCROLL"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QSlider, QComboBox, QCheckBox,
    QFrame, QGroupBox, QStatusBar, QMessageBox, QTextEdit,
    QScrollArea  # AGREGADO PARA SCROLL
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
        
        # Estilo del frame - ALTURA FIJA PARA CONSISTENCIA
        self.setFrameStyle(QFrame.Box)
        self.setFixedHeight(150)  # ALTURA FIJA
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
        
        # Grupo de control de tonos CON SCROLL - AQUI ESTA LA CORRECCION
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
        
        # SCROLL AREA PARA LOS TONOS - SOLUCION AL PROBLEMA
        self.scroll_area_tonos = QScrollArea()
        self.scroll_area_tonos.setWidgetResizable(True)
        self.scroll_area_tonos.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_tonos.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area_tonos.setMinimumHeight(200)  # Altura minima
        self.scroll_area_tonos.setMaximumHeight(400)  # Altura maxima
        
        # Estilo para el scroll area
        self.scroll_area_tonos.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ccc;
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
        """)
        
        # Widget contenedor para los controles de tonos
        self.widget_contenedor_tonos = QWidget()
        self.layout_tonos = QVBoxLayout(self.widget_contenedor_tonos)
        self.layout_tonos.setSpacing(5)  # Espacio entre tonos
        self.layout_tonos.setContentsMargins(5, 5, 5, 5)
        
        # Spacer para empujar tonos hacia arriba
        self.layout_tonos.addStretch()
        
        # Asignar widget contenedor al scroll area
        self.scroll_area_tonos.setWidget(self.widget_contenedor_tonos)
        
        # Agregar scroll area al grupo
        layout_grupo_tonos.addWidget(self.scroll_area_tonos, 1)  # Expandir
        
        layout_controles.addWidget(grupo_tonos, 1)  # Expandir el grupo de tonos
        
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
<li><b>Scroll en Tonos:</b> Usa la rueda del mouse o barra lateral para ver todos</li>
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

<h3>NOVEDAD:</h3>
<p><b>Scroll en Tonos:</b> Ahora puedes agregar muchos tonos y navegar entre ellos!</p>
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
        
        # Agregar a la interfaz ANTES del spacer
        spacer_index = self.layout_tonos.count() - 1  # Indice del spacer
        self.layout_tonos.insertWidget(spacer_index, control_tono)
        self.controles_tonos[id_tono] = control_tono
        
        # Agregar al motor de audio
        self.motor_audio.agregar_tono(id_tono, 440, 0.5)
        
        # Actualizar estadisticas
        self.actualizar_estadisticas()
        
        # Actualizar barra de estado
        self.barra_estado.showMessage(f"Tono {id_tono} agregado - Total: {len(self.controles_tonos)}")
        
        # Auto-scroll hacia el final para mostrar el nuevo tono
        self.scroll_area_tonos.verticalScrollBar().setValue(
            self.scroll_area_tonos.verticalScrollBar().maximum()
        )
        
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