import time
import cv2
from typing import Optional
from webcam_osc.config import GridConfig, OSCConfig, AppConfig
from webcam_osc.capture import WebcamCapture
from webcam_osc.analyzer import GridAnalyzer
from webcam_osc.osc_sender import OSCSender
from webcam_osc.visualizer import DataVisualizer


def main() -> None:
    config: AppConfig = AppConfig(
        grid=GridConfig(rows=4, cols=4),
        osc=OSCConfig(host="127.0.0.1", port=5005),
        camera_index=0,
        target_fps=30
    )

    visualizer: Optional[DataVisualizer] = DataVisualizer(config.grid, config.show_camera) if config.show_visualizer else None

    if visualizer:
        visualizer.show_loading_screen("Initializing components...")

    analyzer: GridAnalyzer = GridAnalyzer(config.grid)

    if visualizer:
        visualizer.show_loading_screen("Connecting to OSC...")

    osc_sender: OSCSender = OSCSender(config.osc)

    frame_delay: float = 1.0 / config.target_fps

    if visualizer:
        visualizer.show_loading_screen("Starting camera...")

    with WebcamCapture(config.camera_index, width=640, height=480) as capture:
        if not capture.start():
            print("Failed to open camera")
            return

        if visualizer:
            visualizer.show_loading_screen("Ready! Starting stream...")
            time.sleep(0.5)

        print(f"Streaming {config.grid.rows}x{config.grid.cols} grid to {config.osc.host}:{config.osc.port}")
        if config.show_visualizer:
            print(f"Data visualizer enabled (camera: {'on' if config.show_camera else 'off'})")
        elif config.show_camera:
            print("Camera preview enabled")

        frame_count = 0
        while True:
            start_time = time.time()

            frame = capture.get_frame()
            if frame is None:
                break

            cells_data = analyzer.analyze_frame(frame)
            osc_sender.send_grid_data(cells_data)

            # Actualizar visualización cada frame para mejor fluidez
            if config.show_camera and not config.show_visualizer:
                cv2.imshow("Webcam Grid", frame)

            if visualizer:
                visualizer.show(cells_data, frame if config.show_camera else None)
                if visualizer.check_should_close():
                    print("\nClosing application...")
                    break

            # waitKey más corto para mejor respuesta
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

            # Control de FPS más preciso
            elapsed = time.time() - start_time
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)
            
            frame_count += 1
            if frame_count % 30 == 0:  # Mostrar FPS cada 30 frames
                actual_fps = 1.0 / (time.time() - start_time + 0.0001)
                if frame_count == 30:
                    print(f"Running at ~{actual_fps:.1f} FPS")

        cv2.destroyAllWindows()
        if visualizer:
            visualizer.close()


if __name__ == "__main__":
    main()
