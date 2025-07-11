#!/usr/bin/env python3
"""
Script Súper Sencillo para Verificar que Todo Funciona
====================================================

Este script comprueba que el simulador funciona correctamente,
explicado de forma que cualquier persona lo entienda.
"""

import sys
import os
import traceback

print("🚀 VERIFICANDO QUE EL SIMULADOR FUNCIONA")
print("=" * 50)

def test_python_funciona():
    """¿Python está instalado y funciona?"""
    print("🔧 Comprobando Python...")
    try:
        import sys
        version = sys.version.split()[0]
        print(f"✅ Python {version} funciona perfectamente")
        return True
    except:
        print("❌ Python no funciona")
        return False

def test_librerias_importantes():
    """¿Están todas las librerías que necesitamos?"""
    print("🔧 Comprobando librerías importantes...")
    
    librerias_necesarias = [
        ("numpy", "para hacer cálculos matemáticos rápidos"),
        ("matplotlib", "para hacer gráficos bonitos"),
        ("pandas", "para manejar datos como Excel"),
        ("scipy", "para cálculos científicos avanzados"),
        ("flask", "para crear la página web")
    ]
    
    todas_ok = True
    
    for libreria, descripcion in librerias_necesarias:
        try:
            __import__(libreria)
            print(f"✅ {libreria} - {descripcion}")
        except ImportError:
            print(f"❌ {libreria} NO ENCONTRADA - {descripcion}")
            todas_ok = False
    
    return todas_ok

def test_modulos_del_simulador():
    """¿Nuestros módulos del simulador funcionan?"""
    print("🔧 Comprobando módulos del simulador...")
    
    # Añadir la carpeta src para que Python encuentre nuestros archivos
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    modulos_nuestros = [
        ("modules.advanced_cfd", "el cerebro que simula el aire y la contaminación"),
        ("modules.sensitivity_analysis", "el que analiza qué factores son más importantes"),
        ("modules.validation_module", "el que comprueba que nuestros resultados son correctos"),
        ("modules.CS_optimized", "el simulador básico súper rápido")
    ]
    
    todos_ok = True
    
    for modulo, descripcion in modulos_nuestros:
        try:
            __import__(modulo)
            print(f"✅ {modulo} - {descripcion}")
        except Exception as e:
            print(f"❌ {modulo} NO FUNCIONA - {descripcion}")
            print(f"   Error: {str(e)}")
            todos_ok = False
    
    return todos_ok

def test_simulacion_basica():
    """¿Podemos hacer una simulación súper simple?"""
    print("🔧 Probando una simulación básica...")
    
    try:
        # Importar lo que necesitamos
        from modules.advanced_cfd import AdvancedCFD
        import numpy as np
        
        print("   📋 Creando un simulador pequeñito...")
        
        # Crear un simulador súper pequeño para probar
        grid_size = (4, 4, 2)  # Una malla pequeñita de 4x4x2
        domain_size = (20.0, 20.0, 10.0)  # Un área de 20m x 20m x 10m
        config = {
            'species_list': ['NOx'],  # Solo simulamos NOx
            'dt': 0.1,  # Pasos de tiempo pequeños
            'wind_speed': 3.0  # Viento suave
        }
        
        # Crear el simulador
        simulador = AdvancedCFD(grid_size, domain_size, config)
        
        print("   📋 Configurando condiciones...")
        simulador.set_boundary_conditions('logarithmic')
        
        print("   📋 Añadiendo una fuente de contaminación...")
        simulador.add_pollution_source(10, 10, 5, {'NOx': 0.001})
        
        print("   📋 Ejecutando un paso de simulación...")
        simulador.time_step()
        
        print("   📋 Verificando que hay contaminación...")
        total_contaminacion = np.sum(simulador.concentrations['NOx'])
        
        if total_contaminacion > 0:
            print(f"✅ ¡Funciona! Hay {total_contaminacion:.6f} unidades de contaminación")
            return True
        else:
            print("❌ No se detectó contaminación, algo falla")
            return False
            
    except Exception as e:
        print(f"❌ Error en la simulación: {str(e)}")
        print("   Detalles del error:")
        print("  ", str(e))
        return False

def test_interfaz_web():
    """¿La página web se puede crear?"""
    print("🔧 Comprobando interfaz web...")
    
    try:
        from flask import Flask
        
        # Crear una mini aplicación web de prueba
        app = Flask(__name__)
        
        @app.route('/')
        def inicio():
            return "¡El simulador web funciona!"
        
        print("✅ La interfaz web se puede crear")
        print("   (Para verla funcionando, ejecuta: python src/webapp.py)")
        return True
        
    except Exception as e:
        print(f"❌ Error con la interfaz web: {str(e)}")
        return False

def verificar_archivos_importantes():
    """¿Están todos los archivos importantes?"""
    print("🔧 Comprobando archivos importantes...")
    
    archivos_importantes = [
        ("src/main_advanced.py", "el programa principal científico"),
        ("src/webapp.py", "la aplicación web"),
        ("src/modules/advanced_cfd.py", "el simulador avanzado"),
        ("docs/TECHNICAL_DOCUMENTATION_EUROPEAN_STANDARDS.md", "la documentación técnica"),
        ("docs/USER_GUIDE_COMPLETE.md", "la guía de usuario"),
        ("PROYECTO_COMPLETO_TRIBUNAL_EUROPEO.md", "el documento final")
    ]
    
    todos_existen = True
    
    for archivo, descripcion in archivos_importantes:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - {descripcion}")
        else:
            print(f"❌ {archivo} NO ENCONTRADO - {descripcion}")
            todos_existen = False
    
    return todos_existen

def verificar_todo():
    """Función principal que verifica todo el sistema"""
    
    print("Vamos a comprobar que todo el simulador funciona correctamente...")
    print("Esto es como revisar un coche antes de un viaje largo 🚗")
    print()
    
    pruebas = [
        ("Python básico", test_python_funciona),
        ("Librerías necesarias", test_librerias_importantes),
        ("Archivos importantes", verificar_archivos_importantes),
        ("Módulos del simulador", test_modulos_del_simulador),
        ("Simulación básica", test_simulacion_basica),
        ("Interfaz web", test_interfaz_web)
    ]
    
    resultados = []
    
    for nombre, test_func in pruebas:
        print(f"\n📋 Probando: {nombre}")
        print("-" * 40)
        
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error inesperado en {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN FINAL")
    print("=" * 50)
    
    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    print(f"Pruebas realizadas: {total}")
    print(f"Pruebas exitosas: {exitosas}")
    print(f"Pruebas fallidas: {total - exitosas}")
    print(f"Porcentaje de éxito: {(exitosas/total)*100:.1f}%")
    
    print("\n📋 Detalle de resultados:")
    for nombre, resultado in resultados:
        estado = "✅ BIEN" if resultado else "❌ MAL"
        print(f"  {estado} - {nombre}")
    
    if exitosas == total:
        print("\n🎉 ¡PERFECTO! Todo funciona correctamente")
        print("🏆 El simulador está listo para usar")
        print("🚀 Puedes presentarlo al tribunal con confianza")
        print("\nPara usar el simulador:")
        print("  • Página web: python src/webapp.py")
        print("  • Programa avanzado: python src/main_advanced.py")
        print("  • Programa básico: python src/main.py")
        
    elif exitosas >= total * 0.8:  # Si al menos 80% funciona
        print("\n🟨 BASTANTE BIEN - Funciona con pequeños problemas")
        print("🔧 Hay algunos errores menores pero el sistema es usable")
        print("💡 Mira los errores arriba para solucionarlos")
        
    else:
        print("\n🟥 PROBLEMAS SERIOS - Necesita reparación")
        print("🔧 Hay varios errores que impiden el funcionamiento correcto")
        print("💡 Revisa los errores arriba y las instrucciones de instalación")
    
    return exitosas == total

if __name__ == "__main__":
    print("🔍 VERIFICADOR DEL SIMULADOR DE CONTAMINACIÓN")
    print("=" * 60)
    print("Este programa comprueba que todo funciona bien")
    print("Es como hacer una revisión técnica del coche 🚗✅")
    print()
    
    resultado_final = verificar_todo()
    
    if resultado_final:
        print("\n🌟 ¡EL SIMULADOR ESTÁ PERFECTO!")
        print("Listo para impresionar al tribunal 🏆")
    else:
        print("\n⚠️  Hay algunos problemillas que arreglar")
        print("Pero no te preocupes, son fáciles de solucionar 🔧")
    
    print("\n¡Gracias por usar el verificador! 😊")
