"""
Módulo CS_optimized - Simulación de Dispersión de Contaminantes Optimizada

Este módulo implementa una simulación de dispersión de contaminantes utilizando un modelo gaussiano,
con optimizaciones mediante código C para mejorar el rendimiento.
"""

import colorsys
import math
import numpy as np
import traci
import sys
import os
import time
from typing import Dict, Tuple, List, Any, Optional

# Asegúrate de que el directorio actual es el de 'modules'
module_path = os.path.join(os.path.dirname(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)

# Cargar el módulo optimizado en C 
try:
    # Intenta cargar el nuevo módulo optimizado
    import cs_module
    use_cs_module = True
    print("Usando módulo C optimizado (cs_module) para cálculos de contaminación")
except ImportError:
    try:
        # Si falla, utiliza el módulo original
        import spam
        use_cs_module = False
        print("Usando módulo C original (spam) para cálculos de contaminación")
    except ImportError:
        print("¡ADVERTENCIA! No se pudo cargar ningún módulo C. El rendimiento será muy lento.")
        use_cs_module = False


class CS:
    """
    Clase para la simulación de dispersión de contaminantes.
    Utiliza un módulo C optimizado para los cálculos intensivos.
    
    Atributos:
        config (Dict): Diccionario con la configuración de la simulación
        pollution_grid (np.ndarray): Matriz NumPy que almacena la contaminación
        x_min, y_min, x_max, y_max: Límites del área de simulación
        wind_speed (float): Velocidad del viento en m/s
        wind_direction (float): Dirección del viento en radianes
        stability_class (str): Clase de estabilidad atmosférica (A-F)
        emission_factor (float): Factor de emisión de los vehículos
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el simulador de contaminación.
        
        Args:
            config: Diccionario con la configuración de la simulación
        """
        # Almacenar la configuración
        self.config = config
        
        # Inicializar cuadrícula de contaminación como matriz de ceros
        self.pollution_grid = np.zeros((config['grid_resolution'], config['grid_resolution']))
        
        # Obtener límites del área de la red SUMO
        self.net_bounds = traci.simulation.getNetBoundary()
        self.x_min, self.y_min = self.net_bounds[0]
        self.x_max, self.y_max = self.net_bounds[1]

        # Parámetros meteorológicos y ambientales
        self.wind_speed = config['wind_speed']
        self.wind_direction = math.radians(config['wind_direction'])
        self.stability_class = config['stability_class']
        self.emission_factor = config['emission_factor']
        
        # Registro de inicio
        print(f"Inicializado simulador de contaminación con resolución {config['grid_resolution']}x{config['grid_resolution']}")
        print(f"Área: ({self.x_min}, {self.y_min}) - ({self.x_max}, {self.y_max})")
        print(f"Viento: {self.wind_speed} m/s, dirección {config['wind_direction']}°, estabilidad {self.stability_class}")

    def calculate_dispersion_coefficients(self, distance: float) -> Tuple[float, float]:
        """
        Calcula los coeficientes de dispersión según la distancia y la clase de estabilidad.
        
        Args:
            distance: Distancia al punto de emisión en metros
            
        Returns:
            Tuple con sigma_y y sigma_z (dispersión horizontal y vertical)
        """
        # Coeficientes según la clase de estabilidad
        stability_params = {
            'A': (0.22, 0.20),  # Muy inestable
            'B': (0.16, 0.12),  # Moderadamente inestable
            'C': (0.11, 0.08),  # Ligeramente inestable
            'D': (0.08, 0.06),  # Neutra
            'E': (0.06, 0.03),  # Ligeramente estable
            'F': (0.04, 0.016)  # Moderadamente estable
        }
        
        # Obtener los parámetros para la clase de estabilidad configurada
        a, b = stability_params.get(self.stability_class, (0.10, 0.05))
        
        # Calcular los coeficientes de dispersión
        sigma_y = a * distance * (1 + 0.0001 * distance) ** (-0.5)
        sigma_z = b * distance * (1 + 0.0001 * distance) ** (-0.5)
        
        return sigma_y, sigma_z

    def calculate_plume_rise(self, vehicle_speed: float) -> float:
        """
        Calcula la elevación de la pluma de contaminación.
        
        Args:
            vehicle_speed: Velocidad del vehículo en m/s
            
        Returns:
            Altura de la pluma en metros
        """
        # La altura aumenta con la velocidad pero tiene un mínimo de 2m
        return max(2, 0.5 + 0.15 * vehicle_speed)

    def calculate_emission_rate(self, vehicle_speed: float) -> float:
        """
        Calcula la tasa de emisión basada en la velocidad del vehículo.
        
        Args:
            vehicle_speed: Velocidad del vehículo en m/s
            
        Returns:
            Tasa de emisión
        """
        # Emisión base
        base_emission = 0.1
        
        # Factor que aumenta la emisión con la velocidad (para velocidades > 20 m/s)
        speed_factor = (1 + 0.05 * (vehicle_speed - 20)) if vehicle_speed > 20 else 1
        
        # Aplicar el factor de emisión global
        return base_emission * speed_factor * self.emission_factor

    def update(self):
        """
        Actualiza la cuadrícula de contaminación considerando todos los vehículos.
        Utiliza el módulo C optimizado para los cálculos intensivos.
        """
        # Obtener lista de vehículos activos en la simulación
        vehicles = traci.vehicle.getIDList()
        
        # Verificar si hay vehículos para procesar
        if not vehicles:
            # Si no hay vehículos, solo aplicar decaimiento
            self.pollution_grid *= 0.99
            return
            
        # Intentar usar la versión optimizada para múltiples vehículos
        if use_cs_module and hasattr(cs_module, 'update_pollution_multiple'):
            # Preparar datos de vehículos como lista de tuplas (x, y, velocidad)
            vehicle_data = []
            for vehicle in vehicles:
                x, y = traci.vehicle.getPosition(vehicle)
                vehicle_speed = traci.vehicle.getSpeed(vehicle)
                vehicle_data.append((x, y, vehicle_speed))
            
            try:
                # Una única llamada a C para procesar todos los vehículos
                # Nota: Asegurarse de que el número y orden de argumentos coincida con la función C
                cs_module.update_pollution_multiple(
                    self.pollution_grid,
                    vehicle_data,
                    self.wind_speed,
                    self.wind_direction,
                    self.emission_factor,
                    self.stability_class,
                    self.x_min, self.x_max, self.y_min, self.y_max,
                    self.config['grid_resolution']
                )
                return
            except Exception as e:
                print(f"Error al ejecutar update_pollution_multiple: {e}")
                print("Fallback a la implementación original...")
        
        # Método alternativo: procesar cada vehículo individualmente
        
        # Decaimiento de la contaminación global (factor 0.99)
        self.pollution_grid *= 0.99
        
        # Procesar cada vehículo individualmente
        for vehicle in vehicles:
            # Obtener posición y velocidad del vehículo
            x, y = traci.vehicle.getPosition(vehicle)
            vehicle_speed = traci.vehicle.getSpeed(vehicle)
            
            # Calcular parámetros específicos para este vehículo
            emission_rate = self.calculate_emission_rate(vehicle_speed)
            plume_height = self.calculate_plume_rise(vehicle_speed)

            # Cálculo de índices para la ventana de cálculo (optimización)
            # Solo calculamos contaminación en una ventana de 200x200m alrededor del vehículo
            i_min = max(0, int((y - self.y_min - 100) / (self.y_max - self.y_min) * self.config['grid_resolution']))
            i_max = min(self.config['grid_resolution'],
                        int((y - self.y_min + 100) / (self.y_max - self.y_min) * self.config['grid_resolution']))
            j_min = max(0, int((x - self.x_min - 100) / (self.x_max - self.x_min) * self.config['grid_resolution']))
            j_max = min(self.config['grid_resolution'],
                        int((x - self.x_min + 100) / (self.x_max - self.x_min) * self.config['grid_resolution']))

            try:
                # Intentar usar el módulo C optimizado para un solo vehículo
                if use_cs_module:
                    cs_module.update_pollution(
                        self.pollution_grid,
                        i_min, i_max, j_min, j_max,
                        x, y,
                        emission_rate,
                        plume_height,
                        self.wind_speed,
                        self.wind_direction,
                        self.x_min, self.x_max, self.y_min, self.y_max,
                        self.config['grid_resolution']
                    )
                # Si no está disponible cs_module, intentar usar spam
                elif 'spam' in sys.modules:
                    spam.update_pollution(
                        self.pollution_grid,
                        i_min, i_max, j_min, j_max,
                        x, y,
                        emission_rate,
                        plume_height,
                        self.wind_speed,
                        self.wind_direction,
                        self.x_min, self.x_max, self.y_min, self.y_max,
                        self.config['grid_resolution']
                    )
                # Si no hay módulos C disponibles, usar implementación Python pura
                else:
                    self._update_pollution_py(i_min, i_max, j_min, j_max, x, y, emission_rate, plume_height)
            except Exception as e:
                print(f"Error al actualizar contaminación para vehículo {vehicle}: {e}")
                # Usar implementación Python pura como respaldo
                self._update_pollution_py(i_min, i_max, j_min, j_max, x, y, emission_rate, plume_height)

    def _update_pollution_py(self, i_min: int, i_max: int, j_min: int, j_max: int, 
                           x: float, y: float, emission_rate: float, plume_height: float):
        """
        Implementación en Python puro del cálculo de contaminación (respaldo).
        Este método se usa si los módulos C no están disponibles o fallan.
        
        Args:
            i_min, i_max, j_min, j_max: Límites de la ventana de cálculo
            x, y: Posición del vehículo emisor
            emission_rate: Tasa de emisión
            plume_height: Altura de la pluma
        """
        # Calcular tamaño de celda
        cell_width = (self.x_max - self.x_min) / self.config['grid_resolution']
        cell_height = (self.y_max - self.y_min) / self.config['grid_resolution']
        two_pi = 2.0 * math.pi
        
        # Para cada celda en la ventana de cálculo
        for i in range(i_min, i_max):
            for j in range(j_min, j_max):
                # Calcular coordenadas del centro de la celda
                receptor_x = self.x_min + (j + 0.5) * cell_width
                receptor_y = self.y_min + (i + 0.5) * cell_height
                
                # Calcular distancia al vehículo
                dx = receptor_x - x
                dy = receptor_y - y
                distance_squared = dx * dx + dy * dy
                
                # Omitir cálculos para puntos muy cercanos (< 1m)
                if distance_squared < 1.0:
                    continue
                
                distance = math.sqrt(distance_squared)
                
                # Omitir cálculos para puntos muy lejanos (> 300m)
                if distance > 300.0:
                    continue
                
                # Calcular ángulo entre dirección del viento y dirección al receptor
                wind_dir_to_rec = math.atan2(dy, dx)
                angle_diff = abs(wind_dir_to_rec - self.wind_direction)
                if angle_diff > math.pi:
                    angle_diff = two_pi - angle_diff
                
                # Calcular coeficientes de dispersión
                sigma_y, sigma_z = self.calculate_dispersion_coefficients(distance)
                
                # Calcular componentes de la ecuación gaussiana
                lateral_dispersion = math.exp(-0.5 * (angle_diff / sigma_y) ** 2)
                vertical_dispersion = math.exp(-0.5 * (plume_height / sigma_z) ** 2) * 2.0
                
                # Calcular concentración usando modelo gaussiano
                concentration = (emission_rate / (two_pi * self.wind_speed * sigma_y * sigma_z)) * \
                                lateral_dispersion * vertical_dispersion
                
                # Añadir contribución a la celda
                self.pollution_grid[i, j] += concentration

    def visualize(self):
        """
        Visualiza la contaminación en la simulación SUMO.
        Crea polígonos coloreados que representan la concentración de contaminantes.
        """
        # Obtener el valor máximo de contaminación para normalizar colores
        max_pollution = np.max(self.pollution_grid)
        if max_pollution == 0:
            return  # No hay contaminación para visualizar

        # Calcular tamaño de celda
        cell_width = (self.x_max - self.x_min) / self.config['grid_resolution']
        cell_height = (self.y_max - self.y_min) / self.config['grid_resolution']

        # Visualizar con celdas más grandes (agrupando de 2x2) para mejor rendimiento
        for i in range(0, self.config['grid_resolution'], 2):
            for j in range(0, self.config['grid_resolution'], 2):
                # Calcular promedio de contaminación en el bloque 2x2
                i_end = min(i + 2, self.config['grid_resolution'])
                j_end = min(j + 2, self.config['grid_resolution'])
                pollution = np.mean(self.pollution_grid[i:i_end, j:j_end])
                
                # Solo visualizar celdas con contaminación
                if pollution > 0:
                    # Calcular posición del polígono
                    x = self.x_min + j * cell_width
                    y = self.y_min + i * cell_height
                    
                    # Determinar color basado en el nivel de contaminación
                    # Usar escala de colores HSV (azul a rojo)
                    hue = (1 - pollution / max_pollution) * 0.4
                    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                    
                    # Crear color RGBA con transparencia basada en nivel de contaminación
                    color = (
                        int(r * 255),  # Rojo
                        int(g * 255),  # Verde
                        int(b * 255),  # Azul
                        int(255 * min(1, pollution / max_pollution * 5))  # Alfa (transparencia)
                    )

                    # Crear polígono en SUMO
                    polygon_id = f"pollution_{i}_{j}"
                    shape = [
                        (x, y),  # Esquina inferior izquierda
                        (x + cell_width * 2, y),  # Esquina inferior derecha
                        (x + cell_width * 2, y + cell_height * 2),  # Esquina superior derecha
                        (x, y + cell_height * 2)  # Esquina superior izquierda
                    ]
                    # Añadir polígono a la visualización de SUMO
                    traci.polygon.add(polygon_id, shape, color, True, "pollution_layer")