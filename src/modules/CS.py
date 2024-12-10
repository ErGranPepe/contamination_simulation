import colorsys
import math

import numpy as np
import traci

# CS :  Contamination SImulation
class CS:
    def __init__(self, config):
        self.config = config
        self.pollution_grid = np.zeros((config['grid_resolution'], config['grid_resolution']))
        self.net_bounds = traci.simulation.getNetBoundary()
        self.x_min, self.y_min = self.net_bounds[0]
        self.x_max, self.y_max = self.net_bounds[1]

        self.wind_speed = config['wind_speed']
        self.wind_direction = math.radians(config['wind_direction'])
        self.stability_class = config['stability_class']
        self.emission_factor = config['emission_factor']

    def calculate_dispersion_coefficients(self, distance):
        stability_params = {
            'A': (0.22, 0.20),
            'B': (0.16, 0.12),
            'C': (0.11, 0.08),
            'D': (0.08, 0.06),
            'E': (0.06, 0.03),
            'F': (0.04, 0.016)
        }
        a, b = stability_params.get(self.stability_class, (0.10, 0.05))
        sigma_y = a * distance * (1 + 0.0001 * distance) ** (-0.5)
        sigma_z = b * distance * (1 + 0.0001 * distance) ** (-0.5)
        return sigma_y, sigma_z

    def calculate_plume_rise(self, vehicle_speed):
        return max(2, 0.5 + 0.15 * vehicle_speed)

    def update(self):
        # Decaimiento del contaminante en la cuadrícula
        self.pollution_grid *= 0.99

        vehicles = traci.vehicle.getIDList()

        for vehicle in vehicles:
            x, y = traci.vehicle.getPosition(vehicle)
            vehicle_speed = traci.vehicle.getSpeed(vehicle)
            emission_rate = self.calculate_emission_rate(vehicle_speed)
            plume_height = self.calculate_plume_rise(vehicle_speed)

            # Definir límites para el cálculo de contaminación para optimizar el rendimiento
            i_min = max(0, int((y - self.y_min - 100) / (self.y_max - self.y_min) * self.config['grid_resolution']))
            i_max = min(self.config['grid_resolution'],
                        int((y - self.y_min + 100) / (self.y_max - self.y_min) * self.config['grid_resolution']))
            j_min = max(0, int((x - self.x_min - 100) / (self.x_max - self.x_min) * self.config['grid_resolution']))
            j_max = min(self.config['grid_resolution'],
                        int((x - self.x_min + 100) / (self.x_max - self.x_min) * self.config['grid_resolution']))

            for i in range(i_min, i_max):
                for j in range(j_min, j_max):
                    receptor_x = self.x_min + (j + 0.5) * (self.x_max - self.x_min) / self.config['grid_resolution']
                    receptor_y = self.y_min + (i + 0.5) * (self.y_max - self.y_min) / self.config['grid_resolution']

                    distance = math.sqrt((receptor_x - x) ** 2 + (receptor_y - y) ** 2)

                    if distance < 1:
                        continue

                    wind_direction_to_receptor = math.atan2(receptor_y - y, receptor_x - x)
                    angle_diff = abs(wind_direction_to_receptor - self.wind_direction)

                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff

                    sigma_y, sigma_z = self.calculate_dispersion_coefficients(distance)

                    concentration = (emission_rate / (2 * math.pi * self.wind_speed * sigma_y * sigma_z)) * \
                                    math.exp(-0.5 * (angle_diff / sigma_y) ** 2) * \
                                    (math.exp(-0.5 * ((plume_height) / sigma_z) ** 2) + \
                                     math.exp(-0.5 * ((plume_height) / sigma_z) ** 2))

                    # Acumular la concentración en la cuadrícula
                    self.pollution_grid[i, j] += concentration

    def calculate_emission_rate(self, vehicle_speed):
        base_emission = 0.1
        speed_factor = (1 + 0.05 * (vehicle_speed - 20)) if vehicle_speed > 20 else 1
        return base_emission * speed_factor * self.emission_factor

    def visualize(self):
        max_pollution = np.max(self.pollution_grid)
        if max_pollution == 0:
            return

        cell_width = (self.x_max - self.x_min) / self.config['grid_resolution']
        cell_height = (self.y_max - self.y_min) / self.config['grid_resolution']

        for i in range(0, self.config['grid_resolution'], 2):
            for j in range(0, self.config['grid_resolution'], 2):
                pollution = np.mean(self.pollution_grid[i:i + 2, j:j + 2])
                if pollution > 0:
                    x = self.x_min + j * cell_width
                    y = self.y_min + i * cell_height

                    hue = (1 - pollution / max_pollution) * 0.4
                    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                    color = (int(r * 255), int(g * 255), int(b * 255), int(255 * min(1, pollution / max_pollution * 5)))

                    polygon_id = f"pollution_{i}_{j}"
                    shape = [(x, y), (x + cell_width * 2, y), (x + cell_width * 2, y + cell_height * 2),
                             (x, y + cell_height * 2)]
                    traci.polygon.add(polygon_id, shape, color, True, "pollution_layer")

