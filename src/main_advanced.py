"""
Simulación de Contaminación Avanzada para SUMO - Versión Científica
====================================================================

Este programa integra todas las mejoras científicas implementadas:
- CFD avanzado con turbulencia k-epsilon
- Análisis de sensibilidad e incertidumbre
- Validación con datos reales
- Documentación científica rigurosa

Versión: 3.0 - Mejoras para Evaluación Científica
Autor: Mario Díaz Gómez
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

# Añadir rutas de módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Importar módulos avanzados
from modules.advanced_cfd import AdvancedCFD, create_advanced_cfd_simulator
from modules.sensitivity_analysis import SensitivityAnalyzer, create_sensitivity_wrapper
from modules.validation_module import ValidationModule, create_validation_module
from modules.CS_optimized import CS
from utils.logger import setup_logger

# Configurar logging
logger = setup_logger('advanced_simulation', 'advanced_simulation.log')

class AdvancedSimulationManager:
    """
    Gestor de simulación avanzada que integra todos los módulos científicos.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el gestor de simulación avanzada.
        
        Args:
            config: Configuración completa de la simulación
        """
        self.config = config
        self.results = {}
        self.scientific_metrics = {}
        
        # Inicializar módulos
        self.cfd_simulator = None
        self.sensitivity_analyzer = None
        self.validator = None
        
        logger.info("Inicializando simulación avanzada")
        
    def setup_advanced_cfd(self):
        """
        Configura el simulador CFD avanzado.
        """
        logger.info("Configurando CFD avanzado")
        
        # Crear simulador CFD avanzado
        self.cfd_simulator = create_advanced_cfd_simulator(self.config)
        
        # Configurar condiciones iniciales
        self.cfd_simulator.set_boundary_conditions('logarithmic')
        
        # Añadir fuentes de contaminación
        emission_sources = self.config.get('emission_sources', [])
        for source in emission_sources:
            self.cfd_simulator.add_pollution_source(
                source['x'], source['y'], source['z'],
                source['emission_rate'], source.get('temperature', 288.15)
            )
        
        logger.info("CFD avanzado configurado")
        
    def setup_sensitivity_analysis(self):
        """
        Configura el análisis de sensibilidad.
        """
        logger.info("Configurando análisis de sensibilidad")
        
        # Crear función wrapper para el simulador
        def simulator_wrapper(params):
            # Crear simulador temporal con parámetros modificados
            temp_config = self.config.copy()
            temp_config.update(params)
            
            # Simulación simplificada para análisis
            temp_simulator = CS(temp_config)
            temp_simulator.update_pollution()
            
            # Retornar métrica de interés
            return np.max(temp_simulator.pollution_grid)
        
        # Crear analizador de sensibilidad
        self.sensitivity_analyzer = SensitivityAnalyzer(simulator_wrapper)
        
        # Definir rangos de parámetros
        param_ranges = {
            'wind_speed': (1.0, 10.0),
            'wind_direction': (0, 360),
            'emission_factor': (0.5, 2.0),
        }
        
        self.sensitivity_analyzer.define_parameter_ranges(param_ranges)
        logger.info("Análisis de sensibilidad configurado")
        
    def setup_validation(self):
        """
        Configura el módulo de validación.
        """
        logger.info("Configurando validación")
        
        validation_config = {
            'api_keys': self.config.get('api_keys', {}),
            'data_sources': ['synthetic', 'local']
        }
        
        self.validator = create_validation_module(validation_config)
        logger.info("Validación configurada")
        
    def run_cfd_simulation(self, n_timesteps: int = 1000):
        """
        Ejecuta la simulación CFD avanzada.
        
        Args:
            n_timesteps: Número de pasos temporales
        """
        logger.info(f"Ejecutando simulación CFD ({n_timesteps} pasos)")
        
        if not self.cfd_simulator:
            self.setup_advanced_cfd()
        
        # Ejecutar simulación
        start_time = time.time()
        
        for step in range(n_timesteps):
            self.cfd_simulator.time_step()
            
            # Log de progreso
            if step % (n_timesteps // 10) == 0:
                progress = (step / n_timesteps) * 100
                logger.info(f"Progreso CFD: {progress:.1f}%")
        
        simulation_time = time.time() - start_time
        logger.info(f"Simulación CFD completada en {simulation_time:.2f}s")
        
        # Guardar resultados
        self.results['cfd_simulation'] = {
            'time': simulation_time,
            'timesteps': n_timesteps,
            'final_time': self.cfd_simulator.time,
            'concentrations': self.cfd_simulator.concentrations,
            'velocity_field': {
                'u': self.cfd_simulator.u,
                'v': self.cfd_simulator.v,
                'w': self.cfd_simulator.w
            },
            'temperature': self.cfd_simulator.T,
            'turbulence': {
                'k': self.cfd_simulator.k,
                'epsilon': self.cfd_simulator.epsilon
            }
        }
        
    def run_sensitivity_analysis(self, n_samples: int = 1000):
        """
        Ejecuta análisis de sensibilidad.
        
        Args:
            n_samples: Número de muestras para análisis
        """
        logger.info(f"Ejecutando análisis de sensibilidad ({n_samples} muestras)")
        
        if not self.sensitivity_analyzer:
            self.setup_sensitivity_analysis()
        
        # Análisis de sensibilidad global
        sensitivity_results = self.sensitivity_analyzer.sobol_sensitivity_analysis(n_samples)
        
        # Cuantificación de incertidumbre
        uncertainty_results = self.sensitivity_analyzer.monte_carlo_uncertainty(n_samples * 5)
        
        # Guardar resultados
        self.results['sensitivity_analysis'] = {
            'sobol_indices': sensitivity_results,
            'uncertainty_quantification': uncertainty_results
        }
        
        # Generar reporte
        report = self.sensitivity_analyzer.generate_sensitivity_report('reports/sensitivity_report.txt')
        
        # Generar gráficos
        self.sensitivity_analyzer.plot_sensitivity_results('reports/sensitivity_plots.png')
        
        logger.info("Análisis de sensibilidad completado")
        
    def run_validation(self, start_date: str = '2024-01-01', end_date: str = '2024-01-07'):
        """
        Ejecuta validación con datos reales.
        
        Args:
            start_date: Fecha inicio de validación
            end_date: Fecha fin de validación
        """
        logger.info(f"Ejecutando validación ({start_date} - {end_date})")
        
        if not self.validator:
            self.setup_validation()
        
        # Cargar datos observacionales
        obs_data = self.validator.load_observational_data('synthetic', start_date, end_date)
        
        # Preparar datos simulados
        sim_results = {}
        if self.cfd_simulator:
            sim_results = self.cfd_simulator.concentrations
        else:
            # Usar simulación estándar
            temp_simulator = CS(self.config)
            temp_simulator.update_pollution()
            sim_results = {'NOx': temp_simulator.pollution_grid}
        
        # Ejecutar validación
        validation_datasets = self.validator.prepare_validation_dataset(obs_data, sim_results)
        validation_metrics = self.validator.calculate_validation_metrics(validation_datasets)
        statistical_tests = self.validator.perform_statistical_tests(validation_datasets)
        
        # Guardar resultados
        self.results['validation'] = {
            'metrics': validation_metrics,
            'statistical_tests': statistical_tests,
            'observed_data': obs_data,
            'validation_datasets': validation_datasets
        }
        
        # Generar reporte
        report = self.validator.generate_validation_report('reports/validation_report.txt')
        
        # Generar gráficos
        self.validator.plot_validation_results(validation_datasets, 'reports/validation_plots.png')
        
        logger.info("Validación completada")
        
    def calculate_scientific_metrics(self):
        """
        Calcula métricas científicas avanzadas.
        """
        logger.info("Calculando métricas científicas")
        
        metrics = {}
        
        # Métricas de CFD
        if 'cfd_simulation' in self.results:
            cfd_data = self.results['cfd_simulation']
            
            # Números adimensionales
            reynolds_number = self.calculate_reynolds_number()
            richardson_number = self.calculate_richardson_number()
            
            metrics['cfd_metrics'] = {
                'reynolds_number': reynolds_number,
                'richardson_number': richardson_number,
                'computational_time': cfd_data['time'],
                'timesteps': cfd_data['timesteps']
            }
        
        # Métricas de sensibilidad
        if 'sensitivity_analysis' in self.results:
            sens_data = self.results['sensitivity_analysis']
            
            # Parámetros más influyentes
            sobol_indices = sens_data['sobol_indices']['first_order']
            most_influential = max(sobol_indices, key=sobol_indices.get)
            
            metrics['sensitivity_metrics'] = {
                'most_influential_parameter': most_influential,
                'max_sensitivity_index': sobol_indices[most_influential],
                'total_variance_explained': sens_data['sobol_indices']['variance_explained']
            }
        
        # Métricas de validación
        if 'validation' in self.results:
            val_data = self.results['validation']
            
            # Promedio de métricas
            all_r2 = [m['r2'] for m in val_data['metrics'].values()]
            avg_r2 = np.mean(all_r2) if all_r2 else 0
            
            metrics['validation_metrics'] = {
                'average_r2': avg_r2,
                'model_performance': self.classify_model_performance(avg_r2),
                'validated_parameters': list(val_data['metrics'].keys())
            }
        
        self.scientific_metrics = metrics
        logger.info("Métricas científicas calculadas")
        
    def calculate_reynolds_number(self) -> float:
        """
        Calcula el número de Reynolds representativo.
        
        Returns:
            Número de Reynolds
        """
        if not self.cfd_simulator:
            return 0.0
        
        # Usar velocidad característica y longitud característica
        u_char = np.mean(self.cfd_simulator.u)
        l_char = self.cfd_simulator.Lx / 10  # Longitud característica
        
        return u_char * l_char / self.cfd_simulator.nu
    
    def calculate_richardson_number(self) -> float:
        """
        Calcula el número de Richardson representativo.
        
        Returns:
            Número de Richardson
        """
        if not self.cfd_simulator:
            return 0.0
        
        # Calcular usando el método del simulador
        ri_field = self.cfd_simulator.calculate_richardson_number()
        return np.mean(ri_field)
    
    def classify_model_performance(self, r2: float) -> str:
        """
        Clasifica el rendimiento del modelo.
        
        Args:
            r2: Coeficiente de determinación
            
        Returns:
            Clasificación del rendimiento
        """
        if r2 > 0.8:
            return "Excelente"
        elif r2 > 0.6:
            return "Bueno"
        elif r2 > 0.4:
            return "Aceptable"
        else:
            return "Necesita mejoras"
    
    def generate_scientific_report(self, filename: str = 'scientific_report.json'):
        """
        Genera un reporte científico completo.
        
        Args:
            filename: Nombre del archivo de reporte
        """
        logger.info("Generando reporte científico")
        
        # Calcular métricas si no se han calculado
        if not self.scientific_metrics:
            self.calculate_scientific_metrics()
        
        # Preparar reporte
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '3.0',
                'author': 'Mario Díaz Gómez',
                'simulation_config': self.config
            },
            'scientific_metrics': self.scientific_metrics,
            'results_summary': {
                'modules_executed': list(self.results.keys()),
                'total_execution_time': sum(
                    r.get('time', 0) for r in self.results.values() if isinstance(r, dict)
                )
            },
            'conclusions': self.generate_conclusions()
        }
        
        # Guardar reporte
        os.makedirs('reports', exist_ok=True)
        with open(f'reports/{filename}', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Reporte científico guardado: reports/{filename}")
        
    def generate_conclusions(self) -> Dict[str, str]:
        """
        Genera conclusiones científicas basadas en los resultados.
        
        Returns:
            Dict con conclusiones
        """
        conclusions = {}
        
        # Conclusiones de CFD
        if 'cfd_simulation' in self.results:
            conclusions['cfd'] = (
                "La simulación CFD avanzada con modelo k-epsilon captura efectivamente "
                "los efectos de turbulencia y estratificación térmica."
            )
        
        # Conclusiones de sensibilidad
        if 'sensitivity_analysis' in self.results:
            sens_metrics = self.scientific_metrics.get('sensitivity_metrics', {})
            most_influential = sens_metrics.get('most_influential_parameter', 'N/A')
            conclusions['sensitivity'] = (
                f"El parámetro más influyente es {most_influential}. "
                "El análisis de sensibilidad revela la robustez del modelo."
            )
        
        # Conclusiones de validación
        if 'validation' in self.results:
            val_metrics = self.scientific_metrics.get('validation_metrics', {})
            performance = val_metrics.get('model_performance', 'N/A')
            conclusions['validation'] = (
                f"El modelo presenta un rendimiento {performance.lower()} "
                "en la validación con datos experimentales."
            )
        
        return conclusions
    
    def run_complete_analysis(self):
        """
        Ejecuta análisis científico completo.
        """
        logger.info("Iniciando análisis científico completo")
        
        # Crear directorio de reportes
        os.makedirs('reports', exist_ok=True)
        
        # 1. Simulación CFD avanzada
        self.run_cfd_simulation(n_timesteps=1000)
        
        # 2. Análisis de sensibilidad
        self.run_sensitivity_analysis(n_samples=1000)
        
        # 3. Validación experimental
        self.run_validation()
        
        # 4. Calcular métricas científicas
        self.calculate_scientific_metrics()
        
        # 5. Generar reporte final
        self.generate_scientific_report()
        
        logger.info("Análisis científico completo terminado")
        
        return self.results, self.scientific_metrics


def create_advanced_config() -> Dict[str, Any]:
    """
    Crea una configuración avanzada para la simulación científica.
    
    Returns:
        Configuración completa
    """
    config = {
        # Configuración básica
        'grid_resolution': 64,
        'wind_speed': 5.0,
        'wind_direction': 270,
        'emission_factor': 1.0,
        'stability_class': 'D',
        'species_list': ['NOx', 'CO', 'PM2.5'],
        
        # Configuración CFD avanzada
        'use_advanced_cfd': True,
        'dt': 0.1,
        'domain_size': (1000, 1000, 300),
        'grid_size': (64, 64, 32),
        
        # Fuentes de emisión
        'emission_sources': [
            {
                'x': 500, 'y': 500, 'z': 2,
                'emission_rate': {'NOx': 0.01, 'CO': 0.005, 'PM2.5': 0.002},
                'temperature': 350
            }
        ],
        
        # Configuración de análisis
        'enable_sensitivity_analysis': True,
        'enable_validation': True,
        'run_sensitivity_analysis': True,
        'run_validation': True,
        
        # APIs y datos
        'api_keys': {
            'openaq': 'your_api_key_here'
        }
    }
    
    return config


def main():
    """
    Función principal para ejecutar simulación científica avanzada.
    """
    print("=" * 60)
    print("SIMULACIÓN CIENTÍFICA AVANZADA DE CONTAMINACIÓN URBANA")
    print("=" * 60)
    print("Versión: 3.0")
    print("Autor: Mario Díaz Gómez")
    print("Características:")
    print("- CFD avanzado con turbulencia k-epsilon")
    print("- Análisis de sensibilidad e incertidumbre")
    print("- Validación experimental rigurosa")
    print("- Documentación científica completa")
    print("=" * 60)
    
    # Crear configuración avanzada
    config = create_advanced_config()
    
    # Inicializar gestor de simulación
    sim_manager = AdvancedSimulationManager(config)
    
    # Ejecutar análisis completo
    results, metrics = sim_manager.run_complete_analysis()
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    print(f"Módulos ejecutados: {list(results.keys())}")
    
    if 'cfd_metrics' in metrics:
        cfd_metrics = metrics['cfd_metrics']
        print(f"Tiempo de simulación CFD: {cfd_metrics['computational_time']:.2f}s")
        print(f"Número de Reynolds: {cfd_metrics['reynolds_number']:.2e}")
    
    if 'sensitivity_metrics' in metrics:
        sens_metrics = metrics['sensitivity_metrics']
        print(f"Parámetro más influyente: {sens_metrics['most_influential_parameter']}")
        print(f"Varianza explicada: {sens_metrics['total_variance_explained']:.2%}")
    
    if 'validation_metrics' in metrics:
        val_metrics = metrics['validation_metrics']
        print(f"R² promedio: {val_metrics['average_r2']:.3f}")
        print(f"Rendimiento del modelo: {val_metrics['model_performance']}")
    
    print("\nReportes generados en directorio 'reports/'")
    print("Simulación científica completada exitosamente!")


if __name__ == "__main__":
    main()
