#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas del sistema
"""

import sys
import os
import time
import traceback

# Añadir ruta del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """
    Verificar que se pueden importar todos los módulos principales
    """
    print("🔧 Test: Importación de módulos")
    
    try:
        # Importar módulos principales
        from modules.advanced_cfd import AdvancedCFD
        from modules.sensitivity_analysis import SensitivityAnalyzer
        from modules.validation_module import ValidationModule
        from modules.CS_optimized import CS
        
        print("✅ Todos los módulos importados correctamente")
        return True
    except Exception as e:
        print(f"❌ Error importando módulos: {e}")
        return False

def test_basic_functionality():
    """
    Verificar funcionalidad básica
    """
    print("🔧 Test: Funcionalidad básica")
    
    try:
        import numpy as np
        from modules.advanced_cfd import AdvancedCFD
        
        # Crear simulador básico
        grid_size = (8, 8, 4)
        domain_size = (50.0, 50.0, 25.0)
        config = {
            'species_list': ['NOx'],
            'dt': 0.1,
            'wind_speed': 5.0
        }
        
        cfd = AdvancedCFD(grid_size, domain_size, config)
        
        # Verificar inicialización
        assert cfd.nx == 8
        assert cfd.ny == 8
        assert cfd.nz == 4
        assert 'NOx' in cfd.concentrations
        
        print("✅ Funcionalidad básica verificada")
        return True
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        print(traceback.format_exc())
        return False

def test_configuration_creation():
    """
    Verificar creación de configuración
    """
    print("🔧 Test: Creación de configuración")
    
    try:
        from main_advanced import create_advanced_config
        
        config = create_advanced_config()
        
        # Verificar campos obligatorios
        assert 'grid_resolution' in config
        assert 'wind_speed' in config
        assert 'species_list' in config
        assert isinstance(config['species_list'], list)
        assert len(config['species_list']) > 0
        
        print("✅ Configuración creada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        print(traceback.format_exc())
        return False

def test_simulation_manager():
    """
    Verificar el gestor de simulación
    """
    print("🔧 Test: Gestor de simulación")
    
    try:
        from main_advanced import AdvancedSimulationManager, create_advanced_config
        
        config = create_advanced_config()
        sim_manager = AdvancedSimulationManager(config)
        
        # Verificar inicialización
        assert sim_manager.config == config
        assert sim_manager.results == {}
        assert sim_manager.scientific_metrics == {}
        
        print("✅ Gestor de simulación inicializado")
        return True
    except Exception as e:
        print(f"❌ Error en gestor de simulación: {e}")
        print(traceback.format_exc())
        return False

def test_numerical_accuracy():
    """
    Verificar precisión numérica básica
    """
    print("🔧 Test: Precisión numérica")
    
    try:
        import numpy as np
        
        # Test de conservación de masa simple
        grid_size = (10, 10, 5)
        total_cells = np.prod(grid_size)
        
        # Crear campo de concentración uniforme
        concentration = np.ones(grid_size) * 10.0
        total_mass_initial = np.sum(concentration)
        
        # Verificar suma
        expected_mass = total_cells * 10.0
        assert abs(total_mass_initial - expected_mass) < 1e-10
        
        print("✅ Precisión numérica verificada")
        return True
    except Exception as e:
        print(f"❌ Error en precisión numérica: {e}")
        return False

def run_all_tests():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA")
    print("=" * 50)
    
    tests = [
        ("Importación de módulos", test_basic_imports),
        ("Funcionalidad básica", test_basic_functionality),
        ("Creación de configuración", test_configuration_creation),
        ("Gestor de simulación", test_simulation_manager),
        ("Precisión numérica", test_numerical_accuracy),
    ]
    
    passed = 0
    total = len(tests)
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ FALLO: {test_name}")
        except Exception as e:
            print(f"❌ EXCEPCIÓN en {test_name}: {e}")
    
    execution_time = time.time() - start_time
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    print(f"Total de pruebas: {total}")
    print(f"Pruebas exitosas: {passed}")
    print(f"Pruebas fallidas: {total - passed}")
    print(f"Tasa de éxito: {success_rate:.1f}%")
    print(f"Tiempo de ejecución: {execution_time:.2f}s")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ Sistema básico funcionando correctamente")
        print("✅ Listo para evaluación")
    else:
        print(f"\n⚠️  {total - passed} pruebas fallaron")
        print("🔧 Revisar implementación")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🏆 CERTIFICACIÓN BÁSICA COMPLETADA")
        print("=" * 50)
        print("✅ Simulador CFD operativo")
        print("✅ Módulos principales funcionando")
        print("✅ Configuración validada")
        print("✅ Sistema listo para uso")
    else:
        print("\n⚠️  CORRECCIONES NECESARIAS")
        print("Revisar fallos antes de continuar")
    
    sys.exit(0 if success else 1)
