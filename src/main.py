"""
Simulación de Contaminación para SUMO - Programa Principal

Este programa proporciona una interfaz gráfica para configurar y ejecutar simulaciones
de dispersión de contaminantes en entornos urbanos utilizando SUMO (Simulation of Urban Mobility).
Utiliza un modelo gaussiano de dispersión optimizado con código C para mayor rendimiento.

Autor: Mario Díaz Gómez
Versión: 2.0
"""

import os
import time
import tkinter as tk
from tkinter import messagebox
from modules.config import ContaminationConfigPlugin
from modules.toolTip import ToolTip
from modules.recorder_fixed import SimulationRecorder  # Módulo de grabación optimizado
from modules.CS_optimized import CS, use_cs_module  # Módulo de simulación de contaminación optimizado
import traci
import threading
import logging
import matplotlib.pyplot as plt
import numpy as np
from ui.control_panel import ControlPanel

# Configurar el sistema de logging
logging.basicConfig(filename='simulation.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def estimate_simulation_time(config):
    """
    Estima el tiempo aproximado que tomará la simulación en minutos.
    
    Args:
        config: Diccionario con la configuración de la simulación
        
    Returns:
        Tiempo estimado en minutos
    """
    total_steps = config['parameters']['total_steps']
    update_interval = config['parameters']['update_interval']
    
    # Factores de estimación (ajustables según rendimiento observado)
    time_per_step = 0.01  # tiempo estimado por paso (segundos)
    visualization_overhead = 0.2  # tiempo estimado para visualización (segundos)
    
    # Cálculo del tiempo estimado
    calculation_time = total_steps * time_per_step
    visualization_time = (total_steps / update_interval) * visualization_overhead
    total_time_seconds = calculation_time + visualization_time
    
    # Convertir a minutos
    return total_time_seconds / 60.0

def run_simulation(config):
    """
    Ejecuta la simulación de contaminación con SUMO.
    
    Args:
        config: Diccionario con la configuración de la simulación
    """
    logging.info("Starting SUMO...")
    
    try:
        # Iniciar SUMO con la interfaz gráfica
        traci.start([r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe", "-c", config['sumo_config']])
        logging.info(f"SUMO started with config: {config['sumo_config']}")
    except Exception as e:
        logging.error(f"Error starting SUMO: {e}")
        messagebox.showerror("Error", f"Error al iniciar SUMO: {str(e)}")
        return
        
    logging.info("Connecting to TraCI...")
    
    # Inicializar el simulador de contaminación y medir el tiempo
    start_time = time.time()
    simulation = CS(config)
    init_time = time.time() - start_time
    logging.info(f"CS initialized in {init_time:.3f}s")

    # Log if using C module or not
    if use_cs_module:
        logging.info("Simulation running with C optimized module.")
    else:
        logging.info("Simulation running with Python fallback module.")

    # Inicializar grabador si se ha solicitado
    recorder = None
    if config['record_simulation']:
        logging.info("Initializing recorder...")
        try:
            recorder = SimulationRecorder(
                config['sumo_config'], 
                config['parameters'],
                output_file=config['output_file'] if config['output_file'] else None
            )
            logging.info(f"Recorder initialized with output file: {recorder.output_file}")
        except Exception as e:
            logging.error(f"Error initializing recorder: {e}")
            messagebox.showerror("Error", f"Error al inicializar el grabador: {str(e)}")
            recorder = None

    # Iniciar la simulación
    logging.info("Starting simulation loop")
    step = 0
    update_times = []  # Para métricas de rendimiento
    detailed_log = open("detailed_timing.log", "w")
    detailed_log.write("step,update_time,visualize_time,capture_frame_time\n")
    
    # Bucle principal de simulación
    while step < config['parameters']['total_steps'] and traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        timing_data = simulation.update()
        update_time = timing_data.get('total_update_time', 0)
        visualize_time = 0
        capture_frame_time = 0
        
        if step % config['parameters']['update_interval'] == 0:
            for polygon_id in traci.polygon.getIDList():
                if polygon_id.startswith("pollution_"):
                    traci.polygon.remove(polygon_id)
            
            visualize_time = simulation.visualize()

            if recorder:
                try:
                    time.sleep(0.5)
                    start_capture = time.perf_counter()
                    recorder.capture_frame()
                    capture_frame_time = time.perf_counter() - start_capture
                    recorder.update_progress(config['parameters']['update_interval'])
                except Exception as e:
                    logging.error(f"Error capturing frame: {e}")
            
            if len(update_times) >= 10:
                avg_update_time = sum(update_times) / len(update_times)
                max_update_time = max(update_times)
                logging.info(f"Rendimiento: {avg_update_time*1000:.2f}ms/actualización (max: {max_update_time*1000:.2f}ms)")
                update_times = []
        
        update_times.append(update_time)
        
        detailed_log.write(f"{step},{update_time:.6f},{visualize_time:.6f},{capture_frame_time:.6f}\n")
        detailed_log.flush()
        
        step += 1
    
    detailed_log.close()
    
    if update_times:
        avg_update_time = sum(update_times) / len(update_times)
        logging.info(f"Rendimiento final: {avg_update_time*1000:.2f}ms/actualización")
    
    logging.info(f"Simulation finished after {step} steps")
    
    # Guardar el video si estábamos grabando
    if recorder:
        try:
            logging.info("Saving video...")
            success = recorder.save_video()
            recorder.close_progress_bar()
            
            if success:
                recorder.visualize_heatmap(simulation.pollution_grid)
                logging.info(f"Video saved to {recorder.output_file}")
                
                if messagebox.askyesno("Eliminar grabación", "¿Desea eliminar la grabación de la simulación?"):
                    if os.path.exists(recorder.output_file):
                        os.remove(recorder.output_file)
                        logging.info("Recording deleted.")
                    else:
                        logging.warning(f"Could not find recording file: {recorder.output_file}")
            else:
                messagebox.showwarning("Advertencia", "No se pudo guardar el video de la simulación.")
        except Exception as e:
            logging.error(f"Error saving video: {e}")
            messagebox.showerror("Error", f"Error al guardar el video: {str(e)}")

    # Cerrar la conexión con SUMO
    traci.close()
    logging.info("SUMO connection closed")

    # Run timing analysis automatically after simulation finishes
    try:
        import src.modules.timing_analysis as timing_analysis
        timing_analysis.analyze_timing_log()
    except Exception as e:
        logging.error(f"Error running timing analysis: {e}")

    # Show control panel after simulation finishes
    try:
        import tkinter as tk
        from ui.control_panel import ControlPanel

        root = tk.Tk()
        root.title("Simulation Timing Control Panel")
        control_panel = ControlPanel(root)
        control_panel.pack(fill='both', expand=True)
        root.mainloop()
    except Exception as e:
        logging.error(f"Error showing control panel: {e}")

def apply_config(config):
    """
    Valida y aplica la configuración para iniciar la simulación.
    
    Args:
        config: Diccionario con la configuración de la simulación
    """
    logging.info("Applying config")
    try:
        # Extraer y organizar los parámetros
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

        # Crear configuración completa
        complete_config = {
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

        # Validar configuración básica
        if not complete_config['sumo_config']:
            messagebox.showerror("Error", "Debe seleccionar un archivo de configuración SUMO.")
            return
            
        # Estimar tiempo de simulación y pedir confirmación
        estimated_time = estimate_simulation_time(complete_config)
        if messagebox.askyesno("Confirmación",
                               f"La simulación tardará aproximadamente {estimated_time:.2f} minutos. ¿Desea continuar?"):
            # Iniciar la simulación en un hilo separado para no bloquear la GUI
            threading.Thread(target=run_simulation, args=(complete_config,)).start()
    except Exception as e:
        messagebox.showerror("Error", f"Error al aplicar la configuración: {str(e)}")
        logging.error(f"Error al aplicar la configuración: {str(e)}")
    logging.info("Config applied")

if __name__ == "__main__":
    logging.info("Starting application")
    
    # Crear ventana principal de la aplicación
    root = tk.Tk()
    
    # Inicializar el plugin de configuración
    logging.info("Initializing configuration plugin")
    app = ContaminationConfigPlugin(root, apply_config)

    # Remove control panel from initial GUI; it will be shown after simulation finishes
    
    # Configure grid weights to allow resizing if needed
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Iniciar el bucle principal de la interfaz gráfica
    logging.info("Starting GUI main loop")
    root.mainloop()
    
    logging.info("Application closed")
