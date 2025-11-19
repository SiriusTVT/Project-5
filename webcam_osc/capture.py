import cv2
from typing import Optional
import numpy as np


class WebcamCapture:
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.width = width
        self.height = height

    def start(self) -> bool:
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if self.cap.isOpened():
            # Configurar resolución para mejor rendimiento
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            # Configurar FPS de la cámara
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            # Deshabilitar auto-exposure para rendimiento más consistente
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            # Buffer pequeño para menor latencia
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return self.cap.isOpened()

    def get_frame(self) -> Optional[np.ndarray]:
        if self.cap is None or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    def stop(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __enter__(self) -> 'WebcamCapture':
        self.start()
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: type) -> None:
        self.stop()
