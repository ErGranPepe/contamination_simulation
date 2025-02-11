import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ui.toolTip import ToolTip
from config_manager import save_config, load_config

class ConfigGUI:
    """
    Interfaz gráfica para configurar parámetros de simulación.
    """

    def __init__(self, root, apply_callback):
        """
        Inicializa la GUI.

        Args:
            root (tk.Tk): Ventana principal de Tkinter.
            apply_callback (callable): Función que se ejecutará al aplicar la configuración.
        """
        self.root = root
        self.root.title("Configuración de Simulación")
        self.apply_callback = apply_callback
        self.config = {
            "sumo_config_file": "",
            "wind_speed": 0.0,
            "wind_direction": 0,
            "grid_resolution": 100,
            "stability_class": "A",
            "emission_factor": 1.0,
            "update_interval": 1,
            "total_steps": 1000,
            "temperature": 25.0,
            "humidity": 50.0,
            "chimney_height": 10.0,
            "deposition_rate": 0.01,
            "record_simulation": False,
            "output_file": ""
        }

        # Crear el menú
        self._create_menu()

        # Crear el formulario principal
        self._create_form()

    def _create_menu(self):
        """Crea el menú superior."""
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Cargar Configuración", command=self._load_config)
        file_menu.add_command(label="Guardar Configuración", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        menu_bar.add_cascade(label="Archivo", menu=file_menu)
        
        self.root.config(menu=menu_bar)

    def _create_form(self):
        """Crea el formulario principal con los parámetros de simulación."""
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="NSEW")

        # Configuración del archivo SUMO
        ttk.Label(frame, text="Archivo de configuración SUMO:").grid(row=0, column=0, sticky="W")
        self.sumo_file_var = tk.StringVar()
        sumo_entry = ttk.Entry(frame, textvariable=self.sumo_file_var, state="readonly", width=40)
        sumo_entry.grid(row=0, column=1, sticky="W")
        ttk.Button(frame, text="Seleccionar", command=self._select_sumo_file).grid(row=0, column=2)
        
        ToolTip(sumo_entry, text="Selecciona el archivo de configuración SUMO.")

        # Parámetros editables
        parameters = [
            ("Velocidad del viento (m/s)", "wind_speed"),
            ("Dirección del viento (°)", "wind_direction"),
            ("Resolución de la cuadrícula", "grid_resolution"),
            ("Clase de estabilidad (A-F)", "stability_class"),
            ("Factor de emisión", "emission_factor"),
            ("Intervalo de actualización (s)", "update_interval"),
            ("Pasos totales", "total_steps"),
            ("Temperatura (°C)", "temperature"),
            ("Humedad (%)", "humidity"),
            ("Altura de la chimenea (m)", "chimney_height"),
            ("Tasa de deposición", "deposition_rate")
        ]

        self.param_vars = {}
        
        for i, (label_text, param_key) in enumerate(parameters):
            ttk.Label(frame, text=f"{label_text}:").grid(row=i+1, column=0, sticky="W")
            
            if param_key == "stability_class":
                var = tk.StringVar(value=self.config[param_key])
                widget = ttk.Combobox(frame, textvariable=var, values=["A", "B", "C", "D", "E", "F"], state="readonly")
                widget.grid(row=i+1, column=1)
                ToolTip(widget, text=f"Clase de estabilidad atmosférica ({label_text}).")
            
            else:
                var = tk.DoubleVar(value=self.config[param_key]) if isinstance(self.config[param_key], float) else tk.IntVar(value=self.config[param_key])
                widget = ttk.Entry(frame, textvariable=var)
                widget.grid(row=i+1, column=1)
                ToolTip(widget, text=f"Introduce el valor para {label_text}.")
            
            self.param_vars[param_key] = var

        # Checkbox para grabar simulación
        self.record_var = tk.BooleanVar(value=self.config["record_simulation"])
        record_checkbox = ttk.Checkbutton(frame, text="Grabar Simulación", variable=self.record_var)
        record_checkbox.grid(row=len(parameters)+1, column=0, sticky="W")
        
        ToolTip(record_checkbox, text="Marca esta opción para grabar la simulación en un archivo.")

        # Selección del archivo de salida
        ttk.Label(frame, text="Archivo de salida:").grid(row=len(parameters)+2, column=0, sticky="W")
        
        self.output_file_var = tk.StringVar()
        output_entry = ttk.Entry(frame, textvariable=self.output_file_var, width=40)
        output_entry.grid(row=len(parameters)+2, column=1)
        
        ttk.Button(frame, text="Seleccionar", command=self._select_output_file).grid(row=len(parameters)+2, column=2)
        
        ToolTip(output_entry, text="Selecciona el archivo donde se guardará la grabación.")

        # Botón para aplicar y ejecutar la simulación
        apply_button = ttk.Button(frame, text="Aplicar y Ejecutar Simulación", command=self._apply_and_run)
        apply_button.grid(row=len(parameters)+3, columnspan=3)

    def _select_sumo_file(self):
        """Abre un cuadro de diálogo para seleccionar el archivo SUMO."""
        filepath = filedialog.askopenfilename(title="Seleccionar archivo SUMO",
                                              filetypes=[("Archivos SUMO (*.sumocfg)", "*.sumocfg"), ("Todos los archivos", "*.*")])
        
        if filepath:
            self.sumo_file_var.set(filepath)

    def _select_output_file(self):
        """Abre un cuadro de diálogo para seleccionar el archivo de salida."""
        filepath = filedialog.asksaveasfilename(title="Seleccionar archivo de salida",
                                                defaultextension=".txt",
                                                filetypes=[("Archivos de texto (*.txt)", "*.txt"), ("Todos los archivos", "*.*")])
        
        if filepath:
            self.output_file_var.set(filepath)

    def _save_config(self):
        """Guarda la configuración actual en un archivo JSON."""
        try:
            config_data = self._get_current_config()
            filepath = filedialog.asksaveasfilename(title="Guardar configuración",
                                                    defaultextension=".json",
                                                    filetypes=[("Archivos JSON (*.json)", "*.json")])
            
            if filepath:
                save_config(config_data, filepath)
                messagebox.showinfo("Guardar Configuración", f"Configuración guardada en {filepath}")
        
        except Exception as e:
            messagebox.showerror("Error al guardar configuración", str(e))

    def _load_config(self):
        """Carga una configuración desde un archivo JSON."""
        try:
            filepath = filedialog.askopenfilename(title="Cargar configuración",
                                                  filetypes=[("Archivos JSON (*.json)", "*.json")])
            
            if filepath:
                loaded_config = load_config(filepath)
                self._set_current_config(loaded_config)
                messagebox.showinfo("Cargar Configuración", f"Configuración cargada desde {filepath}")
        
        except Exception as e:
            messagebox.showerror("Error al cargar configuración", str(e))

    def _apply_and_run(self):
        """Aplica la configuración actual y ejecuta la simulación."""
        config_data = self._get_current_config()
        
        # Llamar al callback con la configuración actual
        self.apply_callback(config_data)

    def _get_current_config(self):
        """Obtiene la configuración actual desde los widgets."""
        config_data = {
            "sumo_config_file": self.sumo_file_var.get(),
            "record_simulation": self.record_var.get(),
            "output_file": self.output_file_var.get()
        }
        
        for key, var in self.param_vars.items():
            if key == "stability_class":
                config_data[key] = var.get()
            else:
                try:
                    config_data[key] = float(var.get())
                except ValueError:
                    messagebox.showerror("Error de entrada", f"Valor inválido para {key}")
                    return None
        
        return config_data

    def _set_current_config(self, config_data):
        """Establece la configuración cargada en los widgets."""
        self.sumo_file_var.set(config_data.get("sumo_config_file", ""))
        self.record_var.set(config_data.get("record_simulation", False))
        self.output_file_var.set(config_data.get("output_file", ""))
        
        for key, var in self.param_vars.items():
            if key in config_data:
                var.set(config_data[key])

    def run(self):
        """Inicia el bucle principal de la interfaz gráfica."""
        self.root.mainloop()

# Ejemplo de uso
if __name__ == "__main__":
    def dummy_callback(config):
        print("Configuración aplicada:", config)

    root = tk.Tk()
    app = ConfigGUI(root, dummy_callback)
    app.run()
