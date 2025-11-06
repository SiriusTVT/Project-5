"""
Sistema de Cámara con envío OSC a Pure Data
Conecta los parámetros visuales con Pure Data en tiempo real
"""

import cv2
import numpy as np
from collections import deque
import time
from pythonosc import udp_client

class CameraToPureData:
    def __init__(self, camera_index=0, osc_ip="127.0.0.1", osc_port=5580):
        """
        Inicializa el sistema de cámara con envío OSC
        
        Args:
            camera_index: Índice de la cámara (0 por defecto)
            osc_ip: IP de Pure Data (127.0.0.1 para mismo equipo)
            osc_port: Puerto OSC (5580 por defecto, igual que tu patch)
        """
        # Configurar cámara
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la cámara")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Configurar cliente OSC
        self.osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        print(f"Cliente OSC configurado: {osc_ip}:{osc_port}")
        
        # Variables para detección de movimiento
        self.prev_frame = None
        self.motion_history = deque(maxlen=10)
        
        # Fuente para overlay
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        print("Sistema de cámara con OSC inicializado correctamente")
    
    def extract_color_params(self, frame):
        """Extrae parámetros de color RGB"""
        avg_color = cv2.mean(frame)[:3]  # BGR
        
        return {
            'red': avg_color[2] / 255.0,
            'green': avg_color[1] / 255.0,
            'blue': avg_color[0] / 255.0
        }
    
    def extract_brightness_contrast(self, frame):
        """Extrae brillo y contraste"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray) / 255.0
        contrast = np.std(gray) / 128.0
        
        return {
            'brightness': brightness,
            'contrast': contrast
        }
    
    def detect_motion(self, frame):
        """Detecta movimiento entre frames"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return 0.0
        
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        motion_pixels = np.sum(thresh) / 255.0
        total_pixels = thresh.shape[0] * thresh.shape[1]
        motion_level = motion_pixels / total_pixels
        
        self.prev_frame = gray
        self.motion_history.append(motion_level)
        
        return min(motion_level * 10, 1.0)
    
    def extract_texture(self, frame):
        """Extrae textura usando gradientes"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        texture_intensity = np.mean(magnitude) / 255.0
        
        return min(texture_intensity, 1.0)
    
    def get_all_params(self, frame):
        """Extrae todos los parámetros visuales"""
        color = self.extract_color_params(frame)
        bright_contrast = self.extract_brightness_contrast(frame)
        motion = self.detect_motion(frame)
        texture = self.extract_texture(frame)
        
        return {
            'red': color['red'],
            'green': color['green'],
            'blue': color['blue'],
            'brightness': bright_contrast['brightness'],
            'contrast': bright_contrast['contrast'],
            'motion': motion,
            'texture': texture
        }
    
    def send_to_puredata(self, params):
        """
        Envía parámetros a Pure Data vía OSC con nombres individuales
        Ahora cada parámetro tiene su propia ruta para ruteo fácil
        """
        try:
            # Enviar cada parámetro con su nombre individual
            self.osc_client.send_message("/red", params['red'])
            self.osc_client.send_message("/green", params['green'])
            self.osc_client.send_message("/blue", params['blue'])
            self.osc_client.send_message("/brightness", params['brightness'])
            self.osc_client.send_message("/contrast", params['contrast'])
            self.osc_client.send_message("/motion", params['motion'])
            self.osc_client.send_message("/texture", params['texture'])
            
            # También enviar lista completa por si la necesitas
            values = [
                params['red'],
                params['green'],
                params['blue'],
                params['brightness'],
                params['contrast'],
                params['motion'],
                params['texture']
            ]
            self.osc_client.send_message("/visual", values)
            
        except Exception as e:
            print(f"Error enviando OSC: {e}")
    
    def draw_overlay(self, frame, params):
        """Dibuja información sobre el frame"""
        overlay = frame.copy()
        
        # Fondo semi-transparente
        cv2.rectangle(overlay, (10, 10), (350, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        y_pos = 35
        line_height = 25
        
        # Título
        cv2.putText(frame, "CAMARA -> PURE DATA", (20, y_pos), 
                   self.font, 0.7, (0, 255, 255), 2)
        y_pos += line_height + 5
        
        # Parámetros
        cv2.putText(frame, f"R: {params['red']:.3f}", (20, y_pos), 
                   self.font, 0.6, (0, 0, 255), 2)
        y_pos += line_height
        
        cv2.putText(frame, f"G: {params['green']:.3f}", (20, y_pos), 
                   self.font, 0.6, (0, 255, 0), 2)
        y_pos += line_height
        
        cv2.putText(frame, f"B: {params['blue']:.3f}", (20, y_pos), 
                   self.font, 0.6, (255, 0, 0), 2)
        y_pos += line_height
        
        cv2.putText(frame, f"Brillo: {params['brightness']:.3f}", (20, y_pos), 
                   self.font, 0.6, (255, 255, 255), 2)
        y_pos += line_height
        
        cv2.putText(frame, f"Movimiento: {params['motion']:.3f}", (20, y_pos), 
                   self.font, 0.6, (255, 255, 0), 2)
        
        return frame
    
    def run(self):
        """Ejecuta el loop principal"""
        print("\n=== Sistema de Cámara → Pure Data ===")
        print("Asegúrate de que Pure Data esté corriendo con [netreceive -u -b 5580]")
        print("\nControles:")
        print("  'q' - Salir")
        print("  's' - Screenshot")
        print("\nEnviando datos...\n")
        
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
                
                # Enviar a Pure Data
                self.send_to_puredata(params)
                
                # Dibujar overlay
                frame = self.draw_overlay(frame, params)
                
                # Calcular FPS
                fps_counter += 1
                if time.time() - fps_time > 1.0:
                    fps = fps_counter
                    fps_counter = 0
                    fps_time = time.time()
                
                cv2.putText(frame, f"FPS: {fps}", (10, frame.shape[0] - 10), 
                           self.font, 0.6, (0, 255, 0), 2)
                
                # Mostrar frame
                cv2.imshow('Camara -> Pure Data (OSC)', frame)
                
                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nSaliendo...")
                    break
                elif key == ord('s'):
                    filename = f"screenshot_{int(time.time())}.png"
                    cv2.imwrite(filename, frame)
                    print(f"Screenshot guardado: {filename}")
                
        except KeyboardInterrupt:
            print("\nInterrumpido por usuario")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Libera recursos"""
        print("Liberando recursos...")
        self.cap.release()
        cv2.destroyAllWindows()


def main():
    """Función principal"""
    print("=== Configuración de Conexión ===")
    print("\nOpciones de IP:")
    print("  127.0.0.1  - Para Pure Data en el mismo equipo (RECOMENDADO)")
    print("  172.24.5.46 - Para Pure Data en otro equipo de la red")
    print("\nPuerto: 5580 (según tu patch de Pure Data)")
    print()
    
    # Usar localhost por defecto (mismo equipo)
    osc_ip = "127.0.0.1"  # Cambia a "172.24.5.46" si Pure Data está en otro equipo
    osc_port = 5580  # Puerto de tu patch de Pure Data
    
    try:
        # Crear instancia del sistema
        camera = CameraToPureData(camera_index=0, osc_ip=osc_ip, osc_port=osc_port)
        
        # Ejecutar
        camera.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
