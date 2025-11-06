"""
Sistema de Cámara para Extracción de Parámetros Visuales
Este script captura video en tiempo real y extrae parámetros visuales
que pueden ser enviados a Pure Data para síntesis de sonido.
"""

import cv2
import numpy as np
from collections import deque
import time

class CameraVisualParams:
    def __init__(self, camera_index=0):
        """
        Inicializa el sistema de captura de cámara
        
        Args:
            camera_index: Índice de la cámara (0 por defecto)
        """
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la cámara")
        
        # Configurar resolución para mejor rendimiento
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Historial para detección de movimiento
        self.prev_frame = None
        self.motion_history = deque(maxlen=10)
        
        # Variables para mostrar valores
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.font_thickness = 2
        
        print("Sistema de cámara inicializado correctamente")
    
    def extract_color_params(self, frame):
        """
        Extrae parámetros de color del frame
        
        Returns:
            dict: Diccionario con valores RGB promedio normalizados (0-1)
        """
        # Calcular color promedio
        avg_color = cv2.mean(frame)[:3]  # BGR
        
        # Normalizar valores a rango 0-1
        b_norm = avg_color[0] / 255.0
        g_norm = avg_color[1] / 255.0
        r_norm = avg_color[2] / 255.0
        
        return {
            'red': r_norm,
            'green': g_norm,
            'blue': b_norm,
            'brightness': (r_norm + g_norm + b_norm) / 3.0
        }
    
    def extract_brightness_contrast(self, frame):
        """
        Extrae brillo y contraste del frame
        
        Returns:
            dict: Diccionario con brillo y contraste normalizados
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calcular brillo (promedio de intensidad)
        brightness = np.mean(gray) / 255.0
        
        # Calcular contraste (desviación estándar)
        contrast = np.std(gray) / 128.0  # Normalizado
        
        return {
            'brightness': brightness,
            'contrast': contrast
        }
    
    def detect_motion(self, frame):
        """
        Detecta cantidad de movimiento en el frame
        
        Returns:
            float: Nivel de movimiento normalizado (0-1)
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return 0.0
        
        # Calcular diferencia absoluta
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Calcular cantidad de movimiento
        motion_pixels = np.sum(thresh) / 255.0
        total_pixels = thresh.shape[0] * thresh.shape[1]
        motion_level = motion_pixels / total_pixels
        
        # Actualizar frame anterior
        self.prev_frame = gray
        
        # Guardar en historial
        self.motion_history.append(motion_level)
        
        return min(motion_level * 10, 1.0)  # Amplificar y limitar a 1.0
    
    def extract_dominant_colors(self, frame, k=3):
        """
        Extrae los colores dominantes usando K-means
        
        Args:
            frame: Frame de video
            k: Número de colores dominantes a extraer
            
        Returns:
            list: Lista de colores dominantes normalizados
        """
        # Redimensionar para acelerar el procesamiento
        small_frame = cv2.resize(frame, (100, 100))
        pixels = small_frame.reshape(-1, 3).astype(np.float32)
        
        # Aplicar K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Normalizar colores
        dominant_colors = []
        for center in centers:
            b, g, r = center / 255.0
            dominant_colors.append({
                'red': float(r),
                'green': float(g),
                'blue': float(b)
            })
        
        return dominant_colors
    
    def extract_texture(self, frame):
        """
        Extrae información de textura usando gradientes
        
        Returns:
            dict: Información de textura
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calcular gradientes
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calcular magnitud del gradiente
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Normalizar
        texture_intensity = np.mean(magnitude) / 255.0
        texture_variance = np.std(magnitude) / 128.0
        
        return {
            'intensity': min(texture_intensity, 1.0),
            'variance': min(texture_variance, 1.0)
        }
    
    def draw_overlay(self, frame, params):
        """
        Dibuja información de parámetros sobre el frame
        
        Args:
            frame: Frame de video
            params: Diccionario de parámetros extraídos
        """
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Fondo semi-transparente para el texto
        cv2.rectangle(overlay, (10, 10), (350, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        y_pos = 35
        line_height = 25
        
        # Título
        cv2.putText(frame, "PARAMETROS VISUALES", (20, y_pos), 
                   self.font, 0.7, (0, 255, 255), 2)
        y_pos += line_height + 10
        
        # Mostrar colores RGB
        cv2.putText(frame, f"R: {params['color']['red']:.3f}", (20, y_pos), 
                   self.font, self.font_scale, (0, 0, 255), self.font_thickness)
        y_pos += line_height
        
        cv2.putText(frame, f"G: {params['color']['green']:.3f}", (20, y_pos), 
                   self.font, self.font_scale, (0, 255, 0), self.font_thickness)
        y_pos += line_height
        
        cv2.putText(frame, f"B: {params['color']['blue']:.3f}", (20, y_pos), 
                   self.font, self.font_scale, (255, 0, 0), self.font_thickness)
        y_pos += line_height + 5
        
        # Brillo y contraste
        cv2.putText(frame, f"Brillo: {params['brightness']:.3f}", (20, y_pos), 
                   self.font, self.font_scale, (255, 255, 255), self.font_thickness)
        y_pos += line_height
        
        cv2.putText(frame, f"Contraste: {params['contrast']:.3f}", (20, y_pos), 
                   self.font, self.font_scale, (255, 255, 255), self.font_thickness)
        y_pos += line_height
        
        # Movimiento
        cv2.putText(frame, f"Movimiento: {params['motion']:.3f}", (20, y_pos), 
                   self.font, self.font_scale, (255, 255, 0), self.font_thickness)
        y_pos += line_height
        
        # Textura
        cv2.putText(frame, f"Textura: {params['texture']['intensity']:.3f}", (20, y_pos), 
                   self.font, self.font_scale, (200, 200, 200), self.font_thickness)
        
        # Barras de visualización (lado derecho)
        bar_x = w - 100
        bar_width = 60
        bar_height = 150
        bar_y = 50
        
        # Barra de color RGB
        rgb_colors = [
            (0, 0, int(params['color']['red'] * 255)),
            (0, int(params['color']['green'] * 255), 0),
            (int(params['color']['blue'] * 255), 0, 0)
        ]
        
        for i, color in enumerate(rgb_colors):
            x_offset = bar_x + i * 25
            height = int(bar_height * list(params['color'].values())[i])
            cv2.rectangle(frame, 
                         (x_offset, bar_y + bar_height - height), 
                         (x_offset + 20, bar_y + bar_height), 
                         color, -1)
            cv2.rectangle(frame, 
                         (x_offset, bar_y), 
                         (x_offset + 20, bar_y + bar_height), 
                         (100, 100, 100), 2)
        
        return frame
    
    def get_all_params(self, frame):
        """
        Extrae todos los parámetros visuales del frame
        
        Returns:
            dict: Diccionario con todos los parámetros
        """
        color_params = self.extract_color_params(frame)
        brightness_contrast = self.extract_brightness_contrast(frame)
        motion = self.detect_motion(frame)
        texture = self.extract_texture(frame)
        
        # Opcional: colores dominantes (más costoso computacionalmente)
        # dominant_colors = self.extract_dominant_colors(frame)
        
        params = {
            'color': color_params,
            'brightness': brightness_contrast['brightness'],
            'contrast': brightness_contrast['contrast'],
            'motion': motion,
            'texture': texture,
            'timestamp': time.time()
        }
        
        return params
    
    def run(self):
        """
        Ejecuta el loop principal de captura y análisis
        """
        print("\n=== Sistema de Captura Visual ===")
        print("Presiona 'q' para salir")
        print("Presiona 's' para tomar screenshot")
        print("\nIniciando captura...\n")
        
        fps_time = time.time()
        fps_counter = 0
        fps = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error al capturar frame")
                    break
                
                # Extraer parámetros
                params = self.get_all_params(frame)
                
                # Dibujar overlay con información
                frame = self.draw_overlay(frame, params)
                
                # Calcular FPS
                fps_counter += 1
                if time.time() - fps_time > 1.0:
                    fps = fps_counter
                    fps_counter = 0
                    fps_time = time.time()
                
                # Mostrar FPS
                cv2.putText(frame, f"FPS: {fps}", (10, frame.shape[0] - 10), 
                           self.font, 0.6, (0, 255, 0), 2)
                
                # Mostrar frame
                cv2.imshow('Sistema de Camara - Parametros Visuales', frame)
                
                # Imprimir parámetros en consola (opcional, comentar si molesta)
                if fps_counter % 30 == 0:  # Cada 30 frames
                    self.print_params(params)
                
                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nSaliendo...")
                    break
                elif key == ord('s'):
                    filename = f"screenshot_{int(time.time())}.png"
                    cv2.imwrite(filename, frame)
                    print(f"Screenshot guardado: {filename}")
                
        finally:
            self.cleanup()
    
    def print_params(self, params):
        """
        Imprime los parámetros en consola de forma legible
        """
        print("\n--- Parámetros Actuales ---")
        print(f"RGB: R={params['color']['red']:.3f} G={params['color']['green']:.3f} B={params['color']['blue']:.3f}")
        print(f"Brillo: {params['brightness']:.3f} | Contraste: {params['contrast']:.3f}")
        print(f"Movimiento: {params['motion']:.3f}")
        print(f"Textura: {params['texture']['intensity']:.3f}")
        print("-" * 30)
    
    def cleanup(self):
        """
        Libera recursos
        """
        print("Liberando recursos...")
        self.cap.release()
        cv2.destroyAllWindows()


def main():
    """
    Función principal
    """
    try:
        # Crear instancia del sistema de cámara
        camera_system = CameraVisualParams(camera_index=0)
        
        # Ejecutar
        camera_system.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
