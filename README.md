# Sound Hz Emitter v2.0

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
