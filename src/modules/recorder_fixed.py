"""
Módulo de Grabación de Simulación

Este módulo proporciona funcionalidades para grabar simulaciones de SUMO como videos,
capturando frames, añadiendo información y generando mapas de calor.

Este módulo resuelve el error 0x80070002 (ERROR_FILE_NOT_FOUND) asegurando que todas
las rutas de archivos son válidas y se crean los directorios necesarios.
"""

import os
import cv2
import traci
from datetime import datetime
import logging
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, Optional
import time

# Configurar logging
logging.basicConfig(filename='simulation_recorder.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SimulationRecorder:
    """
    Clase para grabar la simulación de SUMO como un video.
    
    Atributos:
        sumo_config: Ruta al archivo de configuración de SUMO
        parameters: Parámetros de la simulación
        fps: Frames por segundo del video
        frames: Lista de frames capturados
        temp_dir: Directorio temporal para los frames
        temp_frame_path: Ruta al archivo temporal de frame
        output_file: Ruta al archivo de salida (video)
        progress_bar: Barra de progreso para mostrar avance
    """
    
    def __init__(self, sumo_config: str, parameters: Dict[str, Any], fps: int = 30, output_file: Optional[str] = None):
        """
        Inicializa el grabador de simulación.
        
        Args:
            sumo_config: Ruta al archivo de configuración de SUMO
            parameters: Diccionario con parámetros de la simulación
            fps: Frames por segundo del video de salida
            output_file: Ruta al archivo de salida. Si es None, se generará automáticamente.
        """
        self.sumo_config = sumo_config
        self.parameters = parameters
        self.fps = fps
        self.frames = []
        
        # Crear directorio temporal para guardar frames
        self.temp_dir = os.path.abspath("temp_frames")
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            logging.info(f"Created temporary directory: {self.temp_dir}")
            
        self.temp_frame_path = os.path.join(self.temp_dir, "temp_frame.png")
        
        # Determinar el archivo de salida
        if output_file:
            self.output_file = output_file
        else:
            self.output_file = self.generate_output_filename()
            
        # Asegurar que el directorio de salida existe
        output_dir = os.path.dirname(os.path.abspath(self.output_file))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")
            
        # Inicializar barra de progreso
        self.progress_bar = tqdm(total=parameters['total_steps'], desc="Simulación", unit="step")
        
        logging.info(f"SimulationRecorder initialized. Output file: {self.output_file}")

    def generate_output_filename(self) -> str:
        """
        Genera un nombre de archivo para el video de salida basado en la fecha y hora.
        
        Returns:
            Ruta absoluta al archivo de salida generado
        """
        # Generar timestamp único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extraer solo el nombre de archivo sin la ruta
        sumo_config_name = os.path.basename(self.sumo_config).replace(".sumocfg", "")
        filename = f"{sumo_config_name}_{timestamp}.mp4"
        
        # Crear la carpeta 'recordings' en el directorio actual si no existe
        output_dir = os.path.abspath("recordings")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        return os.path.join(output_dir, filename)

    def capture_frame(self):
        """
        Captura un frame de la simulación SUMO actual.
        """
        try:
            start_time = time.perf_counter()
            traci.gui.screenshot("View #0", self.temp_frame_path)
            frame = cv2.imread(self.temp_frame_path)
            if frame is not None:
                self.frames.append(frame)
                logging.debug(f"Frame captured. Total frames: {len(self.frames)}")
            else:
                logging.warning(f"Frame capture failed: image could not be read from {self.temp_frame_path}")
            elapsed = time.perf_counter() - start_time
            logging.info(f"capture_frame took {elapsed:.6f} seconds")
        except Exception as e:
            logging.error(f"Error capturing frame: {e}")
        finally:
            if os.path.exists(self.temp_frame_path):
                try:
                    os.remove(self.temp_frame_path)
                except Exception as e:
                    logging.error(f"Error removing temp frame: {e}")

    def overlay_text(self, frame, species_name=None, grid=None, step=None):
        """
        Añade información de texto sobre el frame del video, incluyendo especie y métricas.
        
        Args:
            frame: Frame del video a modificar
            species_name: Nombre de la especie (opcional)
            grid: Cuadrícula de contaminación (opcional)
            step: Paso de simulación (opcional)
            
        Returns:
            Frame con el texto añadido
        """
        # Crear texto con información de la simulación
        parameters_text = "\n".join([f"{key}: {value}" for key, value in self.parameters.items()])
        simulation_time = traci.simulation.getTime() if traci.isLoaded() else 0
        num_vehicles = traci.vehicle.getIDCount() if traci.isLoaded() else 0
        additional_info = f"Time: {simulation_time:.2f} s\nVehicles: {num_vehicles}"
        overlay = f"Config: {os.path.basename(self.sumo_config)}\nParameters:\n{parameters_text}\n{additional_info}"
        if species_name and grid is not None:
            overlay += f"\nSpecies: {species_name}"
            overlay += f"\nMax: {np.max(grid):.2e}  Mean: {np.mean(grid):.2e}"
        if step is not None:
            overlay += f"\nStep: {step}"
        # Añadir el texto al frame
        y0, dy = 30, 30
        for i, line in enumerate(overlay.split('\n')):
            y = y0 + i * dy
            cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            
        return frame

    def save_video(self, species_name=None, grid=None, step=None):
        """
        Guarda los frames capturados como un video, con overlay avanzado.
        
        Returns:
            Boolean indicando si el guardado fue exitoso
        """
        if not self.frames:
            logging.warning("No frames to save")
            return False
            
        try:
            # Obtener dimensiones del primer frame
            height, width, layers = self.frames[0].shape
            
            # Crear el objeto de video con codec mp4v
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(self.output_file, fourcc, self.fps, (width, height))
            
            # Escribir cada frame en el video
            for i, frame in enumerate(self.frames):
                frame = self.overlay_text(frame, species_name=species_name, grid=grid, step=step)
                video.write(frame)
                if i % 10 == 0:
                    logging.debug(f"Writing frame {i+1}/{len(self.frames)}")
            
            # Liberar recursos
            video.release()
            
            logging.info(f"Video saved to {self.output_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving video: {e}")
            return False
        
        finally:
            # Limpiar el directorio temporal
            if os.path.exists(self.temp_dir):
                try:
                    for file in os.listdir(self.temp_dir):
                        file_path = os.path.join(self.temp_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(self.temp_dir)
                    logging.info(f"Cleaned temporary directory: {self.temp_dir}")
                except Exception as e:
                    logging.error(f"Error cleaning temp directory: {e}")

    def update_progress(self, step: int):
        """
        Actualiza la barra de progreso.
        
        Args:
            step: Número de pasos a avanzar en la barra de progreso
        """
        self.progress_bar.update(step)

    def close_progress_bar(self):
        """
        Cierra la barra de progreso.
        """
        self.progress_bar.close()

    def visualize_heatmap(self, pollution_grid):
        """
        Visualiza la cuadrícula de contaminación como un mapa de calor.
        
        Args:
            pollution_grid: Array NumPy con valores de contaminación
        """
        try:
            # Crear una nueva figura
            plt.figure(figsize=(10, 8))
            
            # Generar mapa de calor
            heatmap = plt.imshow(pollution_grid, cmap='hot', interpolation='nearest')
            plt.colorbar(heatmap, label='Contaminación')
            plt.title('Mapa de calor de contaminación')
            
            # Añadir etiquetas
            plt.xlabel('Coordenada X')
            plt.ylabel('Coordenada Y')
            
            # Guardar la imagen en el mismo directorio que el video
            heatmap_path = os.path.join(os.path.dirname(self.output_file), 
                                        os.path.basename(self.output_file).replace('.mp4', '_heatmap.png'))
            plt.savefig(heatmap_path)
            plt.close()
            
            logging.info(f"Heatmap saved to {heatmap_path}")
            
        except Exception as e:
            logging.error(f"Error generating heatmap: {e}")