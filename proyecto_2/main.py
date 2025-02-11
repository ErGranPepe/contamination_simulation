import threading
import logging
import traci
import time

from logging_config import setup_logging
from ui.config_gui import ConfigGUI
from simulation.simulation import ContaminationSimulation
from simulation.recorder import SimulationRecorder

# Configurar el logger
logger = setup_logging()

def apply_config(config):
    """
    Callback que se ejecuta al aplicar la configuración desde la GUI.
    Inicia SUMO, la simulación y opcionalmente graba un video.

    Args:
        config (dict): Configuración de la simulación proporcionada por la GUI.
    """
    logger.info("Configuración recibida. Iniciando simulación...")
    
    # Validar que el archivo de configuración SUMO esté especificado
    sumo_config_file = config.get("sumo_config_file")
    if not sumo_config_file:
        logger.error("No se especificó el archivo de configuración SUMO.")
        return

    try:
        # Iniciar SUMO con TraCI
        sumo_command = ["sumo-gui", "-c", sumo_config_file]
        logger.info(f"Iniciando SUMO con el comando: {' '.join(sumo_command)}")
        traci.start(sumo_command)

        # Crear instancia de la simulación
        simulation = ContaminationSimulation(config)

        # Crear instancia del grabador si está habilitado
        recorder = None
        if config.get("record_simulation"):
            recorder = SimulationRecorder(
                output_file=config.get("output_file", "simulation.mp4"),
                fps=30,
                config=config
            )
            logger.info("Grabación habilitada. Archivo de salida: %s", recorder.output_file)

        # Ejecutar la simulación en un hilo separado para no bloquear la GUI
        simulation_thread = threading.Thread(
            target=run_simulation,
            args=(simulation, recorder, config.get("total_steps", 1000)),
            daemon=True  # Hilo en segundo plano que se cerrará al salir del programa
        )
        simulation_thread.start()

    except Exception as e:
        logger.error(f"Error al iniciar la simulación: {e}")
        traci.close()

def run_simulation(simulation, recorder, total_steps):
    """
    Ejecuta la simulación paso a paso.

    Args:
        simulation (ContaminationSimulation): Instancia de la simulación.
        recorder (SimulationRecorder): Instancia del grabador de video (opcional).
        total_steps (int): Número total de pasos a simular.
    """
    try:
        logger.info("Simulación iniciada. Total de pasos: %d", total_steps)

        for step in range(total_steps):
            # Avanzar un paso en SUMO
            traci.simulationStep()

            # Actualizar los cálculos de contaminación en la simulación
            simulation.step()

            # Capturar un frame si el grabador está habilitado
            if recorder and step % int(30 / recorder.fps) == 0:  # Captura según FPS configurado
                recorder.capture_frame()

            time.sleep(0.01)  # Pequeño retraso para evitar sobrecargar el sistema

        logger.info("Simulación completada.")

        # Guardar el video si se habilitó la grabación
        if recorder:
            recorder.save_video()
            logger.info("Video guardado exitosamente.")

    except Exception as e:
        logger.error(f"Error durante la simulación: {e}")

    finally:
        # Cerrar conexión con TraCI al finalizar
        traci.close()
        logger.info("Conexión con TraCI cerrada.")

def main():
    """
    Punto de entrada principal para la aplicación.
    Configura e inicia la interfaz gráfica.
    """
    try:
        import tkinter as tk

        # Crear ventana principal de Tkinter
        root = tk.Tk()

        # Inicializar GUI con callback para aplicar configuración y ejecutar simulación
        app = ConfigGUI(root, apply_callback=apply_config)

        logger.info("Interfaz gráfica iniciada.")
        
        # Ejecutar el bucle principal de Tkinter
        app.run()

    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}")

if __name__ == "__main__":
    main()
