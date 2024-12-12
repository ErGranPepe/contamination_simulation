import gzip
import traci
import numpy as np
import vpython as vp
import xml.etree.ElementTree as ET
import os
import math

class PollutionSimulation3D:
    def __init__(self, sumo_config_path):
        self.sumo_config_path = sumo_config_path
        self.load_sumo_config()
        self.init_simulation()
        self.init_visualization()

    def load_sumo_config(self):
        print(f"Loading SUMO config from: {self.sumo_config_path}")
        tree = ET.parse(self.sumo_config_path)
        root = tree.getroot()
        net_file = root.find(".//net-file").get("value")
        self.net_path = os.path.abspath(os.path.join(os.path.dirname(self.sumo_config_path), net_file))
        
        if not os.path.exists(self.net_path):
            raise FileNotFoundError(f"Network file not found: {self.net_path}")

        if self.net_path.endswith('.gz'):
            with gzip.open(self.net_path, 'rb') as f:
                net_tree = ET.parse(f)
        else:
            net_tree = ET.parse(self.net_path)

        net_root = net_tree.getroot()
        location = net_root.find("location")
        
        if location is None:
            raise ValueError("Location information not found in network file")
        
        self.net_boundary = tuple(map(float, location.get("convBoundary", "-100,-100,100,100").split(",")))
        print(f"Network boundary: {self.net_boundary}")

    def init_simulation(self):
        traci.start(["sumo-gui", "-c", self.sumo_config_path])
        self.grid_resolution = 50
        self.height_resolution = 10
        self.pollution_grid = np.zeros((self.grid_resolution, self.grid_resolution, self.height_resolution))
        
        # Check existing vehicles and add some if none exist
        existing_vehicles = traci.vehicle.getIDList()
        print(f"Existing vehicles: {len(existing_vehicles)}")
        
        if len(existing_vehicles) == 0:
            routes = traci.route.getIDList()
            if len(routes) == 0:
                print("No routes found. Please ensure your SUMO configuration includes routes.")
            else:
                for i in range(10):  # Add 10 vehicles
                    veh_id = f"added_veh{i}"
                    try:
                        traci.vehicle.add(veh_id, routes[0])  # Use the first available route
                        print(f"Added vehicle {veh_id}")
                    except traci.exceptions.TraCIException as e:
                        print(f"Could not add vehicle {veh_id}: {e}")

    def init_visualization(self):
        x_center = (self.net_boundary[0] + self.net_boundary[2]) / 2
        y_center = (self.net_boundary[1] + self.net_boundary[3]) / 2
        max_dim = max(self.net_boundary[2] - self.net_boundary[0], self.net_boundary[3] - self.net_boundary[1])
        
        self.scene = vp.canvas(title='3D Pollution Simulation', width=1200, height=800,
                                center=vp.vector(x_center, y_center, 0), range=max_dim / 2)
        
        self.ground = self.create_ground()
        self.pollution_particles = self.create_pollution_particles()

    def create_ground(self):
        x_range = self.net_boundary[2] - self.net_boundary[0]
        y_range = self.net_boundary[3] - self.net_boundary[1]
        
        ground = vp.box(pos=vp.vector((self.net_boundary[0] + self.net_boundary[2]) / 2,
                                       (self.net_boundary[1] + self.net_boundary[3]) / 2, 
                                       0),
                         size=vp.vector(x_range, y_range, 1), color=vp.color.green)
        
        return ground

    def create_pollution_particles(self):
        particles = []
        
        for i in range(self.grid_resolution):
            for j in range(self.grid_resolution):
                x = self.net_boundary[0] + (i / float(self.grid_resolution)) * (self.net_boundary[2] - self.net_boundary[0])
                y = self.net_boundary[1] + (j / float(self.grid_resolution)) * (self.net_boundary[3] - self.net_boundary[1])
                particle = vp.sphere(pos=vp.vector(x, y, 5), radius=5, color=vp.color.red, opacity=0.5)
                particles.append(particle)
                
        return particles

    def update_pollution(self):
        # Decaimiento de la contaminación
        self.pollution_grid *= 0.99  
        
        vehicles = traci.vehicle.getIDList()
        
        for vehicle_id in vehicles:
            x, y = traci.vehicle.getPosition(vehicle_id)
            emission = self.calculate_emission(vehicle_id)
            
            i = int((x - self.net_boundary[0]) / (self.net_boundary[2] - self.net_boundary[0]) * self.grid_resolution)
            j = int((y - self.net_boundary[1]) / (self.net_boundary[3] - self.net_boundary[1]) * self.grid_resolution)

            if 0 <= i < self.grid_resolution and 0 <= j < self.grid_resolution:
                # Aumentar el efecto de la emisión en la cuadrícula de contaminación
                for h in range(self.height_resolution):
                    concentration_factor = max(0.1, (h + 1) / float(self.height_resolution))  # Factor de concentración por altura
                    pollution_concentration = emission * concentration_factor
                    self.pollution_grid[i, j, h] += pollution_concentration

    def calculate_emission(self, vehicle_id):
        speed = traci.vehicle.getSpeed(vehicle_id)
        emission_rate = max(0.01, speed / 50)  # Ejemplo simple de tasa de emisión
        return emission_rate

    def update_visualization(self):
        max_pollution = np.max(self.pollution_grid)

        if max_pollution > 0:
            for i, particle in enumerate(self.pollution_particles):
                x_index = i % self.grid_resolution
                y_index = i // self.grid_resolution
                
                concentration = np.sum(self.pollution_grid[x_index, y_index])  # Sumar a través de todas las alturas
                
                particle.radius = min(10, concentration * 2)  # Ajustar el tamaño del radio basado en la concentración
                particle.opacity = min(1, concentration / max_pollution)  
                hue = (1 - concentration / max_pollution) * 0.4  
                particle.color = vp.color.hsv_to_rgb(vp.vector(hue, 1, 1))

    def run_simulation(self, steps=1000):
        import time
        
        time.sleep(2)  # Esperar para que se abra la ventana de VPython
        
        try:
            for step in range(steps):
                print(f"Step {step}")
                traci.simulationStep()  
                
                if step % 10 == 0:  
                    self.update_pollution()
                
                # Actualizar visualización al final del ciclo
                if step % 10 == 9:  
                    self.update_visualization()
                    
            print("Simulation finished.")

        except Exception as e:
            print(f"Error during simulation: {e}")
        
        finally:
            traci.close()

# Uso de la clase con el archivo .sumocfg correcto.
if __name__ == "__main__":
    sim_config_path = r"C:\Users\mario\OneDrive\Escritorio\TFG_NOX\simulacion_SUMO.sumocfg"
    simulation_3d = PollutionSimulation3D(sim_config_path)
    simulation_3d.run_simulation()
