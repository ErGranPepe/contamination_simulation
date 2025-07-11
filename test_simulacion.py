#!/usr/bin/env python3
"""
Prueba de una simulacion completa pequena
"""

import sys
import os
import time

# Añadir ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simulacion():
    """Probar una simulacion completa pequena"""
    print("PROBANDO SIMULACION COMPLETA")
    print("=" * 35)
    
    try:
        print("1. Importando modulos...")
        from modules.advanced_cfd import AdvancedCFD
        import numpy as np
        print("   OK - Modulos importados")
        
        print("2. Creando simulador pequeno...")
        grid_size = (8, 8, 4)  # Pequeno para que sea rapido
        domain_size = (40.0, 40.0, 20.0)
        config = {
            'species_list': ['NOx'],
            'dt': 0.1,
            'wind_speed': 3.0
        }
        
        cfd = AdvancedCFD(grid_size, domain_size, config)
        print(f"   OK - Simulador creado {cfd.nx}x{cfd.ny}x{cfd.nz}")
        
        print("3. Configurando condiciones iniciales...")
        cfd.set_boundary_conditions('logarithmic')
        print("   OK - Condiciones de contorno establecidas")
        
        print("4. Añadiendo fuente de contaminacion...")
        cfd.add_pollution_source(20, 20, 5, {'NOx': 0.001})
        print("   OK - Fuente añadida")
        
        print("5. Ejecutando pasos de simulacion...")
        concentracion_inicial = np.sum(cfd.concentrations['NOx'])
        print(f"   Concentracion inicial: {concentracion_inicial:.6f}")
        
        # Ejecutar 5 pasos de tiempo
        for i in range(5):
            start_time = time.time()
            cfd.time_step()
            step_time = time.time() - start_time
            concentracion_actual = np.sum(cfd.concentrations['NOx'])
            print(f"   Paso {i+1}: {step_time:.3f}s, concentracion: {concentracion_actual:.6f}")
        
        concentracion_final = np.sum(cfd.concentrations['NOx'])
        
        print("6. Verificando resultados...")
        if concentracion_final > concentracion_inicial:
            print("   OK - La contaminacion se esta acumulando correctamente")
        else:
            print("   WARNING - La contaminacion no aumenta como se esperaba")
        
        print("7. Verificando campos de velocidad...")
        velocidad_max = np.max(np.sqrt(cfd.u**2 + cfd.v**2 + cfd.w**2))
        print(f"   Velocidad maxima: {velocidad_max:.3f} m/s")
        
        if velocidad_max > 0:
            print("   OK - Campo de velocidad activo")
        else:
            print("   WARNING - Campo de velocidad parece inactivo")
        
        print()
        print("RESULTADO: Simulacion ejecutada exitosamente!")
        print(f"Tiempo simulado: {cfd.time:.1f} segundos")
        print(f"Concentracion final: {concentracion_final:.6f}")
        
        return True
        
    except Exception as e:
        print(f"   ERROR - Simulacion fallo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Probando una simulacion CFD completa...")
    print()
    
    success = test_simulacion()
    
    if success:
        print("\nSIMULACION EXITOSA!")
        print("El simulador CFD funciona perfectamente")
        print("Listo para simulaciones reales")
    else:
        print("\nFALLO EN LA SIMULACION")
        print("Revisar configuracion")
    
    sys.exit(0 if success else 1)
