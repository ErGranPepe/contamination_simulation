#!/usr/bin/env python3
"""
Prueba rápida del funcionamiento básico
"""

import sys
import os

# Añadir ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🔧 PRUEBA RÁPIDA DEL SISTEMA")
print("=" * 40)

try:
    print("1️⃣ Importando librerías básicas...")
    import numpy as np
    import matplotlib.pyplot as plt
    print("   ✅ NumPy y Matplotlib OK")
    
    print("2️⃣ Probando cálculos básicos...")
    test_array = np.array([1, 2, 3, 4, 5])
    suma = np.sum(test_array)
    print(f"   ✅ Suma de [1,2,3,4,5] = {suma}")
    
    print("3️⃣ Probando configuración avanzada...")
    from main_advanced import create_advanced_config
    config = create_advanced_config()
    print(f"   ✅ Configuración creada con {len(config)} parámetros")
    
    print("4️⃣ Probando simulador básico...")
    from modules.CS_optimized import CS
    
    # Configuración mínima para probar
    test_config = {
        'grid_resolution': 10,
        'wind_speed': 5.0,
        'wind_direction': 270,
        'emission_factor': 1.0,
        'stability_class': 'D',
        'species_list': ['NOx']
    }
    
    # Crear un simulador sin SUMO para probar solo el núcleo
    print("   📋 Creando simulador de prueba...")
    
    # Mock de traci para que no falle
    class MockTraci:
        class simulation:
            @staticmethod
            def getNetBoundary():
                return [(0, 0), (100, 100)]
    
    # Sustituir temporalmente traci
    import modules.CS_optimized
    modules.CS_optimized.traci = MockTraci()
    
    cs = CS(test_config)
    print("   ✅ Simulador básico creado")
    
    print("5️⃣ Verificando estructura de datos...")
    print(f"   ✅ Malla: {cs.pollution_grid.shape}")
    print(f"   ✅ Especies: {list(cs.pollution_grids.keys())}")
    
    print("\n🎉 ¡PRUEBA BÁSICA COMPLETADA!")
    print("✅ El sistema funciona correctamente")
    print("🚀 Listo para usar")
    
except Exception as e:
    print(f"\n❌ Error en la prueba: {e}")
    print("🔧 Revisar instalación de dependencias")
    import traceback
    traceback.print_exc()
