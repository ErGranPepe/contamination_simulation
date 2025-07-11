# Almacena configuraciones de simulación y estadísticas para la WebApp
# Autor: Mario Díaz Gómez (TFG Ingeniería Informática)
# Permite guardar y consultar configuraciones y resultados de simulación de forma persistente.

import os
import json
from datetime import datetime

CONFIGS_FILE = os.path.join(os.path.dirname(__file__), 'webapp_configs.json')

class WebAppMemory:
    def __init__(self):
        """
        Inicializa la clase WebAppMemory, cargando las configuraciones existentes
        desde el archivo de configuración.
        """
        self.configs = self._load_configs()

    def _load_configs(self):
        """
        Carga las configuraciones guardadas desde disco.

        Devuelve:
            list: Una lista de configuraciones guardadas. Cada entrada contiene
            una marca de tiempo, la configuración en sí y las estadísticas
            asociadas.
        """
        if os.path.exists(CONFIGS_FILE):
            with open(CONFIGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_config(self, config, stats=None):
        """
        Guarda una configuración y estadísticas asociadas.

        Args:
            config (dict): La configuración de simulación a guardar.
            stats (dict, opcional): Estadísticas de la simulación. Por defecto es None.
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'stats': stats or {}
        }
        self.configs.append(entry)
        with open(CONFIGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.configs, f, indent=2)

    def get_configs(self):
        """
        Devuelve todas las configuraciones y estadísticas guardadas.

        Returns:
            list: Una lista de todas las configuraciones y estadísticas guardadas.
        """
        return self.configs

memory = WebAppMemory()
