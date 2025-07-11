# Guía de Usuario Completa - Simulador CFD Avanzado

## 📋 **TABLA DE CONTENIDOS**

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Configuración Inicial](#configuración-inicial)
4. [Uso Básico](#uso-básico)
5. [Uso Avanzado](#uso-avanzado)
6. [Análisis de Resultados](#análisis-de-resultados)
7. [Resolución de Problemas](#resolución-de-problemas)
8. [Casos de Ejemplo](#casos-de-ejemplo)
9. [Referencia de APIs](#referencia-de-apis)
10. [Mejores Prácticas](#mejores-prácticas)

---

## 🚀 **INTRODUCCIÓN**

### **¿Qué es el Simulador CFD Avanzado?**

El Simulador CFD Avanzado es una herramienta científica de vanguardia para la simulación y análisis de la dispersión de contaminantes atmosféricos en entornos urbanos. Desarrollado específicamente para cumplir con los estándares europeos más exigentes, combina precisión científica con facilidad de uso.

### **Características Principales**

✅ **CFD Completo**: Resolución de ecuaciones de Navier-Stokes 3D  
✅ **Turbulencia Avanzada**: Modelo k-epsilon calibrado  
✅ **Validación Rigurosa**: Comparación con datos experimentales  
✅ **Análisis de Incertidumbre**: Cuantificación estadística completa  
✅ **Múltiples Interfaces**: Web, desktop y línea de comandos  
✅ **Código Abierto**: Licencia MIT, modificable y extensible  

### **Aplicaciones Típicas**

- **Planificación Urbana**: Evaluación de impacto ambiental
- **Salud Pública**: Análisis de exposición a contaminantes
- **Investigación**: Estudios de dispersión atmosférica
- **Consultoría**: Evaluación de proyectos de infraestructura
- **Educación**: Enseñanza de CFD y calidad del aire

---

## ⚙️ **INSTALACIÓN**

### **Requisitos del Sistema**

#### **Requisitos Mínimos**
- **Sistema Operativo**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **Procesador**: Intel Core i5 / AMD Ryzen 5 (4 núcleos)
- **Memoria RAM**: 8 GB
- **Espacio en disco**: 5 GB libre
- **Python**: 3.8 o superior

#### **Requisitos Recomendados**
- **Sistema Operativo**: Windows 11, macOS 12+, Linux Ubuntu 20.04+
- **Procesador**: Intel Core i7 / AMD Ryzen 7 (8+ núcleos)
- **Memoria RAM**: 16 GB o más
- **Espacio en disco**: 20 GB libre (SSD recomendado)
- **GPU**: NVIDIA RTX series (opcional, para aceleración)
- **Python**: 3.11 (más reciente)

### **Instalación Paso a Paso**

#### **Opción 1: Instalación Automática (Recomendada)**

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/ErGranPepe/contamination_simulation.git
   cd contamination_simulation
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   
   # En Windows:
   venv\Scripts\activate
   
   # En macOS/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verificar instalación**:
   ```bash
   python -m pytest tests/ -v
   ```

#### **Opción 2: Instalación Manual**

1. **Instalar Python**: Descargar de [python.org](https://python.org)

2. **Instalar dependencias principales**:
   ```bash
   pip install numpy scipy matplotlib pandas numba flask tkinter
   ```

3. **Instalar dependencias científicas**:
   ```bash
   pip install scikit-learn seaborn plotly h5py requests
   ```

4. **Instalar dependencias opcionales**:
   ```bash
   pip install jupyter notebook ipython
   ```

### **Configuración Inicial**

#### **Configurar Variables de Entorno**

Crear archivo `.env` en el directorio raíz:

```bash
# Configuración del simulador
SIMULATION_DATA_DIR=./data
SIMULATION_RESULTS_DIR=./results
SIMULATION_LOG_LEVEL=INFO

# Configuración de APIs (opcional)
OPENAQ_API_KEY=tu_clave_aqui
WEATHER_API_KEY=tu_clave_aqui

# Configuración de rendimiento
OMP_NUM_THREADS=8
NUMBA_THREADING_LAYER=omp
```

#### **Verificar Configuración**

```bash
python src/utils/check_installation.py
```

---

## 🎯 **USO BÁSICO**

### **Primera Simulación**

#### **Paso 1: Lanzar la Interfaz Web**

```bash
cd contamination_simulation
python src/webapp.py
```

Abrir navegador en: `http://localhost:5000`

#### **Paso 2: Configurar Simulación Básica**

1. **Parámetros Meteorológicos**:
   - Velocidad del viento: 5.0 m/s
   - Dirección del viento: 270° (oeste)
   - Estabilidad atmosférica: D (neutral)

2. **Parámetros de Dominio**:
   - Área: 1000m × 1000m
   - Altura: 200m
   - Resolución: 50 × 50 × 20 celdas

3. **Fuentes de Emisión**:
   - Tipo: Línea (calle)
   - Contaminante: NOx
   - Tasa de emisión: 0.01 kg/s

#### **Paso 3: Ejecutar Simulación**

1. Clic en "Configurar Simulación"
2. Revisar parámetros
3. Clic en "Iniciar Simulación"
4. Esperar 2-5 minutos (dependiendo del hardware)

#### **Paso 4: Visualizar Resultados**

1. **Mapa de Concentraciones**: Visualización 2D en tiempo real
2. **Gráficos Temporales**: Evolución de concentraciones
3. **Estadísticas**: Valores máximos, medios, percentiles
4. **Exportaciones**: Descargar datos en CSV/VTK

### **Interpretación de Resultados Básicos**

#### **Mapa de Concentraciones**
- **Colores cálidos (rojo/naranja)**: Concentraciones altas
- **Colores fríos (azul/verde)**: Concentraciones bajas
- **Patrones**: Pluma de dispersión siguiendo el viento

#### **Métricas Clave**
- **Concentración máxima**: Valor pico en el dominio
- **Área de impacto**: Zona con concentraciones > umbral
- **Tiempo de residencia**: Tiempo de permanencia del contaminante

---

## 🔬 **USO AVANZADO**

### **Simulación CFD Completa**

#### **Configuración Avanzada**

```python
# Archivo: config_advanced.json
{
    "simulation": {
        "name": "Urban_Canyon_Detailed",
        "version": "3.0",
        "mode": "advanced_cfd"
    },
    "domain": {
        "size": [2000, 1000, 300],
        "resolution": [100, 50, 30],
        "refinement_zones": [
            {
                "bounds": [[900, 1100], [400, 600], [0, 50]],
                "factor": 2
            }
        ]
    },
    "physics": {
        "turbulence_model": "k_epsilon",
        "thermal_effects": true,
        "buoyancy": true,
        "chemical_reactions": true
    },
    "meteorology": {
        "wind_profile": "logarithmic",
        "wind_speed": 6.0,
        "wind_direction": 225,
        "surface_roughness": 0.5,
        "stability_class": "D",
        "temperature_profile": "linear",
        "temperature_gradient": -0.0065
    },
    "species": [
        {
            "name": "NOx",
            "molecular_weight": 46.01,
            "diffusivity": 1.5e-5,
            "decay_rate": 1e-5,
            "background_concentration": 20.0
        },
        {
            "name": "CO",
            "molecular_weight": 28.01,
            "diffusivity": 1.8e-5,
            "decay_rate": 0.0,
            "background_concentration": 0.5
        }
    ],
    "sources": [
        {
            "type": "line",
            "name": "Main_Street",
            "coordinates": [[100, 500, 2], [1900, 500, 2]],
            "emission_rate": {
                "NOx": 0.015,
                "CO": 0.008
            },
            "temporal_profile": "traffic_pattern",
            "temperature": 350.0
        },
        {
            "type": "point",
            "name": "Industrial_Stack",
            "coordinates": [1500, 200, 50],
            "emission_rate": {
                "NOx": 0.25,
                "CO": 0.12
            },
            "temporal_profile": "constant",
            "temperature": 450.0
        }
    ],
    "numerical": {
        "timestep": 0.1,
        "max_iterations": 10000,
        "convergence_tolerance": 1e-6,
        "cfl_number": 0.8
    }
}
```

#### **Ejecutar Simulación Avanzada**

```bash
python src/main_advanced.py --config config_advanced.json
```

### **Análisis de Sensibilidad**

#### **Configuración del Análisis**

```python
# sensitivity_config.py
sensitivity_config = {
    'parameters': {
        'wind_speed': {
            'range': [2.0, 8.0],
            'distribution': 'lognormal',
            'mean': 5.0,
            'std': 1.0
        },
        'wind_direction': {
            'range': [0, 360],
            'distribution': 'vonmises',
            'mu': 270,
            'kappa': 2.0
        },
        'emission_rate': {
            'range': [0.005, 0.020],
            'distribution': 'gamma',
            'shape': 2.0,
            'scale': 0.0075
        },
        'stability_class': {
            'range': [1, 6],
            'distribution': 'discrete',
            'probabilities': [0.1, 0.2, 0.3, 0.3, 0.08, 0.02]
        }
    },
    'analysis': {
        'method': 'sobol',
        'samples': 5000,
        'bootstrap': 1000,
        'confidence_level': 0.95
    },
    'outputs': {
        'metrics': ['max_concentration', 'mean_concentration', 'impact_area'],
        'export_format': ['json', 'csv', 'hdf5']
    }
}
```

#### **Ejecutar Análisis**

```python
from src.modules.sensitivity_analysis import SensitivityAnalyzer

# Crear analizador
analyzer = SensitivityAnalyzer(simulator_function)
analyzer.configure(sensitivity_config)

# Ejecutar análisis
results = analyzer.run_analysis()

# Generar reportes
analyzer.generate_report('sensitivity_report.pdf')
analyzer.plot_results('sensitivity_plots.png')
```

### **Validación con Datos Reales**

#### **Configuración de Validación**

```python
# validation_config.py
validation_config = {
    'data_sources': [
        {
            'name': 'madrid_network',
            'type': 'openaq',
            'location': [40.4168, -3.7038],
            'radius': 5000,
            'parameters': ['NOx', 'CO', 'PM2.5']
        },
        {
            'name': 'local_sensors',
            'type': 'csv',
            'file_path': 'data/sensor_data.csv',
            'time_column': 'timestamp',
            'location_columns': ['lat', 'lon']
        }
    ],
    'time_period': {
        'start': '2024-01-01',
        'end': '2024-01-31',
        'frequency': 'hourly'
    },
    'validation_metrics': [
        'rmse', 'mae', 'r2', 'fac2', 'mb', 'mg', 'vg', 'fb'
    ],
    'statistical_tests': [
        'ttest', 'kstest', 'levene', 'shapiro'
    ]
}
```

#### **Ejecutar Validación**

```python
from src.modules.validation_module import ValidationModule

# Crear validador
validator = ValidationModule(validation_config)

# Cargar datos observacionales
obs_data = validator.load_observational_data()

# Ejecutar simulaciones para validación
sim_results = validator.run_validation_simulations()

# Calcular métricas
metrics = validator.calculate_metrics(obs_data, sim_results)

# Generar reporte
validator.generate_validation_report('validation_report.pdf')
```

---

## 📊 **ANÁLISIS DE RESULTADOS**

### **Visualización de Resultados**

#### **Mapas de Concentración**

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_concentration_map(concentration_data, domain_info):
    """
    Crear mapa de concentraciones con isolíneas
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Crear malla de coordenadas
    x = np.linspace(0, domain_info['Lx'], domain_info['nx'])
    y = np.linspace(0, domain_info['Ly'], domain_info['ny'])
    X, Y = np.meshgrid(x, y)
    
    # Contornos de concentración
    contours = ax.contourf(X, Y, concentration_data, 
                          levels=20, cmap='YlOrRd', alpha=0.8)
    
    # Isolíneas
    ax.contour(X, Y, concentration_data, 
               levels=[10, 25, 50, 100], colors='black', linewidths=0.5)
    
    # Configuración
    ax.set_xlabel('Distancia X [m]')
    ax.set_ylabel('Distancia Y [m]')
    ax.set_title('Concentración de NOx [μg/m³]')
    
    # Barra de color
    cbar = plt.colorbar(contours, ax=ax)
    cbar.set_label('Concentración [μg/m³]')
    
    plt.tight_layout()
    plt.show()
```

#### **Perfiles Verticales**

```python
def plot_vertical_profiles(data, locations):
    """
    Graficar perfiles verticales en múltiples ubicaciones
    """
    fig, axes = plt.subplots(1, len(locations), figsize=(15, 6))
    
    for i, (name, x, y) in enumerate(locations):
        # Extraer perfil vertical
        profile = data[x, y, :]
        heights = np.linspace(0, domain_info['Lz'], domain_info['nz'])
        
        # Graficar
        axes[i].plot(profile, heights, 'b-', linewidth=2)
        axes[i].set_xlabel('Concentración [μg/m³]')
        axes[i].set_ylabel('Altura [m]')
        axes[i].set_title(f'Perfil en {name}')
        axes[i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
```

### **Análisis Estadístico**

#### **Estadísticas Descriptivas**

```python
def calculate_statistics(concentration_data):
    """
    Calcular estadísticas descriptivas completas
    """
    stats = {
        'mean': np.mean(concentration_data),
        'median': np.median(concentration_data),
        'std': np.std(concentration_data),
        'min': np.min(concentration_data),
        'max': np.max(concentration_data),
        'percentiles': {
            '25th': np.percentile(concentration_data, 25),
            '75th': np.percentile(concentration_data, 75),
            '90th': np.percentile(concentration_data, 90),
            '95th': np.percentile(concentration_data, 95),
            '99th': np.percentile(concentration_data, 99)
        },
        'skewness': scipy.stats.skew(concentration_data.flatten()),
        'kurtosis': scipy.stats.kurtosis(concentration_data.flatten())
    }
    return stats
```

#### **Análisis de Hotspots**

```python
def identify_hotspots(concentration_data, threshold=50):
    """
    Identificar zonas de alta concentración
    """
    hotspots = concentration_data > threshold
    
    # Encontrar componentes conectados
    from scipy.ndimage import label
    labeled_hotspots, num_hotspots = label(hotspots)
    
    # Calcular propiedades de cada hotspot
    hotspot_properties = []
    for i in range(1, num_hotspots + 1):
        mask = labeled_hotspots == i
        area = np.sum(mask) * (domain_info['dx'] * domain_info['dy'])
        max_conc = np.max(concentration_data[mask])
        mean_conc = np.mean(concentration_data[mask])
        
        hotspot_properties.append({
            'id': i,
            'area': area,
            'max_concentration': max_conc,
            'mean_concentration': mean_conc,
            'cells': np.sum(mask)
        })
    
    return hotspot_properties
```

### **Reportes Automatizados**

#### **Generación de Reportes**

```python
def generate_comprehensive_report(results, config, output_path):
    """
    Generar reporte completo en formato PDF
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title = Paragraph("Reporte de Simulación CFD", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Resumen ejecutivo
    summary = f"""
    <b>Configuración:</b><br/>
    • Dominio: {config['domain']['size']} m<br/>
    • Resolución: {config['domain']['resolution']} celdas<br/>
    • Especies: {', '.join([s['name'] for s in config['species']])}<br/>
    • Viento: {config['meteorology']['wind_speed']} m/s, {config['meteorology']['wind_direction']}°<br/>
    <br/>
    <b>Resultados Principales:</b><br/>
    • Concentración máxima: {results['max_concentration']:.2f} μg/m³<br/>
    • Concentración media: {results['mean_concentration']:.2f} μg/m³<br/>
    • Área de impacto: {results['impact_area']:.2f} km²<br/>
    • Tiempo de simulación: {results['simulation_time']:.1f} minutos<br/>
    """
    
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Agregar figuras
    if 'figures' in results:
        for fig_name, fig_path in results['figures'].items():
            story.append(Paragraph(f"<b>{fig_name}</b>", styles['Heading2']))
            story.append(Image(fig_path, width=400, height=300))
            story.append(Spacer(1, 20))
    
    # Construir documento
    doc.build(story)
```

---

## 🔧 **RESOLUCIÓN DE PROBLEMAS**

### **Problemas Comunes**

#### **Error: "No se puede iniciar SUMO"**

**Síntomas**: Error al ejecutar simulaciones que requieren SUMO

**Soluciones**:
1. Verificar instalación de SUMO:
   ```bash
   sumo --version
   ```
2. Configurar PATH de SUMO:
   ```bash
   export SUMO_HOME=/usr/share/sumo
   export PATH=$PATH:$SUMO_HOME/bin
   ```
3. Instalar SUMO:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install sumo sumo-tools sumo-doc
   
   # Windows: Descargar de https://sumo.dlr.de/
   ```

#### **Error: "Memoria insuficiente"**

**Síntomas**: Simulación se detiene por falta de memoria

**Soluciones**:
1. Reducir resolución de malla:
   ```python
   # En lugar de:
   grid_size = (200, 200, 50)
   # Usar:
   grid_size = (100, 100, 25)
   ```
2. Activar modo de memoria eficiente:
   ```python
   config['memory_efficient'] = True
   config['checkpoint_interval'] = 100
   ```

#### **Error: "Simulación no converge"**

**Síntomas**: Residuos no disminuyen, solución oscila

**Soluciones**:
1. Reducir paso temporal:
   ```python
   config['dt'] = 0.05  # En lugar de 0.1
   ```
2. Aumentar relajación:
   ```python
   config['relaxation_factors'] = {
       'velocity': 0.7,
       'pressure': 0.3,
       'turbulence': 0.8
   }
   ```

### **Problemas de Rendimiento**

#### **Simulación muy lenta**

**Diagnóstico**:
```python
# Verificar uso de CPU
import psutil
print(f"CPU usage: {psutil.cpu_percent()}%")
print(f"Memory usage: {psutil.virtual_memory().percent}%")
```

**Optimizaciones**:
1. Habilitar paralelización:
   ```bash
   export OMP_NUM_THREADS=8
   ```
2. Usar compilación JIT:
   ```python
   config['use_numba'] = True
   ```
3. Optimizar malla:
   ```python
   # Usar refinamiento adaptativo
   config['adaptive_refinement'] = True
   ```

### **Problemas de Validación**

#### **Métricas de validación pobres**

**Diagnóstico**:
```python
# Verificar datos de entrada
print(f"Observed data range: {obs_data.min()} - {obs_data.max()}")
print(f"Simulated data range: {sim_data.min()} - {sim_data.max()}")
```

**Mejoras**:
1. Calibrar parámetros:
   ```python
   config['calibration'] = {
       'wind_speed_factor': 1.1,
       'emission_factor': 0.9,
       'mixing_height': 500
   }
   ```
2. Mejorar condiciones de contorno:
   ```python
   config['boundary_conditions'] = {
       'wind_profile': 'logarithmic',
       'turbulence_intensity': 0.1
   }
   ```

---

## 📚 **CASOS DE EJEMPLO**

### **Caso 1: Intersección Urbana Básica**

```python
# ejemplo_interseccion.py
import numpy as np
from src.main_advanced import AdvancedSimulationManager

# Configuración básica
config = {
    'domain': {
        'size': [500, 500, 100],
        'resolution': [50, 50, 20]
    },
    'meteorology': {
        'wind_speed': 4.0,
        'wind_direction': 270,
        'stability_class': 'D'
    },
    'sources': [
        {
            'type': 'point',
            'coordinates': [250, 250, 2],
            'emission_rate': {'NOx': 0.01},
            'name': 'intersection'
        }
    ],
    'species': [
        {'name': 'NOx', 'diffusivity': 1.5e-5}
    ]
}

# Ejecutar simulación
sim = AdvancedSimulationManager(config)
results = sim.run_complete_analysis()

# Mostrar resultados
print(f"Concentración máxima: {results['max_concentration']:.2f} μg/m³")
print(f"Área de impacto: {results['impact_area']:.2f} m²")
```

### **Caso 2: Cañón Urbano Complejo**

```python
# ejemplo_canon_urbano.py
config = {
    'domain': {
        'size': [1000, 200, 80],
        'resolution': [100, 20, 16]
    },
    'meteorology': {
        'wind_speed': 6.0,
        'wind_direction': 270,  # Perpendicular al cañón
        'stability_class': 'D',
        'surface_roughness': 0.5
    },
    'geometry': {
        'buildings': [
            {
                'bounds': [[0, 200], [0, 20], [0, 60]],
                'type': 'solid'
            },
            {
                'bounds': [[0, 200], [180, 200], [0, 60]],
                'type': 'solid'
            }
        ]
    },
    'sources': [
        {
            'type': 'line',
            'coordinates': [[50, 100, 2], [950, 100, 2]],
            'emission_rate': {'NOx': 0.02, 'CO': 0.01},
            'name': 'street_traffic'
        }
    ],
    'analysis': {
        'enable_recirculation_analysis': True,
        'calculate_residence_time': True
    }
}

# Ejecutar simulación con análisis avanzado
sim = AdvancedSimulationManager(config)
results = sim.run_complete_analysis()

# Análisis específico de cañón urbano
recirculation_zones = sim.identify_recirculation_zones()
residence_time = sim.calculate_residence_time()

print(f"Zonas de recirculación: {len(recirculation_zones)}")
print(f"Tiempo de residencia medio: {residence_time:.1f} minutos")
```

### **Caso 3: Estudio de Validación**

```python
# ejemplo_validacion.py
config = {
    'domain': {
        'size': [2000, 2000, 200],
        'resolution': [80, 80, 20]
    },
    'meteorology': {
        'wind_speed': 5.0,
        'wind_direction': 225,
        'stability_class': 'D'
    },
    'sources': [
        {
            'type': 'area',
            'bounds': [[900, 1100], [900, 1100], [0, 5]],
            'emission_rate': {'NOx': 0.05, 'CO': 0.03},
            'name': 'industrial_area'
        }
    ],
    'validation': {
        'enable': True,
        'data_source': 'madrid_network',
        'metrics': ['rmse', 'mae', 'r2', 'fac2'],
        'time_period': ['2024-01-01', '2024-01-07']
    }
}

# Ejecutar simulación con validación
sim = AdvancedSimulationManager(config)
results = sim.run_complete_analysis()

# Mostrar métricas de validación
validation_metrics = results['validation']['metrics']
for metric, value in validation_metrics.items():
    print(f"{metric.upper()}: {value:.3f}")
```

---

## 🔗 **REFERENCIA DE APIs**

### **API Principal**

#### **Clase AdvancedSimulationManager**

```python
class AdvancedSimulationManager:
    """
    Gestor principal para simulaciones CFD avanzadas
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializar el gestor de simulación
        
        Args:
            config: Configuración completa de la simulación
        """
        
    def run_cfd_simulation(self, n_timesteps: int = 1000) -> Dict:
        """
        Ejecutar simulación CFD básica
        
        Args:
            n_timesteps: Número de pasos temporales
            
        Returns:
            Diccionario con resultados CFD
        """
        
    def run_sensitivity_analysis(self, n_samples: int = 1000) -> Dict:
        """
        Ejecutar análisis de sensibilidad
        
        Args:
            n_samples: Número de muestras para análisis
            
        Returns:
            Diccionario con resultados de sensibilidad
        """
        
    def run_validation(self, start_date: str, end_date: str) -> Dict:
        """
        Ejecutar validación experimental
        
        Args:
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            
        Returns:
            Diccionario con resultados de validación
        """
        
    def run_complete_analysis(self) -> Tuple[Dict, Dict]:
        """
        Ejecutar análisis científico completo
        
        Returns:
            Tupla con (resultados, métricas_científicas)
        """
```

### **API de Configuración**

#### **Esquema de Configuración**

```python
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "domain": {
            "type": "object",
            "properties": {
                "size": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 10},
                    "minItems": 3,
                    "maxItems": 3
                },
                "resolution": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 10},
                    "minItems": 3,
                    "maxItems": 3
                }
            },
            "required": ["size", "resolution"]
        },
        "meteorology": {
            "type": "object",
            "properties": {
                "wind_speed": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 30
                },
                "wind_direction": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 360
                },
                "stability_class": {
                    "type": "string",
                    "enum": ["A", "B", "C", "D", "E", "F"]
                }
            },
            "required": ["wind_speed", "wind_direction", "stability_class"]
        },
        "species": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "diffusivity": {
                        "type": "number",
                        "minimum": 1e-6,
                        "maximum": 1e-3
                    }
                },
                "required": ["name", "diffusivity"]
            }
        }
    },
    "required": ["domain", "meteorology", "species"]
}
```

---

## 🎯 **MEJORES PRÁCTICAS**

### **Diseño de Simulaciones**

#### **Selección de Dominio**

1. **Tamaño del dominio**:
   - Longitud: 10-20 veces la altura de edificios
   - Anchura: 5-10 veces la anchura de la zona de interés
   - Altura: 2-3 veces la altura de edificios

2. **Resolución de malla**:
   - Cerca de fuentes: Δx ≤ 2m
   - Zona de interés: Δx ≤ 5m
   - Lejos de fuentes: Δx ≤ 10m

#### **Condiciones de Contorno**

1. **Entrada (upwind)**:
   - Usar perfil logarítmico de viento
   - Especificar intensidad turbulenta (5-15%)
   - Definir temperatura estratificada

2. **Salida (downwind)**:
   - Condición de gradiente cero
   - Distancia mínima: 5 × altura_edificios

3. **Paredes**:
   - Condición no-slip para velocidad
   - Funciones de pared para turbulencia

### **Optimización de Rendimiento**

#### **Paralelización**

```python
# Configuración óptima para diferentes sistemas
SYSTEM_CONFIGS = {
    'laptop': {
        'threads': 4,
        'memory_limit': '4GB',
        'resolution_limit': [50, 50, 20]
    },
    'workstation': {
        'threads': 16,
        'memory_limit': '32GB',
        'resolution_limit': [200, 200, 50]
    },
    'hpc': {
        'threads': 64,
        'memory_limit': '256GB',
        'resolution_limit': [500, 500, 100]
    }
}
```

#### **Monitoreo de Simulación**

```python
def monitor_simulation(sim_manager):
    """
    Monitorear progreso y rendimiento de simulación
    """
    import time
    import psutil
    
    start_time = time.time()
    
    while sim_manager.is_running():
        # Información de progreso
        progress = sim_manager.get_progress()
        elapsed = time.time() - start_time
        
        # Información de recursos
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        
        print(f"Progreso: {progress:.1f}% | "
              f"Tiempo: {elapsed:.1f}s | "
              f"CPU: {cpu:.1f}% | "
              f"RAM: {memory:.1f}%")
        
        time.sleep(30)  # Actualizar cada 30 segundos
```

### **Validación y Verificación**

#### **Protocolo de Validación**

1. **Verificación (Code Verification)**:
   - Comparar con soluciones analíticas
   - Estudios de convergencia de malla
   - Verificar conservación de masa

2. **Validación (Solution Verification)**:
   - Comparar con datos experimentales
   - Usar múltiples conjuntos de datos
   - Aplicar métricas estándar

3. **Documentación**:
   - Registrar todas las comparaciones
   - Incluir intervalos de confianza
   - Documentar limitaciones

#### **Criterios de Calidad**

```python
QUALITY_CRITERIA = {
    'excellent': {
        'r2': 0.8,
        'fac2': 0.8,
        'fb': 0.25,
        'mg': 2.0
    },
    'good': {
        'r2': 0.6,
        'fac2': 0.6,
        'fb': 0.50,
        'mg': 4.0
    },
    'acceptable': {
        'r2': 0.4,
        'fac2': 0.4,
        'fb': 0.75,
        'mg': 8.0
    }
}
```

---

## 📞 **SOPORTE Y COMUNIDAD**

### **Recursos de Ayuda**

- **Documentación**: `docs/` (local) o [GitHub Pages](https://github.com/ErGranPepe/contamination_simulation/wiki)
- **Ejemplos**: `examples/` directorio con casos de uso
- **Foro**: [GitHub Discussions](https://github.com/ErGranPepe/contamination_simulation/discussions)
- **Issues**: [GitHub Issues](https://github.com/ErGranPepe/contamination_simulation/issues)

### **Contribuir al Proyecto**

1. **Fork** el repositorio
2. **Crear** rama para nueva funcionalidad
3. **Implementar** cambios con tests
4. **Documentar** cambios
5. **Enviar** Pull Request

### **Citar el Software**

```bibtex
@software{contamination_simulation,
  author = {Mario Díaz Gómez},
  title = {Advanced CFD Simulator for Urban Air Pollution},
  year = {2024},
  url = {https://github.com/ErGranPepe/contamination_simulation},
  version = {3.0}
}
```

---

*Esta guía está en constante actualización. Para la versión más reciente, consultar el repositorio oficial.*
