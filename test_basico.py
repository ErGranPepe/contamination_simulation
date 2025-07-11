#!/usr/bin/env python3
"""
Prueba basica del sistema sin emojis
"""

import sys
import os

# Añadir ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("PRUEBA BASICA DEL SISTEMA")
print("=" * 40)

def test_imports():
    """Probar importaciones basicas"""
    print("1. Probando imports basicos...")
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        print("   OK - NumPy y Matplotlib funcionan")
        return True
    except ImportError as e:
        print(f"   ERROR - Falta libreria: {e}")
        return False

def test_config():
    """Probar configuracion"""
    print("2. Probando configuracion...")
    try:
        from main_advanced import create_advanced_config
        config = create_advanced_config()
        print(f"   OK - Configuracion creada con {len(config)} parametros")
        return True
    except Exception as e:
        print(f"   ERROR - No se puede crear config: {e}")
        return False

def test_numpy():
    """Probar calculos numericos"""
    print("3. Probando calculos numericos...")
    try:
        import numpy as np
        test_array = np.array([1, 2, 3, 4, 5])
        suma = np.sum(test_array)
        if suma == 15:
            print(f"   OK - Suma correcta: {suma}")
            return True
        else:
            print(f"   ERROR - Suma incorrecta: {suma}")
            return False
    except Exception as e:
        print(f"   ERROR - Fallo en calculos: {e}")
        return False

def test_advanced_cfd():
    """Probar CFD avanzado"""
    print("4. Probando CFD avanzado...")
    try:
        from modules.advanced_cfd import AdvancedCFD
        
        # Crear simulador pequeño
        grid_size = (4, 4, 2)
        domain_size = (20.0, 20.0, 10.0)
        config = {
            'species_list': ['NOx'],
            'dt': 0.1,
            'wind_speed': 3.0
        }
        
        cfd = AdvancedCFD(grid_size, domain_size, config)
        print(f"   OK - CFD creado con malla {cfd.nx}x{cfd.ny}x{cfd.nz}")
        return True
    except Exception as e:
        print(f"   ERROR - CFD fallo: {e}")
        return False

def test_sensitivity():
    """Probar analisis de sensibilidad"""
    print("5. Probando analisis de sensibilidad...")
    try:
        from modules.sensitivity_analysis import SensitivityAnalyzer
        
        def dummy_func(params):
            return params.get('x', 1.0) * 2
        
        analyzer = SensitivityAnalyzer(dummy_func)
        analyzer.define_parameter_ranges({'x': (0.0, 1.0)})
        print("   OK - Analizador de sensibilidad creado")
        return True
    except Exception as e:
        print(f"   ERROR - Sensibilidad fallo: {e}")
        return False

def test_validation():
    """Probar modulo de validacion"""
    print("6. Probando modulo de validacion...")
    try:
        from modules.validation_module import ValidationModule
        
        config = {'api_keys': {}, 'data_sources': ['synthetic']}
        validator = ValidationModule(config)
        print("   OK - Modulo de validacion creado")
        return True
    except Exception as e:
        print(f"   ERROR - Validacion fallo: {e}")
        return False

def main():
    """Funcion principal"""
    print("Verificando sistema de simulacion CFD...")
    print()
    
    tests = [
        ("Imports basicos", test_imports),
        ("Configuracion", test_config),
        ("Calculos numericos", test_numpy),
        ("CFD avanzado", test_advanced_cfd),
        ("Analisis sensibilidad", test_sensitivity),
        ("Modulo validacion", test_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"   FALLO: {name}")
        except Exception as e:
            print(f"   EXCEPCION en {name}: {e}")
    
    print()
    print("=" * 40)
    print("RESUMEN:")
    print(f"Pruebas realizadas: {total}")
    print(f"Pruebas exitosas: {passed}")
    print(f"Pruebas fallidas: {total - passed}")
    print(f"Porcentaje exito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print()
        print("PERFECTO! Todo funciona correctamente")
        print("El sistema esta listo para usar")
        print()
        print("Para usar el simulador:")
        print("  - Pagina web: python src/webapp.py")
        print("  - Programa avanzado: python src/main_advanced.py")
        
    elif passed >= total * 0.8:
        print()
        print("BASTANTE BIEN - Funciona con pequeños problemas")
        
    else:
        print()
        print("PROBLEMAS SERIOS - Necesita reparacion")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
