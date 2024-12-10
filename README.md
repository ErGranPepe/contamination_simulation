## Simulación de Contaminación con SUMO

Este proyecto implementa una simulación de la dispersión de contaminantes generados por vehículos en un entorno urbano utilizando SUMO (Simulation of Urban MObility) y Python. La simulación permite analizar el impacto de diferentes parámetros ambientales y vehiculares sobre la calidad del aire, utilizando un modelo de dispersión gaussiana.

## ****Índice****

-   Características
-   Requisitos
-   Instalación
-   Uso
-   Simulación del Viento
-   Ejecución de Pruebas
-   Preguntas Frecuentes (FAQ)
-   Contribuciones
-   Licencia
-   Contacto

**

## Características

**

-   Interfaz Gráfica Amigable: Configura los parámetros de la simulación de manera sencilla.
-   Modelo de Dispersión Gaussiana: Implementa un modelo físico para calcular la dispersión de contaminantes en función de factores como el viento y la estabilidad atmosférica.
-   Grabación de Video: Captura la simulación en tiempo real y guarda el resultado en formato MP4.
-   Estimación del Tiempo de Simulación: Proporciona una estimación del tiempo total que tomará ejecutar la simulación.

**

## Requisitos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

-   Python 3.x
-   SUMO: Debe estar instalado y configurado correctamente en tu sistema.
-   Bibliotecas de Python:
    
    -   numpy
    -   opencv-python
    -   tkinter (incluido con Python estándar)
    -   Pillow
    

Puedes instalar las bibliotecas necesarias ejecutando:pip install numpy opencv-python Pillow  
## Instalación

1.  **Clonar el Repositorio**:
    
    bash
    
    `git clone https://github.com/tu_usuario/simulation_project.git cd simulation_project` 
    
2.  **Configurar SUMO**: Asegúrese de que SUMO esté instalado y que el ejecutable sea accesible desde la línea de comandos.
3.  **Preparar el Archivo de Configuración SUMO** (`tu_archivo_configuracion.sumocfg`): Este archivo debe apuntar a su red y rutas específicas.

## Uso

1.  Ejecute el script principal:
    
    bash
    
    `python capas_plugin_v1.0.py` 
    
2.  Ajuste los parámetros en la interfaz gráfica:
    
    -   **Velocidad del viento (m/s)**: Define la velocidad del viento que influye en la dispersión.
    -   **Dirección del viento (grados)**: Establece la dirección del viento en grados (0 a 360).
    -   **Resolución de la cuadrícula**: Define el número de celdas en cada dimensión para el cálculo de contaminación.
    -   **Clase de estabilidad atmosférica**: Seleccione entre A (muy inestable) y F (muy estable), lo cual afecta los coeficientes de dispersión.
    -   **Factor de emisión**: Multiplicador que ajusta las emisiones generadas por los vehículos.
    -   **Intervalo de actualización (pasos)**: Número de pasos entre actualizaciones visuales.
    -   **Número total de pasos**: Define cuántos pasos se ejecutará la simulación.
    -   **Grabar simulación**: Opción para grabar la simulación a un archivo MP4.
    
3.  Haga clic en "Aplicar y Ejecutar" para iniciar la simulación.
4.  Si ha seleccionado grabar, se le pedirá que elija un archivo para guardar el video.

## Simulación del Viento

La simulación del viento se basa en un modelo físico que considera varios factores clave:

-   **Velocidad del Viento**: Este parámetro afecta directamente a la dispersión de los contaminantes. Se mide en metros por segundo (m/s).
-   **Dirección del Viento**: Representada en grados, donde 0° indica viento del norte y 90° del este, entre otros.
-   **Estabilidad Atmosférica**: Se clasifica desde A (muy inestable) hasta F (muy estable). Esta clasificación influye en los coeficientes de dispersión utilizados en el modelo gaussiano.

El modelo calcula cómo los contaminantes se dispersan a partir de las emisiones generadas por los vehículos, considerando estos factores para predecir las concentraciones en diferentes puntos dentro del área simulada.

## Ejecución de Pruebas

Para garantizar que el código funcione correctamente, se pueden implementar pruebas unitarias utilizando `unittest` o `pytest`. A continuación se presenta un ejemplo básico utilizando `unittest`:

1.  Cree un archivo llamado `test_simulation.py`.
2.  Escriba sus pruebas como se muestra a continuación:

python

`import unittest from tu_modulo import ContaminationSimulation # Asegúrese de importar su clase correctamente   class  TestContaminationSimulation(unittest.TestCase):   def  test_calculate_emission_rate(self): sim = ContaminationSimulation({'emission_factor':  1.0}) self.assertAlmostEqual(sim.calculate_emission_rate(20),  0.1)   if __name__ ==  '__main__':   unittest.main()` 

3.  Ejecute las pruebas desde la línea de comandos:
    
    bash
    
    `python test_simulation.py` 
    

Para usar `pytest`, primero instale pytest:

bash

`pip install pytest` 

Luego ejecute sus pruebas con:

bash

`pytest` 

## Preguntas Frecuentes (FAQ)

## ¿Qué es SUMO?

SUMO es un simulador de tráfico que permite modelar el comportamiento del tráfico vehicular en entornos urbanos. Es ampliamente utilizado para investigaciones en movilidad y planificación urbana.

## ¿Cómo ajusto los parámetros?

Los parámetros pueden ajustarse directamente desde la interfaz gráfica. Cada parámetro incluye una descripción que facilita su comprensión.

## ¿Puedo usar mi propia red?

Sí, es posible utilizar su propia red configurando adecuadamente su archivo `tu_archivo_configuracion.sumocfg`. Asegúrese de que todas las rutas y archivos necesarios estén disponibles.

## ¿Cuánto tiempo tardará la simulación?

La estimación del tiempo se calcula automáticamente según los parámetros ingresados. Se mostrará un aviso antes de iniciar la simulación.

## ¿Qué hacer si encuentro errores?

Si encuentra errores, revise los mensajes en la consola para obtener detalles sobre lo que salió mal. Asegúrese también de que todas las dependencias estén correctamente instaladas.

## Contribuciones

Las contribuciones son bienvenidas. Si desea mejorar o añadir características al proyecto, siéntase libre de abrir un issue o enviar un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulte el archivo LICENSE para más detalles.

## Contacto

Para preguntas o comentarios, puede contactar a Mario Díaz Gómez en m.diazg.2021@alumnos.urjc.es .  ¡Gracias por utilizar nuestro simulador! Esperamos que esta herramienta sea útil para sus estudios sobre contaminación urbana y análisis ambiental.
