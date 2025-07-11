#!/usr/bin/env python3
"""
Prueba rapida de la webapp
"""

import sys
import os
import threading
import time

# Añadir ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_webapp_startup():
    """Probar que la webapp arranca correctamente"""
    print("PROBANDO ARRANQUE DE WEBAPP")
    print("=" * 30)
    
    try:
        print("1. Importando webapp...")
        from webapp import app
        print("   OK - Webapp importada")
        
        print("2. Configurando para prueba...")
        app.config['TESTING'] = True
        client = app.test_client()
        print("   OK - Cliente de prueba creado")
        
        print("3. Probando ruta principal...")
        response = client.get('/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   OK - Página principal responde")
            return True
        else:
            print("   ERROR - Página principal no responde")
            return False
            
    except Exception as e:
        print(f"   ERROR - Fallo en webapp: {e}")
        return False

if __name__ == "__main__":
    print("Probando que la aplicación web arranca correctamente...")
    print()
    
    success = test_webapp_startup()
    
    if success:
        print("\nWEBAP FUNCIONA PERFECTAMENTE!")
        print("Para usar:")
        print("  1. Ejecutar: python src/webapp.py")
        print("  2. Abrir navegador en: http://localhost:5000")
        print("  3. Usar la interfaz web intuitiva")
    else:
        print("\nHay problemas con la webapp")
    
    sys.exit(0 if success else 1)
