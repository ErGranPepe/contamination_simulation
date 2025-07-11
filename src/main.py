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
from modules.sensitivity_analysis import SensitivityAnalyzer, create_sensitivity_wrapper
from modules.advanced_cfd import AdvancedCFD, create_advanced_cfd_simulator
from modules.validation_module import ValidationModule, create_validation_module
import traci
import threading
from utils.logger import setup_logger
from utils.validation import validate_simulation_config
import matplotlib.pyplot as plt
import numpy as np
from ui.control_panel import ControlPanel


# Configurar el sistema de logging centralizado
logger = setup_logger('simulation', 'simulation.log')

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

import threading

def run_simulation(config):
    """
    Ejecuta la simulación de contaminación urbana acoplada a SUMO.
    
    Args:
        config (dict): Configuración completa de la simulación, incluyendo parámetros físicos, meteorológicos y de grabación.
    
    Características:
        - CFD multiespecie optimizado en C (advección-difusión, meteorología avanzada).
        - Exportación automática a CSV y VTK para todas las especies.
        - Grabación de vídeo con overlays técnicos y animaciones.
        - Logging técnico, profiling y validación avanzada.
        - Integración total con la WebApp Flask para visualización y análisis científico.
    """
    logger.info("Starting SUMO...")
    
    try:
        # Iniciar SUMO con la interfaz gráfica
        traci.start([r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe", "-c", config['sumo_config']])
        logger.info(f"SUMO started with config: {config['sumo_config']}")
    except Exception as e:
        logger.error(f"Error starting SUMO: {e}")
        messagebox.showerror("Error", f"Error al iniciar SUMO: {str(e)}")
        return
        
    logger.info("Connecting to TraCI...")
    
    # Inicializar el simulador de contaminación y medir el tiempo
    start_time = time.time()
    simulation = CS(config)
    init_time = time.time() - start_time
    logger.info(f"CS initialized in {init_time:.3f}s")

    # Log if using C module or not
    if use_cs_module:
        logger.info("Simulation running with C optimized module.")
    else:
        logger.info("Simulation running with Python fallback module.")

    # Inicializar grabador si se ha solicitado
    recorder = None
    if config['record_simulation']:
        logger.info("Initializing recorder...")
        try:
            recorder = SimulationRecorder(
                config['sumo_config'], 
                config['parameters'],
                output_file=config['output_file'] if config['output_file'] else None
            )
            logger.info(f"Recorder initialized with output file: {recorder.output_file}")
        except Exception as e:
            logger.error(f"Error initializing recorder: {e}")
            messagebox.showerror("Error", f"Error al inicializar el grabador: {str(e)}")
            recorder = None

    # Variables para sincronización entre hilos
    visualize_event = threading.Event()
    update_lock = threading.Lock()
    visualize_lock = threading.Lock()
    stop_event = threading.Event()

    # Variables para compartir tiempos
    timing_data_shared = {
        'update_time': 0,
        'visualize_time': 0,
        'capture_frame_time': 0,
        'step': 0
    }

    def simulation_thread():
        step = 0
        update_times = []
        detailed_log = open("detailed_timing.log", "w")
        detailed_log.write("step,update_time,visualize_time,capture_frame_time\n")

        # --- NUEVO: obtener species_list de la config ---
        species_list = config.get('species_list', ['NOx'])
        final_step = 0  # Para exportación tras la simulación

        # --- NUEVO: Guardar evolución temporal de cada especie para análisis web ---
        species_evolution = {sp: [] for sp in species_list}
        steps_evolution = []

        while step < config['parameters']['total_steps'] and traci.simulation.getMinExpectedNumber() > 0 and not stop_event.is_set():
            t_step_start = time.perf_counter()
            traci.simulationStep()

            # --- Actualización CFD vectorizada y multiespecie con C puro ---
            with update_lock:
                wind_field = config.get('wind_field', None)  # Campo de viento espacialmente variable
                diffusion_field = config.get('diffusion_field', None)  # Campo de difusión variable
                try:
                    # Se fuerza el uso del método C vectorizado multiespecie
                    if hasattr(simulation, 'update_pollution_vectorized_multi'):
                        simulation.update_pollution_vectorized_multi(
                            dt=1.0,
                            diffusion_coeff=2.0,
                            wind_field=wind_field,
                            diffusion_field=diffusion_field,
                            use_c_module=True  # Forzar C siempre
                        )
                    else:
                        simulation.update(use_vectorized=True, dt=1.0, diffusion_coeff=2.0, z_layers=1)
                except Exception as e:
                    logger.error(f"Error en actualización C vectorizada: {e}")
                    # Fallback solo si es absolutamente necesario
                    simulation.update(use_vectorized=True, dt=1.0, diffusion_coeff=2.0, z_layers=1)
                timing_data_shared['update_time'] = time.perf_counter() - t_step_start
                timing_data_shared['step'] = step

                # Visualizar solo la primera especie (ejemplo: NOx)
                if hasattr(simulation, 'pollution_grids'):
                    simulation.pollution_grid = simulation.pollution_grids[species_list[0]]

                    # Guardar evolución temporal (media por paso) de cada especie
                    for sp in species_list:
                        grid = simulation.pollution_grids.get(sp)
                        if grid is not None:
                            mean_val = float(np.mean(grid))
                            species_evolution[sp].append(mean_val)
                    steps_evolution.append(step)

                # Visualización asíncrona o por lotes para no ralentizar
                if step % max(1, config['parameters']['update_interval']//2) == 0:
                    simulation.visualize()

                if recorder and (step % config['parameters']['update_interval'] == 0):
                    try:
                        recorder.capture_frame()
                        recorder.update_progress(config['parameters']['update_interval'])
                    except Exception as e:
                        logger.error(f"Error capturing frame: {e}")

            update_times.append(timing_data_shared['update_time'])
            if step % config['parameters']['update_interval'] == 0:
                visualize_event.set()
            with visualize_lock:
                detailed_log.write(f"{step},{timing_data_shared['update_time']:.6f},{timing_data_shared['visualize_time']:.6f},{timing_data_shared['capture_frame_time']:.6f}\n")
                detailed_log.flush()
            if len(update_times) >= 10:
                avg_update_time = sum(update_times) / len(update_times)
                max_update_time = max(update_times)
                logger.info(f"Rendimiento: {avg_update_time*1000:.2f}ms/actualización (max: {max_update_time*1000:.2f}ms)")
                update_times = []
            step += 1
            final_step = step

        detailed_log.close()
        stop_event.set()
        logger.info(f"Simulation finished after {step} steps")
        # Exportar todas las especies a VTK y CSV
        try:
            if hasattr(simulation, 'export_to_vtk_multi'):
                simulation.export_to_vtk_multi(filename_prefix="pollution_grid", step=final_step)
                logger.info(f"Exported all species to VTK")
            # Exportar a CSV
            if hasattr(simulation, 'pollution_grids'):
                for species, grid in simulation.pollution_grids.items():
                    np.savetxt(f"pollution_grid_{species}_{final_step}.csv", grid, delimiter=",", fmt="%.6e")
                    logger.info(f"Exported {species} to CSV")
            # Guardar evolución temporal para análisis web (JSON y CSV)
            if steps_evolution and species_evolution:
                import json
                import csv
                evo_data = {
                    'steps': steps_evolution,
                    'species': {sp: vals for sp, vals in species_evolution.items()}
                }
                with open("pollution_evolution.json", "w", encoding="utf-8") as f:
                    json.dump(evo_data, f, indent=2)
                logger.info("Evolución temporal guardada en pollution_evolution.json")
                # Exportar también a CSV para análisis científico externo
                csv_path = "pollution_evolution.csv"
                with open(csv_path, "w", newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    header = ["step"] + list(species_evolution.keys())
                    writer.writerow(header)
                    for i, step_val in enumerate(steps_evolution):
                        row = [step_val]
                        for sp in species_evolution.keys():
                            vals = species_evolution[sp]
                            row.append(vals[i] if i < len(vals) else '')
                        writer.writerow(row)
                logger.info(f"Evolución temporal exportada a {csv_path}")
        except Exception as e:
            logger.error(f"Error exporting results: {e}")

        return species_list, final_step

    def visualization_thread():
        while not stop_event.is_set():
            # Esperar señal para visualizar
            visualize_event.wait()
            visualize_event.clear()

            with update_lock:
                start_visualize = time.perf_counter()
                # Limpiar polígonos antiguos
                for polygon_id in traci.polygon.getIDList():
                    if polygon_id.startswith("pollution_"):
                        traci.polygon.remove(polygon_id)

                visualize_time = simulation.visualize()
                timing_data_shared['visualize_time'] = visualize_time

            with visualize_lock:
                if recorder:
                    try:
                        start_capture = time.perf_counter()
                        recorder.capture_frame()
                        capture_frame_time = time.perf_counter() - start_capture
                        timing_data_shared['capture_frame_time'] = capture_frame_time
                        recorder.update_progress(config['parameters']['update_interval'])
                    except Exception as e:
                        logger.error(f"Error capturing frame: {e}")

    # Crear y arrancar hilos
    sim_thread = threading.Thread(target=simulation_thread, name="SimulationThread")
    vis_thread = threading.Thread(target=visualization_thread, name="VisualizationThread")

    sim_thread.start()
    vis_thread.start()

    sim_thread.join()
    vis_thread.join()

    # Recuperar species_list y final_step del hilo de simulación
    # (como no se puede devolver de un hilo, se almacena en variables globales)
    # Solución: definir variables fuera y modificarlas dentro del hilo, o usar un objeto compartido
    # Aquí, para simplicidad, recalculamos species_list y final_step
    species_list = config.get('species_list', ['NOx'])
    final_step = config['parameters']['total_steps']

    # Guardar el video si estábamos grabando
    if recorder:
        try:
            logger.info("Saving video...")
            if hasattr(simulation, 'pollution_grids'):
                for species, grid in simulation.pollution_grids.items():
                    recorder.output_file = f"video_{species}.mp4"
                    success = recorder.save_video(species_name=species, grid=grid, step=final_step)
                    if success:
                        logger.info(f"Video saved to {recorder.output_file}")
                    else:
                        logger.warning(f"No video saved for {species}")
            else:
                success = recorder.save_video()
                if success:
                    logger.info(f"Video saved to {recorder.output_file}")
                else:
                    logger.warning("No video saved")
            recorder.close_progress_bar()
            if hasattr(simulation, 'pollution_grids'):
                recorder.visualize_heatmap(simulation.pollution_grids[species_list[0]])
            else:
                recorder.visualize_heatmap(simulation.pollution_grid)
            if messagebox.askyesno("Eliminar grabación", "¿Desea eliminar la grabación de la simulación?"):
                if os.path.exists(recorder.output_file):
                    os.remove(recorder.output_file)
                    logger.info("Recording deleted.")
                else:
                    logger.warning(f"Could not find recording file: {recorder.output_file}")
        except Exception as e:
            logger.error(f"Error saving video: {e}")
            messagebox.showerror("Error", f"Error al guardar el video: {str(e)}")

    # Cerrar la conexión con SUMO
    traci.close()
    logger.info("SUMO connection closed")

    # Run timing analysis automatically after simulation finishes
    try:
        import src.modules.timing_analysis as timing_analysis
        timing_analysis.analyze_timing_log()
    except Exception as e:
        logger.error(f"Error running timing analysis: {e}")

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
        logger.error(f"Error showing control panel: {e}")

def apply_config(config):
    """
    Valida y aplica la configuración para iniciar la simulación.
    
    Args:
        config: Diccionario con la configuración de la simulación
    """
    logger.info("Applying config")
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

        # Validar configuración básica y parámetros
        errors = validate_simulation_config(complete_config)
        if errors:
            messagebox.showerror("Error de configuración", "\n".join(errors))
            logger.error(f"Errores de configuración: {'; '.join(errors)}")
            return

        # Estimar tiempo de simulación y pedir confirmación
        estimated_time = estimate_simulation_time(complete_config)
        if messagebox.askyesno("Confirmación",
                               f"La simulación tardará aproximadamente {estimated_time:.2f} minutos. ¿Desea continuar?"):
            # Iniciar la simulación en un hilo separado para no bloquear la GUI
            threading.Thread(target=run_simulation, args=(complete_config,)).start()
    except Exception as e:
        messagebox.showerror("Error", f"Error al aplicar la configuración: {str(e)}")
        logger.error(f"Error al aplicar la configuración: {str(e)}")
    logger.info("Config applied")

if __name__ == "__main__":
    logger.info("Starting application")

    # Crear ventana principal de la aplicación
    root = tk.Tk()

    # Inicializar el plugin de configuración
    logger.info("Initializing configuration plugin")
    app = ContaminationConfigPlugin(root, apply_config)

    # Remove control panel from initial GUI; it will be shown after simulation finishes

    # Configure grid weights to allow resizing if needed
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Iniciar el bucle principal de la interfaz gráfica
    logger.info("Starting GUI main loop")
    root.mainloop()

    logger.info("Application closed")
