#!/usr/bin/env python3
"""
Prueba final de la webapp
"""

import sys
import os

# Añadir ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_webapp_final():
    """Prueba final de la webapp"""
    print("PRUEBA FINAL DE LA WEBAPP")
    print("=" * 30)
    
    try:
        print("1. Importando webapp simple...")
        from webapp_simple import app
        print("   OK - Webapp importada")
        
        print("2. Configurando para prueba...")
        app.config['TESTING'] = True
        client = app.test_client()
        print("   OK - Cliente configurado")
        
        print("3. Probando página principal...")
        response = client.get('/')
        if response.status_code == 200:
            print(f"   OK - Página principal (código: {response.status_code})")
        else:
            print(f"   ERROR - Página principal falló (código: {response.status_code})")
            return False
        
        print("4. Probando API de estado...")
        response = client.get('/api/status')
        if response.status_code == 200:
            data = response.get_json()
            print(f"   OK - API estado: {data['status']}")
        else:
            print(f"   ERROR - API estado falló")
            return False
        
        print("5. Probando página de test...")
        response = client.get('/test')
        if response.status_code == 200:
            print("   OK - Página de test funciona")
        else:
            print("   ERROR - Página de test falló")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ERROR - Fallo en webapp: {e}")
        return False

if __name__ == "__main__":
    print("Probando webapp final...")
    print()
    
    success = test_webapp_final()
    
    if success:
        print("\n*** WEBAPP FUNCIONA PERFECTAMENTE! ***")
        print()
        print("Para usar la interfaz web:")
        print("  1. Ejecutar: python src/webapp_simple.py")
        print("  2. Abrir navegador: http://localhost:5000")
        print("  3. Disfrutar de la interfaz intuitiva!")
        print()
        print("Características disponibles:")
        print("  - Configuración visual de simulaciones")
        print("  - Resultados en tiempo real")
        print("  - API REST para desarrolladores")
        print("  - Interfaz responsive")
        
    else:
        print("\nHay problemas con la webapp")
    
    sys.exit(0 if success else 1)
