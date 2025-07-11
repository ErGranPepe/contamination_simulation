"""
Módulo de validación de parámetros para la simulación de contaminación.
"""

def validate_simulation_config(config: dict) -> list:
    """
    Valida los parámetros de configuración de la simulación.
    Args:
        config: Diccionario de configuración
    Returns:
        Lista de errores encontrados (vacía si todo es correcto)
    """
    errors = []
    params = config.get('parameters', {})
    if not config.get('sumo_config'):
        errors.append("Debe seleccionar un archivo de configuración SUMO.")
    if params.get('wind_speed', 0) < 0 or params.get('wind_speed', 0) > 30:
        errors.append("La velocidad del viento debe estar entre 0 y 30 m/s.")
    if params.get('grid_resolution', 0) < 10 or params.get('grid_resolution', 0) > 1000:
        errors.append("La resolución de la cuadrícula debe estar entre 10 y 1000.")
    if params.get('update_interval', 0) < 1:
        errors.append("El intervalo de actualización debe ser mayor que 0.")
    if params.get('total_steps', 0) < 1:
        errors.append("El número total de pasos debe ser mayor que 0.")
    # Puedes añadir más validaciones según tus necesidades
    return errors
