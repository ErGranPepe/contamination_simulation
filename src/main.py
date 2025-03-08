import os
import time
import tkinter as tk
from tkinter import messagebox
from modules.config import ContaminationConfigPlugin
from modules.toolTip import ToolTip
from modules.recorder import SimulationRecorder
from modules.CS import CS
import traci
import threading
import logging
import matplotlib.pyplot as plt
import numpy as np


logging.basicConfig(filename='simulation.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def estimate_simulation_time(config):
    total_steps = config['parameters']['total_steps']
    update_interval = config['parameters']['update_interval']
    estimated_time = (total_steps / update_interval) * 0.1  # Ejemplo de cálculo
    return estimated_time

def run_simulation(config):
    logging.info("Starting SUMO...")
    traci.start([r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe", "-c", config['sumo_config']])
    logging.info("SUMO started, connecting to TraCI...")
    simulation = CS(config)
    logging.info("Connected to TraCI")

    recorder = None
    if config['record_simulation']:
        logging.info("Recording simulation...")
        sumo_config = config['sumo_config']
        parameters = config['parameters']
        recorder = SimulationRecorder(sumo_config, parameters)
        logging.info("Recorder initialized")

    logging.info("Simulation started")
    step = 0
    while step < config['parameters']['total_steps'] and traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        simulation.update()

        if step % config['parameters']['update_interval'] == 0:
            for polygon_id in traci.polygon.getIDList():
                if polygon_id.startswith("pollution_"):
                    traci.polygon.remove(polygon_id)
            simulation.visualize()

            if recorder:
                time.sleep(1)  # esperar un segundo para asegurar que todo esté coloreado antes de capturar
                recorder.capture_frame()
                recorder.update_progress(1)

        step += 1
    logging.info("Simulation finished")
    if recorder:
        recorder.save_video()
        recorder.close_progress_bar()
        if messagebox.askyesno("Eliminar grabación", "¿Desea eliminar la grabación de la simulación?"):
            os.remove(config['output_file'])
            logging.info("Grabación eliminada.")

    traci.close()
    logging.info("Simulation finished")

def apply_config(config):
    logging.info("Applying config")
    try:
        parameters = {
            'wind_speed': config['wind_speed'],
            'wind_direction': config['wind_direction'],
            'grid_resolution': config['grid_resolution'],
            'stability_class': config['stability_class'],
            'emission_factor': config['emission_factor'],
            'update_interval': config['update_interval'],
            'total_steps': config['total_steps'],
            'temperature': config['temperature'],
            'humidity': config['humidity'],
            'chimney_height': config['chimney_height'],
            'deposition_rate': config['deposition_rate']
        }

        config = {
            'sumo_config': config['sumo_config'],
            'parameters': parameters,
            'record_simulation': config['record_simulation'],
            'output_file': config['output_file'],
            'grid_resolution': config['grid_resolution'],
            'wind_speed': config['wind_speed'],
            'wind_direction': config['wind_direction'],
            'stability_class': config['stability_class'],
            'emission_factor': config['emission_factor'],
            'update_interval': config['update_interval'],
            'total_steps': config['total_steps'],
            'temperature': config['temperature'],
            'humidity': config['humidity'],
            'chimney_height': config['chimney_height'],
            'deposition_rate': config['deposition_rate']
        }

        estimated_time = estimate_simulation_time(config)
        if messagebox.askyesno("Confirmación",
                               f"La simulación tardará aproximadamente {estimated_time:.2f} minutos. ¿Desea continuar?"):
            threading.Thread(target=run_simulation, args=(config,)).start()
    except Exception as e:
        messagebox.showerror("Error", f"Error al aplicar la configuración: {str(e)}")
        logging.error(f"Error al aplicar la configuración: {str(e)}")
    logging.info("Config applied")

if __name__ == "__main__":
    logging.info("Starting main")
    root = tk.Tk()
    logging.info("Starting contamination config plugin")
    app = ContaminationConfigPlugin(root, apply_config)
    logging.info("Running main loop")
    root.mainloop()
    logging.info("Main loop finished")