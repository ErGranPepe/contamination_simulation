
# Simulación de Contaminación con SUMO

Este proyecto implementa una simulación de la dispersión de contaminantes generados por vehículos en un entorno urbano utilizando **SUMO** (Simulation of Urban MObility) y Python. La simulación permite analizar el impacto de diferentes parámetros ambientales y vehiculares sobre la calidad del aire, utilizando un modelo de dispersión gaussiana.

## Índice

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Simulación del Viento](#simulación-del-viento)
- [Ejecución de Pruebas](#ejecución-de-pruebas)
- [Preguntas Frecuentes (FAQ)](#preguntas-frecuentes-faq)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)
- [Contacto](#contacto)

---

## Características

- **Interfaz Gráfica Amigable**: Configura los parámetros de la simulación de manera sencilla.
- **Modelo de Dispersión Gaussiana**: Implementa un modelo físico para calcular la dispersión de contaminantes en función de factores como el viento y la estabilidad atmosférica.
- **Grabación de Video**: Captura la simulación en tiempo real y guarda el resultado en formato MP4.
- **Estimación del Tiempo de Simulación**: Proporciona una estimación del tiempo total que tomará ejecutar la simulación.

---

## Requisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- **Python 3.x**
- **SUMO**: Debe estar instalado y configurado correctamente en tu sistema.
- **Bibliotecas de Python**:
  - `numpy`
  - `opencv-python`
  - `tkinter` (incluido con Python estándar)
  - `Pillow`

Puedes instalar las bibliotecas necesarias ejecutando:

```bash
pip install numpy opencv-python Pillow

Instalación
Clona este repositorio o descarga el código fuente:
bash
git clone https://github.com/tu_usuario/simulation_project.git
cd simulation_project

Configura SUMO: Asegúrate de que SUMO esté instalado y que el ejecutable sea accesible desde la línea de comandos.
Prepara tu archivo de configuración SUMO (tu_archivo_configuracion.sumocfg) para apuntar a tu red y rutas.
Uso
Ejecuta el script principal:
bash
python capas_plugin_v1.0.py

Ajusta los parámetros en la interfaz gráfica:
Velocidad del viento (m/s): Define la velocidad del viento.
Dirección del viento (grados): Establece la dirección del viento en grados (0-360).
Resolución de la cuadrícula: Define el número de celdas en cada dimensión.
Clase de estabilidad atmosférica: Selecciona entre A (muy inestable) y F (muy estable).
Factor de emisión: Multiplicador para las emisiones generadas por los vehículos.
Intervalo de actualización (pasos): Número de pasos entre actualizaciones visuales.
Número total de pasos: Define cuántos pasos se ejecutará la simulación.
Grabar simulación: Selecciona si deseas grabar la simulación a un archivo MP4.
Haz clic en "Aplicar y Ejecutar" para iniciar la simulación.
Si seleccionaste grabar, se te pedirá que elijas un archivo para guardar el video.
Simulación del Viento
La simulación del viento se basa en un modelo físico que considera varios factores clave:
Velocidad del Viento: Este parámetro afecta directamente a la dispersión de los contaminantes. Se mide en metros por segundo (m/s).
Dirección del Viento: Representada en grados, donde 0° indica viento del norte y 90° del este, entre otros.
Estabilidad Atmosférica: Se clasifica desde A (muy inestable) hasta F (muy estable). Esta clasificación influye en los coeficientes de dispersión utilizados en el modelo gaussiano.
El modelo calcula cómo los contaminantes se dispersan a partir de las emisiones generadas por los vehículos, considerando estos factores para predecir las concentraciones en diferentes puntos dentro del área simulada.
Ejecución de Pruebas
Para garantizar que el código funcione correctamente, puedes implementar pruebas unitarias utilizando unittest o pytest. Aquí hay un ejemplo básico utilizando unittest:
Crea un archivo llamado test_simulation.py.
Escribe tus pruebas como se muestra a continuación:
python
import unittest
from tu_modulo import ContaminationSimulation  # Asegúrate de importar tu clase correctamente

class TestContaminationSimulation(unittest.TestCase):
    def test_calculate_emission_rate(self):
        sim = ContaminationSimulation({'emission_factor': 1.0})
        self.assertAlmostEqual(sim.calculate_emission_rate(20), 0.1)

if __name__ == '__main__':
    unittest.main()

Ejecuta las pruebas desde la línea de comandos:
bash
python test_simulation.py

Para usar pytest, primero instala pytest:
bash
pip install pytest

Luego ejecuta tus pruebas con:
bash
pytest

Preguntas Frecuentes (FAQ)
¿Qué es SUMO?
SUMO es un simulador de tráfico que permite modelar el comportamiento del tráfico vehicular en entornos urbanos. Es ampliamente utilizado para investigaciones en movilidad y planificación urbana.
¿Cómo ajusto los parámetros?
Puedes ajustar los parámetros directamente desde la interfaz gráfica. Cada parámetro tiene una descripción que te ayudará a entender su función.
¿Puedo usar mi propia red?
Sí, puedes utilizar tu propia red configurando adecuadamente tu archivo tu_archivo_configuracion.sumocfg. Asegúrate de que todas las rutas y archivos necesarios estén disponibles.
¿Cuánto tiempo tardará la simulación?
La estimación del tiempo se calcula automáticamente según los parámetros ingresados. Se te mostrará un aviso antes de iniciar la simulación.
¿Qué hacer si encuentro errores?
Si encuentras errores, revisa los mensajes en la consola para obtener detalles sobre lo que salió mal. Asegúrate también de que todas las dependencias estén correctamente instaladas.
Contribuciones
Las contribuciones son bienvenidas. Si deseas mejorar o añadir características al proyecto, siéntete libre de abrir un issue o enviar un pull request.
Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
Contacto
Para preguntas o comentarios, puedes contactar a [tu nombre] en [tu correo electrónico]. ¡Gracias por utilizar nuestro simulador! Esperamos que esta herramienta sea útil para sus estudios sobre contaminación urbana y análisis ambiental.
text
