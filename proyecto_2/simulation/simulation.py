
import numpy as np
import colorsys
import traci
print(traci.getVersion())


class ContaminationSimulation:
    """
    Clase para gestionar la simulación de dispersión de contaminación en SUMO.
    """

    def __init__(self, config):
        """
        Inicializa la simulación con los parámetros de configuración.

        Args:
            config (dict): Diccionario con los parámetros de configuración.
                - grid_resolution: Resolución de la cuadrícula (metros).
                - wind_speed: Velocidad del viento (m/s).
                - wind_direction: Dirección del viento (grados).
                - stability_class: Clase de estabilidad atmosférica (A-F).
                - emission_factor: Factor de emisión por vehículo.
                - temperature: Temperatura ambiente (°C).
                - humidity: Humedad relativa (%).
                - deposition_rate: Tasa de deposición.
        """
        self.grid_resolution = config["grid_resolution"]
        self.wind_speed = config["wind_speed"]
        self.wind_direction = np.radians(config["wind_direction"])  # Convertir a radianes
        self.stability_class = config["stability_class"]
        self.emission_factor = config["emission_factor"]
        self.temperature = config["temperature"]
        self.humidity = config["humidity"]
        self.deposition_rate = config["deposition_rate"]

        # Conectar a SUMO y obtener límites de la red
        self.network_bounds = self._get_network_bounds()
        
        # Crear una cuadrícula para almacenar los niveles de contaminación
        self.grid = self._create_grid()

    def _get_network_bounds(self):
        """
        Obtiene los límites de la red desde SUMO.

        Returns:
            tuple: Coordenadas mínimas y máximas (xmin, ymin, xmax, ymax).
        """
        edges = traci.edge.getIDList()
        x_coords = []
        y_coords = []

        for edge_id in edges:
            shape = traci.edge.getShape(edge_id)  # Obtener la forma del borde usando su ID
            for x, y in shape:
                x_coords.append(x)
                y_coords.append(y)

        xmin, xmax = min(x_coords), max(x_coords)
        ymin, ymax = min(y_coords), max(y_coords)
        
        return xmin, ymin, xmax, ymax


    def _create_grid(self):
        """
        Crea una matriz NumPy para representar la cuadrícula de contaminación.

        Returns:
            np.ndarray: Matriz inicializada con ceros.
        """
        xmin, ymin, xmax, ymax = self.network_bounds
        x_size = int((xmax - xmin) / self.grid_resolution) + 1
        y_size = int((ymax - ymin) / self.grid_resolution) + 1
        
        return np.zeros((x_size, y_size))

    def _calculate_dispersion_coefficients(self):
        """
        Calcula coeficientes de dispersión basados en un modelo gaussiano.

        Returns:
            float: Coeficientes sigma_y y sigma_z.
        """
        stability_classes = {
            "A": (0.22, 0.20),
            "B": (0.16, 0.12),
            "C": (0.11, 0.08),
            "D": (0.08, 0.06),
            "E": (0.06, 0.03),
            "F": (0.04, 0.016),
        }
        
        return stability_classes.get(self.stability_class.upper(), (0.08, 0.06))

    def _calculate_emission_rate(self, vehicle_speed):
        """
        Calcula la tasa de emisión en función de la velocidad del vehículo.

        Args:
            vehicle_speed (float): Velocidad del vehículo en m/s.

        Returns:
            float: Tasa de emisión calculada.
        """
        return self.emission_factor * vehicle_speed

    def _update_contamination(self):
        """
        Actualiza los niveles de contaminación en la cuadrícula paso a paso.
        
        Este método calcula la dispersión usando un modelo gaussiano simplificado.
        """
        sigma_y, sigma_z = self._calculate_dispersion_coefficients()
        
        vehicles = traci.vehicle.getIDList()
        
        for vehicle_id in vehicles:
            x, y = traci.vehicle.getPosition(vehicle_id)
            speed = traci.vehicle.getSpeed(vehicle_id)

            emission_rate = self._calculate_emission_rate(speed)
            
            # Convertir posición a índices en la cuadrícula
            grid_x = int((x - self.network_bounds[0]) / self.grid_resolution)
            grid_y = int((y - self.network_bounds[1]) / self.grid_resolution)

            # Actualizar contaminación en el punto correspondiente
            if 0 <= grid_x < self.grid.shape[0] and 0 <= grid_y < self.grid.shape[1]:
                dispersion_factor = np.exp(-self.deposition_rate * speed)
                self.grid[grid_x][grid_y] += emission_rate * dispersion_factor

    def _render_contamination(self):
        """
        Renderiza visualmente los niveles de contaminación en SUMO usando polígonos.
        
        Utiliza un esquema de colores basado en HSV para representar diferentes niveles.
        """
        traci.polygon.removeAll()  # Eliminar polígonos existentes
        
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                contamination_level = self.grid[i][j]
                
                if contamination_level > 0:
                    # Convertir el nivel de contaminación a color (HSV -> RGB)
                    hue = max(0, min(1 - contamination_level / np.max(self.grid), 1))
                    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

                    # Crear un polígono para representar este nivel
                    xmin = self.network_bounds[0] + i * self.grid_resolution
                    ymin = self.network_bounds[1] + j * self.grid_resolution
                    xmax = xmin + self.grid_resolution
                    ymax = ymin + self.grid_resolution
                    
                    polygon_id = f"cell_{i}_{j}"
                    color = (int(r * 255), int(g * 255), int(b * 255), 128)  # RGBA
                    
                    traci.polygon.add(
                        polygon_id,
                        [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)],
                        color=color,
                        layer=1
                    )

    def step(self):
        """
        Realiza un paso en la simulación:
          - Actualiza los niveles de contaminación.
          - Renderiza los resultados visualmente en SUMO.
          - Avanza un paso en TraCI.
        """
        self._update_contamination()
        self._render_contamination()
