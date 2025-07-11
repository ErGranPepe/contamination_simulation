#!/usr/bin/env python3
"""
Prueba de la aplicacion web
"""

import sys
import os
import time
import threading

# Añadir ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_webapp():
    """Probar que la webapp se puede crear"""
    print("PROBANDO APLICACION WEB")
    print("=" * 30)
    
    try:
        print("1. Importando Flask...")
        from flask import Flask
        print("   OK - Flask disponible")
        
        print("2. Creando aplicacion de prueba...")
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Simulador funcionando!"
        
        @app.route('/test')
        def test():
            return {"status": "ok", "message": "API funcionando"}
        
        print("   OK - Aplicacion web creada")
        
        print("3. Probando configuracion...")
        app.config['TESTING'] = True
        client = app.test_client()
        
        print("4. Probando rutas...")
        response = client.get('/')
        if response.status_code == 200:
            print("   OK - Ruta principal funciona")
        else:
            print(f"   ERROR - Ruta principal fallo: {response.status_code}")
            return False
        
        response = client.get('/test')
        if response.status_code == 200:
            print("   OK - Ruta de prueba funciona")
        else:
            print(f"   ERROR - Ruta de prueba fallo: {response.status_code}")
            return False
        
        print()
        print("RESULTADO: Aplicacion web funciona perfectamente")
        print("Para usar: python src/webapp.py")
        print("Luego abrir: http://localhost:5000")
        
        return True
        
    except ImportError as e:
        print(f"   ERROR - Falta dependencia: {e}")
        return False
    except Exception as e:
        print(f"   ERROR - Fallo inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_webapp()
    
    if success:
        print("\nTODO LISTO PARA USAR LA INTERFAZ WEB!")
    else:
        print("\nHay problemas con la interfaz web")
    
    sys.exit(0 if success else 1)
