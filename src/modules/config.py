from tkinter import BooleanVar, DoubleVar, IntVar, StringVar, Tk as tk, filedialog, messagebox, ttk
from modules.toolTip import ToolTip

class ContaminationConfigPlugin:
    def __init__(self, master, apply_callback):
        self.master = master
        master.title("Configuración de Simulación de Contaminación")
        self.apply_callback = apply_callback

        
        self.sumo_config = StringVar(value="") 
        self.wind_speed = DoubleVar(value=2.0)
        self.wind_direction = DoubleVar(value=0.0)
        self.grid_resolution = IntVar(value=100)
        self.stability_class = StringVar(value='B')
        self.emission_factor = DoubleVar(value=0.5)
        self.update_interval = IntVar(value=10)
        self.record_simulation = BooleanVar(value=False)
        self.output_file = StringVar(value="simulation_output.mp4")
        self.total_steps = IntVar(value=1000)
        self.temperature = DoubleVar(value=20.0)  
        self.humidity = DoubleVar(value=50.0)      
        self.chimney_height = DoubleVar(value=10.0)  
        self.deposition_rate = DoubleVar(value=0.1)  

        self.create_widgets()

    def create_widgets(self):
        def create_labeled_entry(row, text, variable, tooltip, min_val=None, max_val=None):
            ttk.Label(self.master, text=text).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(self.master, textvariable=variable)
            entry.grid(row=row, column=1, padx=5, pady=2)

            tooltip_label = ttk.Label(self.master, text="ℹ️")
            tooltip_label.grid(row=row, column=2, padx=2)
            ToolTip(tooltip_label, tooltip)

            if min_val is not None and max_val is not None:
                ttk.Label(self.master, text=f"({min_val} - {max_val})").grid(row=row, column=3, padx=2)


        ttk.Label(self.master, text="Configuración de SUMO:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.sumo_entry = ttk.Entry(self.master, textvariable=self.sumo_config, state='readonly')
        self.sumo_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(self.master, text="Seleccionar archivo", command=self.select_sumo_file).grid(row=0, column=2, padx=5, pady=2)

        create_labeled_entry(1, "Velocidad del viento (m/s):", self.wind_speed,
                             "Velocidad del viento en metros por segundo", 0, 30)
        create_labeled_entry(2, "Dirección del viento (grados):", self.wind_direction,
                             "Dirección del viento en grados (0-360)", 0, 360)
        create_labeled_entry(3, "Resolución de la cuadrícula:", self.grid_resolution,
                             "Número de celdas en cada dimensión de la cuadrícula", 50, 500)

        ttk.Label(self.master, text="Clase de estabilidad atmosférica:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        stability_combo = ttk.Combobox(self.master, textvariable=self.stability_class,
                                       values=('A ', 'B', 'C', 'D', 'E', 'F'))
        stability_combo.grid(row=4, column=1, padx=5, pady=2)
        ToolTip(stability_combo, "A: Muy inestable; F: Muy estable")

        create_labeled_entry(5, "Factor de emisión:", self.emission_factor,
                             "Factor multiplicador para las emisiones de los vehículos", 0.1, 2.0)
        create_labeled_entry(6, "Intervalo de actualización (pasos):", self.update_interval,
                             "Número de pasos de simulación entre actualizaciones visuales", 1, 100)
        create_labeled_entry(7, "Número total de pasos:", self.total_steps,
                             "Número total de pasos de la simulación", 100, 100000)

        create_labeled_entry(8, "Temperatura (°C):", self.temperature,
                             "Temperatura en grados Celsius", -30, 50)
        create_labeled_entry(9, "Humedad (%):", self.humidity,
                             "Humedad relativa en porcentaje", 0, 100)
        create_labeled_entry(10, "Altura de chimeneas (m):", self.chimney_height,
                             "Altura de las chimeneas en metros", 0, 100)
        create_labeled_entry(11, "Tasa de deposición:", self.deposition_rate,
                             "Tasa de deposición de contaminantes (g/m²/s)", 0, 1)

        ttk.Checkbutton(self.master, text="Grabar simulación", variable=self.record_simulation).grid(row=12,
                                                                                                     column=0,
                                                                                                     columnspan=2,
                                                                                                     pady=5)
        ttk.Button(self.master, text="Seleccionar archivo de salida", command=self.select_output_file).grid(row=13,
                                                                                                            column=0,
                                                                                                            columnspan=2,
                                                                                                            pady=5)

        ttk.Button(self.master, text="Aplicar y Ejecutar", command=self.apply_config).grid(row=14,
                                                                                           column=0,
                                                                                           columnspan=2,
                                                                                           pady=10)

        # Calcular dimensiones celdas
        self.cell_length_label = ttk.Label(self.master, text="Longitud de cada celda (m):")
        self.cell_length_label.grid(row=15, column=0, sticky="w", padx=5, pady=2)
        self.cell_length_value = ttk.Label(self.master, text="0.0")
        self.cell_length_value.grid(row=15, column=1, sticky="w", padx=5, pady=2)

        self.grid_resolution.trace("w", self.update_cell_length)

    def select_sumo_file(self):
        filename = filedialog.askopenfilename(filetypes=[("SUMO config files", "*.sumocfg")])
        if filename:
            self.sumo_config.set(filename)

    def select_output_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                filetypes=[("MP4 files", "*.mp4")])
        if filename:
            self.output_file.set(filename)

    def apply_config(self):
        try:
            config = {
                'sumo_config': self.sumo_config.get(),
                'wind_speed': self.wind_speed.get(),
                'wind_direction': self.wind_direction.get(),
                'grid_resolution': self.grid_resolution.get(),
                'stability_class': self.stability_class.get(),
                'emission_factor': self.emission_factor.get(),
                'update_interval': self.update_interval.get(),
                'record_simulation': self.record_simulation.get(),
                'output_file': self.output_file.get(),
                'total_steps': self.total_steps.get(),
                'temperature': self.temperature.get(),
                'humidity': self.humidity.get(),
                'chimney_height': self.chimney_height.get(),
                'deposition_rate': self.deposition_rate.get()
            }

            estimated_time = self.estimate_simulation_time(config)
            if messagebox.askyesno("Confirmación",
                                   f"La simulación tardará aproximadamente {estimated_time:.2f} minutos. ¿Desea continuar?"):
                self.apply_callback(config)
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar la configuración: {str(e)}")

    def estimate_simulation_time(self, config):
        time_per_step = 0.1  
        time_per_update = 0.5  # segundos por actualización visual
        total_time = (config['total_steps'] * time_per_step) + \
                     (config['total_steps'] / config['update_interval'] * time_per_update)
        return total_time / 60  

    def update_cell_length(self, *args):
        """Actualiza la longitud de cada celda en función de la resolución de la cuadrícula."""
        grid_resolution = self.grid_resolution.get()
        if grid_resolution > 0:
            # Suponiendo que el tamaño del mapa de SUMO es de 1000 metros por 1000 metros
            map_size = 1000 
            cell_length = map_size / grid_resolution
            self.cell_length_value.config(text=f"{cell_length:.2f}")
        else:
            self.cell_length_value.config(text="0.0")
