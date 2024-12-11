import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traci
import math
import random
import cv2 

class ImprovedCS:
    def __init__(self, config):
        self.config = config
        self.grid_resolution = config['grid_resolution']
        self.pollution_grid = [[0 for _ in range(self.grid_resolution)] for _ in range(self.grid_resolution)]
        self.wind_grid = [[[0, 0] for _ in range(self.grid_resolution)] for _ in range(self.grid_resolution)]
        self.nox_grid = [[0 for _ in range(self.grid_resolution)] for _ in range(self.grid_resolution)]
        self.net_bounds = traci.simulation.getNetBoundary()
        self.x_min, self.y_min = self.net_bounds[0]
        self.x_max, self.y_max = self.net_bounds[1]
        self.wind_speed = config['wind_speed']
        self.wind_direction = math.radians(config['wind_direction'])
        self.stability_class = config['stability_class']
        self.emission_factor = config['emission_factor']
        self.current_layer = 'pollution'
        self.recording = config['recording']
        self.video_writer = None

    def update(self):
        self._decay_pollutants()
        self._update_wind_field()
        self._calculate_emissions()

    def _decay_pollutants(self):
        decay_factor = 0.99
        for i in range(self.grid_resolution):
            for j in range(self.grid_resolution):
                self.pollution_grid[i][j] *= decay_factor
                self.nox_grid[i][j] *= decay_factor

    def _update_wind_field(self):
        for i in range(self.grid_resolution):
            for j in range(self.grid_resolution):
                angle = self.wind_direction + random.gauss(0, 0.1)
                speed = self.wind_speed + random.gauss(0, 0.5)
                self.wind_grid[i][j] = [speed * math.cos(angle), speed * math.sin(angle)]

    def _calculate_emissions(self):
        vehicles = traci.vehicle.getIDList()
        for vehicle in vehicles:
            x, y = traci.vehicle.getPosition(vehicle)
            speed = traci.vehicle.getSpeed(vehicle)
            emission_rate = self._calculate_emission_rate(speed)
            self._disperse_pollutant(x, y, emission_rate)

    def _calculate_emission_rate(self, speed):
        base_emission = 0.1
        speed_factor = 1 + 0.05 * max(0, speed - 20)
        return base_emission * speed_factor * self.emission_factor

    def _disperse_pollutant(self, x, y, emission_rate):
        for i in range(self.grid_resolution):
            for j in range(self.grid_resolution):
                rx, ry = self._get_receptor_coordinates(i, j)
                distance = math.hypot(rx - x, ry - y)
                if distance < 1:
                    continue
                concentration = self._gaussian_plume(x, y, rx, ry, emission_rate)
                self.pollution_grid[i][j] += concentration
                self.nox_grid[i][j] += concentration * 0.7

    def _gaussian_plume(self, sx, sy, rx, ry, emission_rate):
        wind_u, wind_v = self._get_wind_at_point(rx, ry)
        wind_speed = math.hypot(wind_u, wind_v)
        wind_direction = math.atan2(wind_v, wind_u)
        dx = rx - sx
        dy = ry - sy
        x = dx * math.cos(wind_direction) + dy * math.sin(wind_direction)
        y = -dx * math.sin(wind_direction) + dy * math.cos(wind_direction)
        sigma_y, sigma_z = self._calculate_dispersion_coefficients(x)
        return (emission_rate / (2 * math.pi * wind_speed * sigma_y * sigma_z)) * \
               math.exp(-0.5 * (y / sigma_y) ** 2) * \
               (math.exp(-0.5 * (1.5 / sigma_z) ** 2) + math.exp(-0.5 * (1.5 / sigma_z) ** 2))

    def _calculate_dispersion_coefficients(self, distance):
        stability_params = {
            'A': (0.22, 0.20), 'B': (0.16, 0.12), 'C': (0.11, 0.08),
            'D': (0.08, 0.06), 'E': (0.06, 0.03), 'F': (0.04, 0.016)
        }
        
        a, b = stability_params.get(self.stability_class, (0.10, 0.05))
        sigma_y = a * distance * (1 + 0.0001 * distance) ** (-0.5)
        sigma_z = b * distance * (1 + 0.0001 * distance) ** (-0.5)
        return sigma_y, sigma_z

    def _get_wind_at_point(self, x, y):
        i = min(self.grid_resolution - 1, max(0, int((y - self.y_min) / (self.y_max - self.y_min) * self.grid_resolution)))
        j = min(self.grid_resolution - 1, max(0, int((x - self.x_min) / (self.x_max - self.x_min) * self.grid_resolution)))
        return self.wind_grid[i][j]

    def _get_receptor_coordinates(self, i, j):
        rx = self.x_min + (j + 0.5) * (self.x_max - self.x_min) / self.grid_resolution
        ry = self.y_min + (i + 0.5) * (self.y_max - self.y_min) / self.grid_resolution
        return rx, ry

    def visualize(self):
        if self.current_layer == 'pollution':
            self._visualize_pollution()
        elif self.current_layer == 'wind_speed':
            self._visualize_wind_speed()
        elif self.current_layer == 'wind_direction':
            self._visualize_wind_direction()
        elif self.current_layer == 'nox':
            self._visualize_nox()

    def _visualize_pollution(self):
        self._visualize_grid(self.pollution_grid, "pollution")

    def _visualize_wind_speed(self):
        wind_speed_grid = [[math.hypot(u, v) for u, v in row] for row in self.wind_grid]
        self._visualize_grid(wind_speed_grid, "wind_speed")

    def _visualize_wind_direction(self):
        wind_dir_grid = [[math.atan2(v, u) for u, v in row] for row in self.wind_grid]
        self._visualize_grid(wind_dir_grid, "wind_direction")

    def _visualize_nox(self):
        self._visualize_grid(self.nox_grid, "nox")

    def _visualize_grid(self, grid, layer_name):
        max_value = max(max(row) for row in grid)
        if max_value == 0:
            return
        cell_width = (self.x_max - self.x_min) / self.grid_resolution
        cell_height = (self.y_max - self.y_min) / self.grid_resolution
        for i in range(0, self.grid_resolution, 2):
            for j in range(0, self.grid_resolution, 2):
                value = sum(sum(grid[i+di][j+dj] for dj in range(2)) for di in range(2)) / 4
                if value > 0:
                    x, y = self.x_min + j * cell_width, self.y_min + i * cell_height
                    color = self._value_to_color(value / max_value)
                    polygon_id = f"{layer_name}_{i}_{j}"
                    shape = [(x, y), (x + cell_width * 2, y), (x + cell_width * 2, y + cell_height * 2),
                             (x, y + cell_height * 2)]
                    traci.polygon.add(polygon_id, shape, color, True, layer_name)

    @staticmethod
    def _value_to_color(value):
        hue = (1 - value) * 0.4
        r, g, b = ImprovedCS._hsv_to_rgb(hue, 1, 1)
        return int(r * 255), int(g * 255), int(b * 255), int(255 * min(1, value * 5))

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0: return v, t, p
        if i == 1: return q, v, p
        if i == 2: return p, v, t
        if i == 3: return p, q, v
        if i == 4: return t, p, v
        if i == 5: return v, p, q

    def start_recording(self, filename):
        self.video_writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), 20, (640, 480))

    def stop_recording(self):
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def record_frame(self, frame):
        if self.video_writer:
            self.video_writer.write(frame)

class ImprovedContaminationConfigPlugin:
    def __init__(self, master):
        self.master = master
        self.master.title("Improved Contamination Simulation Config")
        self.config = {
            'sumo_config': '',
            'grid_resolution': 100,
            'wind_speed': 5.0,
            'wind_direction': 0,
            'stability_class': 'D',
            'emission_factor': 1.0,
            'total_steps': 1000,
            'update_interval': 10,
            'recording': False
        }
        self.simulation = None
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.general_frame = ttk.Frame(self.notebook)
        self.simulation_frame = ttk.Frame(self.notebook)
        self.visualization_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.general_frame, text='General')
        self.notebook.add(self.simulation_frame, text='Simulation')
        self.notebook.add(self.visualization_frame, text='Visualization')

        self.create_general_widgets()
        self.create_simulation_widgets()
        self.create_visualization_widgets()

        ttk.Button(self.master, text="Start Simulation", command=self.start_simulation).pack(pady=10)

    def create_visualization_widgets(self):
        ttk.Label(self.visualization_frame, text="Select Visualization Layer:").grid(row=0, column=0, padx=5, pady=5)
        self.layer_combobox = ttk.Combobox(self.visualization_frame, values=['pollution', 'wind_speed', 'wind_direction', 'nox'])
        self.layer_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.layer_combobox.current(0)

    def create_general_widgets(self):
        ttk.Label(self.general_frame, text="SUMO Config File:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.sumo_config_entry = ttk.Entry(self.general_frame, textvariable=tk.StringVar(value=self.config['sumo_config']))
        self.sumo_config_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        ttk.Button(self.general_frame, text="Browse", command=self.browse_sumo_config).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.general_frame, text="Grid Resolution:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.grid_resolution_slider = ttk.Scale(self.general_frame, from_=50, to=200, orient=tk.HORIZONTAL)
        self.grid_resolution_slider.set(self.config['grid_resolution'])
        self.grid_resolution_slider.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        self.time_estimate_label = ttk.Label(self.general_frame, text="Estimated simulation time: N/A")
        self.time_estimate_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        ttk.Button(self.general_frame, text="Select Output Video", command=self.select_output_video).grid(row=3, column=0, columnspan=2, pady=5)

    def create_simulation_widgets(self):
        ttk.Label(self.simulation_frame, text="Wind Speed (m/s):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.wind_speed_slider = ttk.Scale(self.simulation_frame, from_=0, to=20, orient=tk.HORIZONTAL)
        self.wind_speed_slider.set(self.config['wind_speed'])
        self.wind_speed_slider.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(self.simulation_frame, text="Wind Direction (degrees):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.wind_direction_slider = ttk.Scale(self.simulation_frame, from_=0, to=359, orient=tk.HORIZONTAL)
        self.wind_direction_slider.set(self.config['wind_direction'])
        self.wind_direction_slider.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label (self.simulation_frame, text="Stability Class:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.stability_class_entry = ttk.Entry(self.simulation_frame, textvariable=tk.StringVar(value=self.config['stability_class']))
        self.stability_class_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(self.simulation_frame, text="Emission Factor:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.emission_factor_slider = ttk.Scale(self.simulation_frame, from_=0, to=10, orient=tk.HORIZONTAL)
        self.emission_factor_slider.set(self.config['emission_factor'])
        self.emission_factor_slider.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(self.simulation_frame, text="Total Steps:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.total_steps_slider = ttk.Scale(self.simulation_frame, from_=100, to=5000, orient=tk.HORIZONTAL)
        self.total_steps_slider.set(self.config['total_steps'])
        self.total_steps_slider.grid(row=4, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(self.simulation_frame, text="Update Interval:").grid(row=5, column=0, sticky='w', padx=5, pady=5)
        self.update_interval_slider = ttk.Scale(self.simulation_frame, from_=1, to=60, orient=tk.HORIZONTAL)
        self.update_interval_slider.set(self.config['update_interval'])
        self.update_interval_slider.grid(row=5, column=1, sticky='ew', padx=5, pady=5)

    def start_simulation(self):
        self.config['total_steps'] = int(self.total_steps_slider.get())
        self.config['update_interval'] = int(self.update_interval_slider.get())
        
        
        self.simulation = ImprovedCS(self.config)  
        
        
        output_video = "output_video.mp4"  
        self.simulation.start_recording(output_video)  
        
        threading.Thread(target=self.run_simulation).start()

    def run_simulation(self):
        try:
            traci.start(["sumo-gui", "-c", self.config['sumo_config']])
            for step in range(self.config['total_steps']):
                traci.simulationStep()
                self.simulation.update()
                
                if step % self.config['update_interval'] == 0:
                    self.simulation.current_layer = 'pollution' 
                    self.simulation.visualize()
                    
                    
                    if self.config['recording']:
                        frame = self.capture_frame()
                        self.simulation.record_frame(frame)

            if self.config['recording']:
                self.simulation.stop_recording()
                
            traci.close()
            messagebox.showinfo("Simulation Complete", "The simulation has finished successfully.")
        except Exception as e:
            messagebox.showerror("Simulation Error", f"An error occurred during the simulation: {str(e)}")

    def capture_frame(self):
        return None

    def browse_sumo_config(self):
        filename = filedialog.askopenfilename(filetypes=[("SUMO Config Files", "*.sumo.cfg"), ("All Files", "*.*")])
        if filename:
            self.sumo_config_entry.delete(0, tk.END)
            self.sumo_config_entry.insert(0, filename)

    def select_output_video(self):
        filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if filename:
            self.config['recording'] = True
            self.sumo_config_entry.delete(0, tk.END)
            self.sumo_config_entry.insert(0, filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImprovedContaminationConfigPlugin(root)
    root.mainloop()
