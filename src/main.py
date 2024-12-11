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

def run_simulation(config):
    
    print("Starting SUMO...")
    traci.start([r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe", "-c", config['sumo_config']])
    print("SUMO started, connecting to TraCI...")
    simulation = CS(config)
    recorder = SimulationRecorder(config['output_file']) if config['record_simulation'] else None

    step = 0
    while step < config['total_steps'] and traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        simulation.update()

        if step % config['update_interval'] == 0:
            for polygon_id in traci.polygon.getIDList():
                if polygon_id.startswith("pollution_"):
                    traci.polygon.remove(polygon_id)
            simulation.visualize()

            if recorder:
                time.sleep(1)  # esperar un segundo para asegurar que todo esté coloreado antes de capturar
                recorder.capture_frame()

        step += 1

    if recorder:
        recorder.save_video()
        if messagebox.askyesno("Eliminar grabación", "¿Desea eliminar la grabación de la simulación?"):
            os.remove(config['output_file'])
            print("Grabación eliminada.")

    traci.close()

def apply_config(config):
    """Inicia un hilo para ejecutar la simulación con la configuración dada."""
    threading.Thread(target=run_simulation, args=(config,)).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ContaminationConfigPlugin(root, apply_config)
    root.mainloop()
