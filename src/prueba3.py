import gzip
import traci
import numpy as np
import vpython as vp
import xml.etree.ElementTree as ET
import os

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

        location = net_tree.getroot().find("location")
        
        if location is None:
            raise ValueError("Location information not found in network file")
        
        self.net_boundary = tuple(map(float, location.get("convBoundary", "-100,-100,100,100").split(",")))
        print(f"Network boundary: {self.net_boundary}")

    def init_simulation(self):
        traci.start(["sumo-gui", "-c", self.sumo_config_path])
        self.grid_resolution = 50
        self.height_resolution = 10
        self.pollution_grid = np.zeros((self.grid_resolution, self.grid_resolution, self.height_resolution))

    def init_visualization(self):
        x_center = (self.net_boundary[0] + self.net_boundary[2]) / 2
        y_center = (self.net_boundary[1] + self.net_boundary[3]) / 2
        max_dim = max(self.net_boundary[2] - self.net_boundary[0], self.net_boundary[3] - self.net_boundary[1])
        
        # Crear la escena de VPython
        self.scene = vp.canvas(title='3D Pollution Simulation', width=1200, height=800,
                                center=vp.vector(x_center, y_center, 0), range=max_dim / 2)

        # Crear el mapa de SUMO
        self.create_map()

    def create_map(self):
        # Dibujar las carreteras del mapa de SUMO
        for edge_id in traci.edge.getIDList():
            try:
                shape = traci.edge.getShape(edge_id)
                points = [vp.vector(x, y, 0) for x, y in shape]
                vp.curve(pos=points, color=vp.color.gray(0.5), radius=1)  # Dibujar las carreteras en gris
            except traci.TraCIException as e:
                print(f"Error processing edge {edge_id}: {e}")

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
                    concentration_factor = max(0.1, (h + 1) / float(self.height_resolution))  
                    pollution_concentration = emission * concentration_factor
                    self.pollution_grid[i, j, h] += pollution_concentration

    def calculate_emission(self, vehicle_id):
        speed = traci.vehicle.getSpeed(vehicle_id)
        emission_rate = max(0.01, speed / 50)  
        return emission_rate

    def update_visualization(self):
        max_pollution = np.max(self.pollution_grid)

        if max_pollution > 0:
            for i in range(len(self.pollution_particles)):
                particle = self.pollution_particles[i]
                x_index = i % self.grid_resolution
                y_index = i // self.grid_resolution
                
                concentration = np.sum(self.pollution_grid[x_index, y_index])  
                
                particle.radius = min(10, concentration * 2)  
                particle.opacity = min(1, concentration / max_pollution)  
                hue = (1 - concentration / max_pollution) * 0.4  
                particle.color = vp.color.hsv_to_rgb(vp.vector(hue, 1, 1))

    def run_simulation(self, steps=1000):
        import time
        
        time.sleep(2)  
        
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

    # Crear partículas de contaminación antes de ejecutar la simulación.
    simulation_3d.pollution_particles = simulation_3d.create_pollution_particles()

    simulation_3d.run_simulation()
