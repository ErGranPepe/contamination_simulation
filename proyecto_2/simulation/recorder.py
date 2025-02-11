import os
import cv2
import traci
import logging
from datetime import datetime

# Importar configuración de logging
from logging_config import setup_logging

# Configurar logger
logger = setup_logging()

class SimulationRecorder:
    """
    Clase para grabar la simulación de SUMO como un video.
    """

    def __init__(self, output_file="simulation.mp4", fps=30, config=None):
        """
        Inicializa el grabador de simulación.

        Args:
            output_file (str): Nombre del archivo de salida (video MP4).
            fps (int): Fotogramas por segundo para el video.
            config (dict): Diccionario con los parámetros de configuración.
        """
        self.output_file = output_file
        self.fps = fps
        self.config = config or {}
        self.frames = []  # Lista para almacenar los frames capturados temporalmente

        # Validar extensión del archivo de salida
        if not self.output_file.endswith(".mp4"):
            raise ValueError("El archivo de salida debe tener la extensión .mp4")
        
        logger.info(f"SimulationRecorder inicializado con archivo de salida: {self.output_file}, FPS: {self.fps}")

    def capture_frame(self, view_id="View #0"):
        """
        Captura un frame de la simulación desde una vista específica en SUMO.

        Args:
            view_id (str): ID de la vista SUMO desde donde capturar el frame.
        """
        try:
            # Crear un nombre temporal para guardar el screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            temp_filename = f"temp_frame_{timestamp}.png"

            # Capturar el screenshot usando TraCI
            traci.gui.screenshot(view_id, temp_filename)
            logger.debug(f"Frame capturado y guardado temporalmente en {temp_filename}")

            # Leer la imagen capturada con OpenCV
            frame = cv2.imread(temp_filename)
            
            if frame is not None:
                # Superponer información en el frame
                annotated_frame = self._annotate_frame(frame)
                self.frames.append(annotated_frame)
            
            # Eliminar el archivo temporal
            os.remove(temp_filename)

        except Exception as e:
            logger.error(f"Error al capturar el frame: {e}")
            raise

    def _annotate_frame(self, frame):
        """
        Superpone información sobre el frame usando OpenCV.

        Args:
            frame (np.ndarray): Imagen capturada del simulador.

        Returns:
            np.ndarray: Frame con anotaciones superpuestas.
        """
        try:
            overlay_text = [
                f"Wind Speed: {self.config.get('wind_speed', 'N/A')} m/s",
                f"Wind Direction: {self.config.get('wind_direction', 'N/A')}°",
                f"Grid Resolution: {self.config.get('grid_resolution', 'N/A')} m",
                f"Stability Class: {self.config.get('stability_class', 'N/A')}",
                f"Emission Factor: {self.config.get('emission_factor', 'N/A')}",
                f"Temperature: {self.config.get('temperature', 'N/A')}°C",
                f"Humidity: {self.config.get('humidity', 'N/A')}%",
                f"Deposition Rate: {self.config.get('deposition_rate', 'N/A')}"
            ]

            y_offset = 20  # Posición inicial del texto
            for line in overlay_text:
                cv2.putText(
                    frame,
                    line,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,  # Tamaño del texto
                    (255, 255, 255),  # Color del texto (blanco)
                    1,  # Grosor del texto
                    cv2.LINE_AA
                )
                y_offset += 20  # Incrementar posición vertical para la siguiente línea

            return frame

        except Exception as e:
            logger.error(f"Error al superponer información en el frame: {e}")
            raise

    def save_video(self):
        """
        Guarda los frames capturados como un video MP4.

        Raises:
            ValueError: Si no se han capturado frames.
        """
        try:
            if not self.frames:
                raise ValueError("No hay frames capturados para guardar en el video.")

            # Obtener dimensiones del primer frame
            height, width, _ = self.frames[0].shape

            # Crear un objeto VideoWriter para guardar el video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec para MP4
            video_writer = cv2.VideoWriter(self.output_file, fourcc, self.fps, (width, height))

            for frame in self.frames:
                video_writer.write(frame)

            video_writer.release()
            
            logger.info(f"Video guardado exitosamente en {self.output_file}")

        except Exception as e:
            logger.error(f"Error al guardar el video: {e}")
            raise

    def clear_frames(self):
        """
        Limpia los frames almacenados temporalmente.
        """
        self.frames.clear()
        logger.info("Frames temporales eliminados.")

# Ejemplo de uso
if __name__ == "__main__":
    import traci

    try:
        # Iniciar TraCI (asegúrate de que SUMO esté configurado correctamente)
        traci.start(["sumo-gui", "-c", "your_sumo_config.sumocfg"])

        recorder = SimulationRecorder(output_file="simulation.mp4", fps=30, config={
            "wind_speed": 5.0,
            "wind_direction": 90,
            "grid_resolution": 50,
            "stability_class": "C",
            "emission_factor": 1.2,
            "temperature": 25.0,
            "humidity": 60.0,
            "deposition_rate": 0.01
        })

        for step in range(100):  # Simular 100 pasos
            traci.simulationStep()
            
            if step % 5 == 0:  # Capturar un frame cada 5 pasos
                recorder.capture_frame()

        recorder.save_video()
    
    except Exception as e:
        logger.error(f"Error durante la grabación de la simulación: {e}")
    
    finally:
        traci.close()
