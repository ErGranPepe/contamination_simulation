# Simulación de Contaminación con SUMO

Este proyecto implementa una simulación de alta precisión para la dispersión de contaminantes generados por vehículos en entornos urbanos, utilizando SUMO (Simulation of Urban MObility) y un motor de cálculo híbrido Python/C para máximo rendimiento. La simulación permite analizar el impacto de diferentes parámetros ambientales y vehiculares sobre la calidad del aire, utilizando un modelo gaussiano de dispersión optimizado.

## Índice

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Uso](#uso)
- [Modelo de Dispersión](#modelo-de-dispersión)
- [Optimización de Rendimiento](#optimización-de-rendimiento)
- [Grabación de Simulaciones](#grabación-de-simulaciones)
- [Análisis de Datos](#análisis-de-datos)
- [Solución de Problemas](#solución-de-problemas)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Características

- **Interfaz Gráfica Intuitiva**: Configura parámetros de simulación a través de una interfaz gráfica amigable.
- **Motor de Cálculo Híbrido**: Aprovecha código C optimizado para cálculos intensivos, manteniendo la flexibilidad de Python.
- **Alto Rendimiento**: Optimizado para simulaciones con muchos vehículos y alta resolución espacial.
- **Modelo Gaussiano de Dispersión**: Implementa un modelo físico preciso para la dispersión de contaminantes.
- **Visualización en Tiempo Real**: Muestra la concentración de contaminantes con representación cromática dinámica.
- **Grabación de Simulaciones**: Captura videos de alta calidad con información superpuesta.
- **Generación de Mapas de Calor**: Crea visualizaciones para análisis posterior.
- **Múltiples Parámetros Ambientales**: Simula diferentes condiciones atmosféricas (estabilidad, viento, etc.).
- **Métricas de Rendimiento**: Muestra estadísticas sobre el rendimiento durante la ejecución.
- **Sistema Robusto**: Implementa mecanismos de respaldo para garantizar la ejecución incluso bajo condiciones adversas.

## Requisitos

### Software

- **Python 3.9+**
- **SUMO (Simulation of Urban MObility)**: Versión 1.12.0 o superior
- **Compilador C**: 
  - Windows: Visual Studio Build Tools con soporte para C/C++
  - Linux/Mac: GCC 8+ o Clang
- **Bibliotecas de Python**:
  - numpy
  - opencv-python
  - matplotlib
  - tqdm
  - tkinter (incluido con Python estándar)

### Hardware Recomendado

- **Procesador**: CPU multi-núcleo (4+ núcleos) para aprovechar las optimizaciones
- **RAM**: 8GB mínimo, 16GB recomendado para simulaciones de alta resolución
- **Gráficos**: Tarjeta gráfica compatible con OpenGL para visualización SUMO

## Instalación

### 1. Preparación del Entorno

```bash
# Clonar el repositorio
git clone https://github.com/usuario/contamination_simulation.git
cd contamination_simulation

# Crear entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Compilación del Módulo C

```bash
# Navegar al directorio de módulos
cd src/modules

# Compilar el módulo C optimizado
python cs_setup.py build_ext --inplace

# Volver al directorio raíz
cd ../..
```

### 3. Verificación de la Instalación

```bash
# Ejecutar la aplicación para verificar que todo funciona
python src/main.py
```

Si ves la interfaz gráfica sin errores, la instalación ha sido exitosa.

## Arquitectura del Sistema

El proyecto está estructurado en módulos bien definidos para facilitar el mantenimiento y la extensibilidad:

### Componentes Principales

- **Interfaz de Usuario** (`modules/config.py`): 
  - Proporciona controles intuitivos para todos los parámetros de simulación
  - Implementa validación de datos y feedback visual

- **Núcleo de Simulación** (`modules/CS_optimized.py`): 
  - Gestiona la lógica principal de simulación de contaminación
  - Coordina la comunicación entre Python y el módulo C
  - Implementa sistemas de respaldo y manejo de errores

- **Motor de Cálculo C** (`modules/cs_module.c`): 
  - Implementa los cálculos intensivos del modelo gaussiano de dispersión
  - Optimizado para rendimiento máximo
  - Proporciona dos interfaces: para vehículos individuales y procesamiento por lotes

- **Grabador de Simulación** (`modules/recorder_fixed.py`): 
  - Captura frames de la simulación
  - Superpone información relevante
  - Genera videos y mapas de calor

- **Controlador Principal** (`main.py`): 
  - Coordina todos los componentes
  - Gestiona el ciclo de vida de la simulación
  - Implementa métricas de rendimiento

### Diagrama de Flujo

1. **Configuración**: El usuario configura los parámetros a través de la interfaz gráfica
2. **Inicialización**: Se inicializa SUMO y los componentes de simulación
3. **Simulación**: Para cada paso de simulación:
   - SUMO actualiza las posiciones de los vehículos
   - El núcleo de simulación calcula la dispersión de contaminantes
   - Se actualiza la visualización periódicamente
   - Se capturan frames si la grabación está activada
4. **Finalización**: Se generan los resultados finales y se cierran todos los componentes

## Uso

### Ejecución Básica

```bash
python src/main.py
```

### Configuración de Parámetros

La interfaz gráfica permite configurar:

1. **Archivo de configuración SUMO**: Seleccione su archivo .sumocfg
2. **Parámetros Ambientales**:
   - **Velocidad del viento**: 0-30 m/s
   - **Dirección del viento**: 0-360 grados
   - **Clase de estabilidad atmosférica**: A (muy inestable) a F (muy estable)
   - **Temperatura**: -30 a 50 °C
   - **Humedad**: 0-100%
3. **Parámetros de Simulación**:
   - **Resolución de cuadrícula**: Determina la precisión espacial (50-500)
   - **Factor de emisión**: Multiplicador para las emisiones (0.1-2.0)
   - **Intervalo de actualización**: Pasos entre actualizaciones visuales (1-100)
   - **Número total de pasos**: Duración de la simulación (100-100000)
4. **Opciones de Grabación**:
   - Activar/desactivar grabación
   - Seleccionar archivo de salida

### Visualización

Durante la simulación, la contaminación se visualiza mediante polígonos coloreados:
- **Azul**: Baja concentración
- **Verde/Amarillo**: Concentración media
- **Rojo**: Alta concentración

La transparencia indica la intensidad de la contaminación.

### Resultados

Al finalizar la simulación con grabación activada, se generan:
- Video MP4 de la simulación completa
- Mapa de calor final de la contaminación
- Métricas de rendimiento en el archivo de log

## Modelo de Dispersión

El proyecto implementa un modelo gaussiano de dispersión atmosférica, que calcula la concentración de contaminantes en cada punto basándose en:

### Factores Considerados

1. **Emisión de Contaminantes**: Varía según la velocidad del vehículo
2. **Dispersión Atmosférica**: Determinada por la estabilidad atmosférica
3. **Viento**: Dirección y velocidad afectan el transporte de contaminantes
4. **Elevación de la Pluma**: Calculada según las características del vehículo
5. **Decaimiento**: Los contaminantes se disipan con el tiempo

### Ecuación Principal

La concentración de contaminantes en un punto (x,y) se calcula mediante:

```
C(x,y) = (Q / (2π × σy × σz × U)) × exp(-0.5 × (y/σy)²) × [exp(-0.5 × (z-h/σz)²) + exp(-0.5 × (z+h/σz)²)]
```

Donde:
- C: Concentración
- Q: Tasa de emisión
- σy, σz: Coeficientes de dispersión (dependen de la estabilidad atmosférica)
- U: Velocidad del viento
- h: Altura de la pluma
- x,y,z: Coordenadas relativas a la fuente de emisión

### Clases de Estabilidad

El modelo utiliza las clases de Pasquill-Gifford para la estabilidad atmosférica:
- **Clase A**: Extremadamente inestable
- **Clase B**: Moderadamente inestable
- **Clase C**: Ligeramente inestable
- **Clase D**: Neutra
- **Clase E**: Ligeramente estable
- **Clase F**: Moderadamente estable

Cada clase afecta los coeficientes de dispersión (σy, σz) y por tanto el comportamiento de la pluma de contaminación.

## Optimización de Rendimiento

El sistema utiliza varias estrategias para maximizar el rendimiento:

### 1. Implementación en C para Cálculos Intensivos

- **Cálculos Gaussianos**: Implementados en C para mayor velocidad
- **Acceso Optimizado a Arrays**: Utiliza strides para acceso eficiente a memoria
- **Precálculo**: Reutiliza valores calculados para mejorar rendimiento

### 2. Procesamiento por Lotes

- **Actualización Múltiple**: Procesa todos los vehículos en una sola llamada a C
- **Decaimiento Global**: Aplica decaimiento a toda la cuadrícula en una operación
- **Reducción de Sobrecarga**: Minimiza la comunicación Python-C

### 3. Optimizaciones Matemáticas

- **Ventana de Cálculo**: Solo calcula puntos en un radio relevante
- **Umbral de Distancia**: Omite cálculos para puntos muy lejanos
- **Factores Precalculados**: Optimiza cálculos repetitivos

### 4. Robustez

- **Fallback Automático**: Si el módulo C falla, utiliza implementación en Python
- **Manejo de Errores**: Recuperación de errores sin detener la simulación
- **Validación de Datos**: Previene errores de segmentación y accesos inválidos

## Grabación de Simulaciones

El sistema permite grabar simulaciones con características avanzadas:

### Características

- **Captura Automática**: Guarda frames en intervalos configurables
- **Información Superpuesta**: Muestra parámetros, tiempo y estadísticas
- **Formato MP4**: Genera videos compatibles con la mayoría de reproductores
- **Gestión de Recursos**: Limpia automáticamente archivos temporales
- **Manejo de Errores**: Recuperación ante problemas de captura o almacenamiento

### Visualizaciones Adicionales

- **Mapas de Calor**: Genera representaciones cromáticas de la concentración final
- **Estadísticas**: Registra métricas sobre la simulación

## Análisis de Datos

Los resultados de la simulación pueden analizarse de varias formas:

### Durante la Simulación

- **Visualización en Tiempo Real**: Observar cómo se dispersan los contaminantes
- **Estadísticas en Terminal**: Ver métricas de rendimiento en tiempo real

### Después de la Simulación

- **Análisis de Video**: Revisar la grabación para observar patrones
- **Mapas de Calor**: Analizar la distribución final de contaminantes
- **Logs**: Revisar el archivo de log para métricas detalladas

## Solución de Problemas

### Problemas Comunes

1. **Error al Compilar el Módulo C**:
   - Asegurarse de tener instalado un compilador C compatible
   - Verificar que numpy está instalado antes de compilar
   - En Windows, asegurarse de tener Visual Studio Build Tools

2. **SUMO no Inicia**:
   - Verificar que SUMO está correctamente instalado
   - Comprobar que la ruta en `main.py` apunta a la ubicación correcta de SUMO
   - Asegurarse de que el archivo .sumocfg es válido

3. **Errores en la Grabación**:
   - Verificar permisos de escritura en el directorio de salida
   - Comprobar que OpenCV está correctamente instalado
   - Asegurarse de que hay suficiente espacio en disco

4. **Bajo Rendimiento**:
   - Reducir la resolución de la cuadrícula
   - Aumentar el intervalo de actualización
   - Comprobar si el módulo C está siendo utilizado correctamente

### Archivos de Log

- **simulation.log**: Contiene información general y métricas de rendimiento
- **simulation_recorder.log**: Información específica sobre la grabación

## Contribuciones

Las contribuciones son bienvenidas y pueden hacerse de varias formas:

1. **Mejoras de Rendimiento**: Optimizaciones adicionales en el código C
2. **Nuevas Características**: Implementación de modelos de dispersión más avanzados
3. **Mejoras en la Interfaz**: Enriquecimiento de la experiencia de usuario
4. **Documentación**: Mejoras en la documentación y ejemplos
5. **Pruebas**: Desarrollo de casos de prueba y validación de resultados

Para contribuir:
1. Crear un fork del repositorio
2. Crear una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Confirmar los cambios (`git commit -am 'Añadir nueva característica'`)
4. Enviar la rama (`git push origin feature/nueva-caracteristica`)
5. Crear una Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Consulte el archivo LICENSE para más detalles.

## Contacto

Para preguntas, sugerencias o colaboraciones, puede contactar a:

Mario Díaz Gómez - m.diazg.2021@alumnos.urjc.es

---

Este proyecto es parte de una investigación sobre la dispersión de contaminantes en entornos urbanos y su impacto en la calidad del aire. Los resultados obtenidos son aproximaciones y deben validarse con mediciones reales para aplicaciones críticas.