import json
import os

def save_config(config: dict, filepath: str) -> None:
    """
    Guarda una configuración en un archivo JSON.

    Args:
        config (dict): Diccionario con la configuración a guardar.
        filepath (str): Ruta del archivo donde se guardará la configuración.

    Raises:
        ValueError: Si el parámetro `config` no es un diccionario.
        IOError: Si ocurre un error al escribir el archivo.
    """
    if not isinstance(config, dict):
        raise ValueError("El parámetro 'config' debe ser un diccionario.")

    try:
        with open(filepath, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Configuración guardada exitosamente en {filepath}")
    except IOError as e:
        print(f"Error al guardar la configuración en {filepath}: {e}")
        raise

def load_config(filepath: str) -> dict:
    """
    Carga una configuración desde un archivo JSON.

    Args:
        filepath (str): Ruta del archivo JSON a cargar.

    Returns:
        dict: Diccionario con los datos de la configuración cargada.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el contenido del archivo no es un JSON válido.
        IOError: Si ocurre un error al leer el archivo.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo {filepath} no existe.")

    try:
        with open(filepath, 'r') as file:
            config = json.load(file)
            if not isinstance(config, dict):
                raise ValueError("El contenido del archivo no es un diccionario válido.")
            return config
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON en {filepath}: {e}")
        raise ValueError(f"El archivo {filepath} no contiene un JSON válido.") from e
    except IOError as e:
        print(f"Error al leer el archivo {filepath}: {e}")
        raise

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración de prueba
    config_data = {
        "simulation_speed": 1.5,
        "output_directory": "results/",
        "enable_logging": True,
        "max_iterations": 1000
    }

    # Guardar configuración
    try:
        save_config(config_data, "config.json")
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")

    # Cargar configuración
    try:
        loaded_config = load_config("config.json")
        print("Configuración cargada:", loaded_config)
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
