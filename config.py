"""
Archivo de configuración para el sistema de cámara
Ajusta estos valores según tus necesidades
"""

# ===== CONFIGURACIÓN DE CÁMARA =====
CAMERA_INDEX = 0  # Índice de la cámara (0 = cámara por defecto, 1, 2... para otras cámaras)
CAMERA_WIDTH = 640  # Ancho de captura en píxeles
CAMERA_HEIGHT = 480  # Alto de captura en píxeles
FPS_TARGET = 30  # FPS objetivo (no garantizado, depende de la cámara)

# ===== CONFIGURACIÓN DE VISUALIZACIÓN =====
SHOW_OVERLAY = True  # Mostrar información sobre el video
SHOW_COLOR_BARS = True  # Mostrar barras de color
SHOW_FPS = True  # Mostrar FPS en pantalla
PRINT_TO_CONSOLE = True  # Imprimir parámetros en consola
CONSOLE_PRINT_INTERVAL = 30  # Cada cuántos frames imprimir (30 = cada segundo aprox)

# ===== CONFIGURACIÓN DE DETECCIÓN DE MOVIMIENTO =====
MOTION_THRESHOLD = 25  # Umbral para detección de movimiento (0-255)
MOTION_BLUR_SIZE = 21  # Tamaño del filtro Gaussian blur (debe ser impar)
MOTION_SENSITIVITY = 10  # Multiplicador de sensibilidad de movimiento
MOTION_HISTORY_SIZE = 10  # Número de frames a mantener en historial

# ===== CONFIGURACIÓN DE COLORES DOMINANTES =====
NUM_DOMINANT_COLORS = 3  # Número de colores dominantes a extraer (más = más lento)
ENABLE_DOMINANT_COLORS = False  # Activar extracción de colores dominantes (más CPU)
DOMINANT_COLORS_SAMPLE_SIZE = 100  # Tamaño de muestra para K-means (menor = más rápido)

# ===== CONFIGURACIÓN DE TEXTURA =====
SOBEL_KERNEL_SIZE = 3  # Tamaño del kernel de Sobel (3, 5, 7)
TEXTURE_NORMALIZATION = 255  # Factor de normalización para textura

# ===== CONFIGURACIÓN DE OVERLAY =====
OVERLAY_TRANSPARENCY = 0.6  # Transparencia del fondo del overlay (0.0-1.0)
FONT_SCALE = 0.6  # Escala del texto
FONT_THICKNESS = 2  # Grosor del texto
OVERLAY_COLOR_TEXT = (0, 255, 255)  # Color del texto del título (BGR)
OVERLAY_COLOR_RGB_R = (0, 0, 255)  # Color para texto de Red (BGR)
OVERLAY_COLOR_RGB_G = (0, 255, 0)  # Color para texto de Green (BGR)
OVERLAY_COLOR_RGB_B = (255, 0, 0)  # Color para texto de Blue (BGR)
OVERLAY_COLOR_WHITE = (255, 255, 255)  # Color para texto general (BGR)
OVERLAY_COLOR_MOTION = (255, 255, 0)  # Color para texto de movimiento (BGR)

# ===== CONFIGURACIÓN DE BARRAS DE VISUALIZACIÓN =====
BAR_WIDTH = 20  # Ancho de cada barra de color
BAR_HEIGHT = 150  # Alto de las barras
BAR_SPACING = 25  # Espaciado entre barras
BAR_OFFSET_RIGHT = 100  # Offset desde el borde derecho

# ===== CONFIGURACIÓN DE MAPEO SONORO =====
# Estos valores pueden ser usados para mapear a Pure Data

# Rango de frecuencias (Hz)
FREQ_MIN_RED = 200
FREQ_MAX_RED = 600
FREQ_MIN_GREEN = 400
FREQ_MAX_GREEN = 800
FREQ_MIN_BLUE = 600
FREQ_MAX_BLUE = 1400

# Rango de amplitud
AMP_MIN = 0.0
AMP_MAX = 0.8  # Evitar saturación

# Rango de armónicos
HARMONICS_MIN = 1
HARMONICS_MAX = 9

# Rango de LFO (Hz)
LFO_MIN = 0.0
LFO_MAX = 10.0

# Rango de filtro (Hz)
FILTER_MIN = 200
FILTER_MAX = 4000

# ===== CONFIGURACIÓN DE DETECCIÓN DE EVENTOS =====
# Umbrales para detectar cambios significativos
BRIGHTNESS_CHANGE_THRESHOLD = 0.3  # Cambio mínimo de brillo para triggear evento
MOTION_START_THRESHOLD = 0.5  # Nivel de movimiento para considerar "inicio de movimiento"
MOTION_STOP_THRESHOLD = 0.2  # Nivel de movimiento para considerar "fin de movimiento"
COLOR_CHANGE_THRESHOLD = 0.4  # Cambio mínimo en cualquier canal RGB

# ===== CONFIGURACIÓN DE RENDIMIENTO =====
ENABLE_GPU = False  # Intentar usar GPU (requiere opencv-contrib-python)
OPTIMIZE_FOR_SPEED = True  # Optimizar para velocidad vs calidad
REDUCE_QUALITY_ON_LOW_FPS = True  # Reducir calidad si FPS < 20
LOW_FPS_THRESHOLD = 20  # FPS mínimo antes de reducir calidad

# ===== CONFIGURACIÓN DE DEBUG =====
DEBUG_MODE = False  # Activar modo debug con información extra
SAVE_DEBUG_FRAMES = False  # Guardar frames de debug
DEBUG_FRAME_INTERVAL = 100  # Guardar cada N frames en modo debug

# ===== CONFIGURACIÓN DE PURE DATA (para futura integración) =====
OSC_ENABLED = False  # Habilitar envío OSC a Pure Data
OSC_IP = "127.0.0.1"  # IP de Pure Data
OSC_PORT = 8000  # Puerto OSC
OSC_UPDATE_RATE = 30  # Actualizaciones por segundo (max)

# ===== PRESETS =====
# Puedes crear diferentes configuraciones para diferentes escenarios

PRESETS = {
    'performance': {
        'description': 'Optimizado para rendimiento',
        'CAMERA_WIDTH': 320,
        'CAMERA_HEIGHT': 240,
        'ENABLE_DOMINANT_COLORS': False,
        'CONSOLE_PRINT_INTERVAL': 60,
        'MOTION_BLUR_SIZE': 11
    },
    'quality': {
        'description': 'Máxima calidad',
        'CAMERA_WIDTH': 1280,
        'CAMERA_HEIGHT': 720,
        'ENABLE_DOMINANT_COLORS': True,
        'NUM_DOMINANT_COLORS': 5,
        'MOTION_BLUR_SIZE': 31
    },
    'balanced': {
        'description': 'Balance entre calidad y rendimiento',
        'CAMERA_WIDTH': 640,
        'CAMERA_HEIGHT': 480,
        'ENABLE_DOMINANT_COLORS': False,
        'MOTION_BLUR_SIZE': 21
    }
}

# Preset activo (puedes cambiar esto)
ACTIVE_PRESET = 'balanced'


def apply_preset(preset_name):
    """
    Aplica un preset de configuración
    
    Args:
        preset_name: Nombre del preset a aplicar
    """
    if preset_name not in PRESETS:
        print(f"Preset '{preset_name}' no encontrado. Usando configuración por defecto.")
        return
    
    preset = PRESETS[preset_name]
    print(f"Aplicando preset: {preset_name} - {preset['description']}")
    
    # Actualizar variables globales
    globals().update(preset)


def get_config():
    """
    Retorna un diccionario con toda la configuración actual
    
    Returns:
        dict: Configuración completa
    """
    return {
        'camera': {
            'index': CAMERA_INDEX,
            'width': CAMERA_WIDTH,
            'height': CAMERA_HEIGHT,
            'fps_target': FPS_TARGET
        },
        'display': {
            'show_overlay': SHOW_OVERLAY,
            'show_color_bars': SHOW_COLOR_BARS,
            'show_fps': SHOW_FPS,
            'print_to_console': PRINT_TO_CONSOLE,
            'console_interval': CONSOLE_PRINT_INTERVAL
        },
        'motion': {
            'threshold': MOTION_THRESHOLD,
            'blur_size': MOTION_BLUR_SIZE,
            'sensitivity': MOTION_SENSITIVITY,
            'history_size': MOTION_HISTORY_SIZE
        },
        'colors': {
            'num_dominant': NUM_DOMINANT_COLORS,
            'enable_dominant': ENABLE_DOMINANT_COLORS,
            'sample_size': DOMINANT_COLORS_SAMPLE_SIZE
        },
        'texture': {
            'kernel_size': SOBEL_KERNEL_SIZE,
            'normalization': TEXTURE_NORMALIZATION
        },
        'mapping': {
            'freq_red': (FREQ_MIN_RED, FREQ_MAX_RED),
            'freq_green': (FREQ_MIN_GREEN, FREQ_MAX_GREEN),
            'freq_blue': (FREQ_MIN_BLUE, FREQ_MAX_BLUE),
            'amplitude': (AMP_MIN, AMP_MAX),
            'harmonics': (HARMONICS_MIN, HARMONICS_MAX),
            'lfo': (LFO_MIN, LFO_MAX),
            'filter': (FILTER_MIN, FILTER_MAX)
        },
        'events': {
            'brightness_threshold': BRIGHTNESS_CHANGE_THRESHOLD,
            'motion_start': MOTION_START_THRESHOLD,
            'motion_stop': MOTION_STOP_THRESHOLD,
            'color_change': COLOR_CHANGE_THRESHOLD
        },
        'performance': {
            'enable_gpu': ENABLE_GPU,
            'optimize_speed': OPTIMIZE_FOR_SPEED,
            'reduce_on_low_fps': REDUCE_QUALITY_ON_LOW_FPS,
            'low_fps_threshold': LOW_FPS_THRESHOLD
        },
        'osc': {
            'enabled': OSC_ENABLED,
            'ip': OSC_IP,
            'port': OSC_PORT,
            'update_rate': OSC_UPDATE_RATE
        }
    }


def print_config():
    """
    Imprime la configuración actual de forma legible
    """
    config = get_config()
    
    print("\n" + "="*50)
    print("CONFIGURACIÓN ACTUAL")
    print("="*50)
    
    for category, settings in config.items():
        print(f"\n[{category.upper()}]")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    # Si ejecutas este archivo, muestra la configuración actual
    print_config()
    
    print("\nPresets disponibles:")
    for name, preset in PRESETS.items():
        print(f"  - {name}: {preset['description']}")
