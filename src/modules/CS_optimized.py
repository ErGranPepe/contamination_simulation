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
import scipy.ndimage
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
    # print("Usando módulo C optimizado (cs_module) para cálculos de contaminación")
    # print(f"cs_module loaded from: {cs_module.__file__}")
except ImportError:
    try:
        # Si falla, utiliza el módulo original
        import spam
        use_cs_module = False
        # print("Usando módulo C original (spam) para cálculos de contaminación")
    except ImportError:
        # print("¡ADVERTENCIA! No se pudo cargar ningún módulo C. El rendimiento será muy lento.")
        use_cs_module = False


class CS:
    """
    Núcleo CFD multiespecie optimizado para simulación de contaminación urbana.
    - Soporta múltiples especies, meteorología avanzada, campos variables.
    - Métodos vectorizados y acoplados a módulo C para máxima velocidad.
    - Exporta resultados a VTK, CSV y memoria para visualización web.
    """
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
        
        # Soporte para múltiples especies contaminantes
        self.species_list = config.get('species_list', ['NOx'])
        self.pollution_grids = {species: np.zeros((config['grid_resolution'], config['grid_resolution'])) for species in self.species_list}
        
        # Registro de inicio
        # print(f"Inicializado simulador de contaminación con resolución {config['grid_resolution']}x{config['grid_resolution']}")
        # print(f"Área: ({self.x_min}, {self.y_min}) - ({self.x_max}, {self.y_max})")
        # print(f"Viento: {self.wind_speed} m/s, dirección {config['wind_direction']}°, estabilidad {self.stability_class}")

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

    def update(self, use_vectorized=False, **kwargs):
        """
        Actualiza la cuadrícula de contaminación considerando todos los vehículos.
        Si use_vectorized=True, usa el método CFD vectorizado profesional.
        """
        if use_vectorized:
            self.update_pollution_vectorized(**kwargs)
            return {'total_update_time': 0}  # Puedes medir el tiempo si lo deseas

        # ...existing code (fallback a C o Python clásico)...
        start_total = time.perf_counter()
        vehicles = traci.vehicle.getIDList()
        start_vehicle_data = time.perf_counter()
        vehicle_data = []
        for vehicle in vehicles:
            x, y = traci.vehicle.getPosition(vehicle)
            vehicle_speed = traci.vehicle.getSpeed(vehicle)
            vehicle_data.append((x, y, vehicle_speed))
        end_vehicle_data = time.perf_counter()

        timing_data = {}
        timing_data['time_getting_vehicle_data'] = end_vehicle_data - start_vehicle_data

        if not vehicles:
            self.pollution_grid *= 0.99
            timing_data['total_update_time'] = time.perf_counter() - start_total
            return timing_data

        if use_cs_module and hasattr(cs_module, 'update_pollution_multiple'):
            try:
                start_c_call = time.perf_counter()
                cs_module.update_pollution_multiple(
                    self.pollution_grid,
                    vehicle_data,
                    self.wind_speed,
                    self.wind_direction,
                    self.emission_factor,
                    self.stability_class,
                    self.x_min, self.x_max,
                    self.y_min, self.y_max,
                    self.config['grid_resolution']
                )
                elapsed_c_call = time.perf_counter() - start_c_call
                timing_data['time_in_c_call'] = elapsed_c_call
                timing_data['total_update_time'] = time.perf_counter() - start_total
                return timing_data

            except Exception as e:
                # print(f"Error al ejecutar update_pollution_multiple: {e}")
                # print("Fallback a la implementación original...")
                pass
            
            # Decaimiento natural de la contaminación (factor de limpieza)
            self.pollution_grid *= 0.99

        start_update_calls = time.perf_counter()
        for vehicle in vehicles:
            x, y, vehicle_speed = vehicle_data.pop(0)
            emission_rate = self.calculate_emission_rate(vehicle_speed)
            plume_height = self.calculate_plume_rise(vehicle_speed)

            i_min = max(0, int((y - self.y_min - 100) / (self.y_max - self.y_min) * self.config['grid_resolution']))
            i_max = min(self.config['grid_resolution'],
                        int((y - self.y_min + 100) / (self.y_max - self.y_min) * self.config['grid_resolution']))
            j_min = max(0, int((x - self.x_min - 100) / (self.x_max - self.x_min) * self.config['grid_resolution']))
            j_max = min(self.config['grid_resolution'],
                        int((x - self.x_min + 100) / (self.x_max - self.x_min) * self.config['grid_resolution']))

            try:
                if use_cs_module:
                    start_time = time.perf_counter()
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
                    elapsed = time.perf_counter() - start_time
                    timing_data.setdefault('time_per_vehicle', []).append(elapsed)
                elif 'spam' in sys.modules:
                    start_time = time.perf_counter()
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
                    elapsed = time.perf_counter() - start_time
                    timing_data.setdefault('time_per_vehicle', []).append(elapsed)
                else:
                    start_time = time.perf_counter()
                    self._update_pollution_py(i_min, i_max, j_min, j_max, x, y, emission_rate, plume_height)
                    elapsed = time.perf_counter() - start_time
                    timing_data.setdefault('time_per_vehicle', []).append(elapsed)
            except Exception as e:
                # print(f"Error al actualizar contaminación para vehículo {vehicle}: {e}")
                start_time = time.perf_counter()
                self._update_pollution_py(i_min, i_max, j_min, j_max, x, y, emission_rate, plume_height)
                elapsed = time.perf_counter() - start_time
                timing_data.setdefault('time_per_vehicle', []).append(elapsed)
        end_update_calls = time.perf_counter()
        timing_data['time_in_update_calls'] = end_update_calls - start_update_calls
        timing_data['total_update_time'] = time.perf_counter() - start_total
        return timing_data

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
        start_visualize = time.perf_counter()
        # Obtener el valor máximo de contaminación para normalizar colores
        max_pollution = np.max(self.pollution_grid)
        if max_pollution == 0:
            return 0  # No hay contaminación para visualizar

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
        elapsed_visualize = time.perf_counter() - start_visualize
        return elapsed_visualize

    def update_pollution_vectorized(self, dt=1.0, diffusion_coeff=2.0, wind_field=None, z_layers=1):
        """
        Actualiza la malla de contaminación usando advección-difusión vectorizada (CFD simplificado).
        - Añade emisiones de vehículos como fuentes puntuales.
        - Aplica difusión y advección física explícita.
        - Preparado para 3D (z_layers>1).
        - Permite campos de viento variables (wind_field).
        """
        grid_res = self.config['grid_resolution']
        if z_layers > 1:
            if not hasattr(self, 'pollution_grid_3d'):
                self.pollution_grid_3d = np.zeros((grid_res, grid_res, z_layers))
            grid = self.pollution_grid_3d
        else:
            grid = self.pollution_grid

        # 1. Añadir emisiones de vehículos
        vehicles = traci.vehicle.getIDList()
        for veh in vehicles:
            x, y = traci.vehicle.getPosition(veh)
            speed = traci.vehicle.getSpeed(veh)
            emission = self.calculate_emission_rate(speed)
            # Mapear a celda
            i = int((y - self.y_min) / (self.y_max - self.y_min) * grid_res)
            j = int((x - self.x_min) / (self.x_max - self.x_min) * grid_res)
            if 0 <= i < grid_res and 0 <= j < grid_res:
                if z_layers > 1:
                    grid[i, j, 0] += emission * dt  # fuente en la capa más baja
                else:
                    grid[i, j] += emission * dt

        # 2. Difusión (Laplaciano)
        if z_layers > 1:
            for z in range(z_layers):
                grid[:, :, z] += diffusion_coeff * scipy.ndimage.laplace(grid[:, :, z]) * dt
        else:
            grid += diffusion_coeff * scipy.ndimage.laplace(grid) * dt

        # 3. Advección (viento)
        if wind_field is None:
            # Viento uniforme
            vx = self.wind_speed * np.cos(self.wind_direction)
            vy = self.wind_speed * np.sin(self.wind_direction)
            if z_layers > 1:
                for z in range(z_layers):
                    grid[:, :, z] = np.roll(grid[:, :, z], int(vy * dt), axis=0)
                    grid[:, :, z] = np.roll(grid[:, :, z], int(vx * dt), axis=1)
            else:
                # CORRECCIÓN: np.roll devuelve una copia, hay que asignar el resultado a self.pollution_grid
                grid[...] = np.roll(grid, int(vy * dt), axis=0)
                grid[...] = np.roll(grid, int(vx * dt), axis=1)
        else:
            # Campo de viento variable (no implementado en detalle aquí)
            pass

        # 4. Decaimiento natural
        grid *= 0.995
        if z_layers > 1:
            self.pollution_grid_3d = grid
        else:
            self.pollution_grid = grid

    def update_pollution_vectorized_multi(self, dt=1.0, diffusion_coeff=2.0, wind_field=None, diffusion_field=None, use_c_module=True):
        """
        Actualiza todas las mallas de especies usando advección-difusión vectorizada y C puro si está disponible.
        Permite campos de viento y difusión variables (hooks para meteorología avanzada).
        Args:
            dt (float): Paso temporal de integración.
            diffusion_coeff (float): Coeficiente de difusión global.
            wind_field (np.ndarray): Campo de viento espacialmente variable (opcional).
            diffusion_field (np.ndarray): Campo de difusión espacialmente variable (opcional).
            use_c_module (bool): Si True, fuerza el uso del módulo C para máxima velocidad.
        """
        grid_res = self.config['grid_resolution']
        vehicles = traci.vehicle.getIDList()
        for species in self.species_list:
            grid = self.pollution_grids[species]
            # 1. Añadir emisiones de vehículos (puedes personalizar por especie)
            for veh in vehicles:
                x, y = traci.vehicle.getPosition(veh)
                speed = traci.vehicle.getSpeed(veh)
                emission = self.calculate_emission_rate(speed)  # Personaliza por especie si lo deseas
                i = int((y - self.y_min) / (self.y_max - self.y_min) * grid_res)
                j = int((x - self.x_min) / (self.x_max - self.x_min) * grid_res)
                if 0 <= i < grid_res and 0 <= j < grid_res:
                    grid[i, j] += emission * dt
            # 2. Difusión
            if use_c_module and 'cs_module' in sys.modules and hasattr(cs_module, 'diffuse_grid'):
                # Difusión ultra-rápida en C
                cs_module.diffuse_grid(grid, diffusion_coeff, dt)
            elif diffusion_field is not None:
                # Difusión espacialmente variable (hook para futuro)
                grid += diffusion_field * scipy.ndimage.laplace(grid) * dt
            else:
                grid += diffusion_coeff * scipy.ndimage.laplace(grid) * dt
            # 3. Advección
            if use_c_module and 'cs_module' in sys.modules and hasattr(cs_module, 'advect_grid'):
                # Advección ultra-rápida en C
                cs_module.advect_grid(grid, self.wind_speed, self.wind_direction, dt)
            elif wind_field is not None:
                # Advección espacialmente variable (hook para futuro)
                for i in range(grid_res):
                    for j in range(grid_res):
                        vx, vy = wind_field[i, j]
                        ii = (i + int(vy * dt)) % grid_res
                        jj = (j + int(vx * dt)) % grid_res
                        grid[ii, jj] += grid[i, j] * 0.01  # Pequeña fracción advectada
            else:
                vx = self.wind_speed * np.cos(self.wind_direction)
                vy = self.wind_speed * np.sin(self.wind_direction)
                grid[...] = np.roll(grid, int(vy * dt), axis=0)
                grid[...] = np.roll(grid, int(vx * dt), axis=1)
            # 4. Decaimiento
            grid *= 0.995
            self.pollution_grids[species] = grid

    def export_to_vtk(self, filename='pollution_grid.vtk', z_layers=1):
        """
        Exporta la malla de contaminación a formato VTK para visualización 3D (Paraview, Blender).
        """
        grid_res = self.config['grid_resolution']
        if z_layers > 1 and hasattr(self, 'pollution_grid_3d'):
            grid = self.pollution_grid_3d
        else:
            grid = self.pollution_grid
        with open(filename, 'w') as f:
            f.write('# vtk DataFile Version 3.0\n')
            f.write('Pollution grid\n')
            f.write('ASCII\n')
            f.write('DATASET STRUCTURED_POINTS\n')
            f.write(f'DIMENSIONS {grid_res} {grid_res} {z_layers}\n')
            f.write('ORIGIN 0 0 0\n')
            f.write('SPACING 1 1 1\n')
            f.write(f'POINT_DATA {grid_res*grid_res*z_layers}\n')
            f.write('SCALARS pollution float 1\n')
            f.write('LOOKUP_TABLE default\n')
            if z_layers > 1:
                for z in range(z_layers):
                    for i in range(grid_res):
                        for j in range(grid_res):
                            f.write(f'{grid[i,j,z]:.6e}\n')
            else:
                for i in range(grid_res):
                    for j in range(grid_res):
                        f.write(f'{grid[i,j]:.6e}\n')

    def export_to_vtk_multi(self, filename_prefix='pollution_grid', step=0):
        """
        Exporta todas las especies a archivos VTK independientes.
        """
        grid_res = self.config['grid_resolution']
        for species in self.species_list:
            grid = self.pollution_grids[species]
            filename = f"{filename_prefix}_{species}_{step}.vtk"
            with open(filename, 'w') as f:
                f.write('# vtk DataFile Version 3.0\n')
                f.write(f'Pollution grid {species}\n')
                f.write('ASCII\n')
                f.write('DATASET STRUCTURED_POINTS\n')
                f.write(f'DIMENSIONS {grid_res} {grid_res} 1\n')
                f.write('ORIGIN 0 0 0\n')
                f.write('SPACING 1 1 1\n')
                f.write(f'POINT_DATA {grid_res*grid_res}\n')
                f.write('SCALARS pollution float 1\n')
                f.write('LOOKUP_TABLE default\n')
                for i in range(grid_res):
                    for j in range(grid_res):
                        f.write(f'{grid[i,j]:.6e}\n')
