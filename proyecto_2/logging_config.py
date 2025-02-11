import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logging(log_file='app.log', console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Configura el sistema de logging con salida a consola y archivo.

    Args:
    log_file (str): Nombre del archivo de log. Por defecto es 'app.log'.
    console_level (int): Nivel de logging para la consola. Por defecto es logging.INFO.
    file_level (int): Nivel de logging para el archivo. Por defecto es logging.DEBUG.

    Returns:
    logging.Logger: El logger configurado.
    """
    try:
        # Crear el logger principal
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Establecer el nivel más bajo para capturar todos los mensajes

        # Formato del log
        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                       datefmt='%Y-%m-%d %H:%M:%S')

        # Configurar el manejador de consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

        # Configurar el manejador de archivo
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

        return logger

    except Exception as e:
        print(f"Error al configurar el logging: {str(e)}")
        raise

if __name__ == "__main__":
    # Ejemplo de uso
    logger = setup_logging()
    logger.debug("Este es un mensaje de debug")
    logger.info("Este es un mensaje de info")
    logger.warning("Este es un mensaje de advertencia")
    logger.error("Este es un mensaje de error")
    logger.critical("Este es un mensaje crítico")
