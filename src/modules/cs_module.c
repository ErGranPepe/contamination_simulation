// cs_module.c - Módulo C optimizado para cálculos de dispersión de contaminación
// Este módulo proporciona funciones de alto rendimiento para calcular la dispersión de contaminantes
// utilizando el modelo gaussiano de dispersión.

#define PY_SSIZE_T_CLEAN
#ifndef M_PI
    #define M_PI 3.14159265358979323846  // Definir pi si no está disponible
#endif
#include <Python.h>
#include <math.h>
#include <numpy/arrayobject.h>
#include <string.h>

/**
 * Calcula los coeficientes de dispersión basados en la distancia y clase de estabilidad.
 * 
 * @param stability_class Clase de estabilidad atmosférica (A-F)
 * @param distance Distancia desde la fuente en metros
 * @param sigma_y Puntero donde se guardará el coeficiente de dispersión horizontal
 * @param sigma_z Puntero donde se guardará el coeficiente de dispersión vertical
 */
static void calculate_dispersion_coefficients(const char* stability_class, double distance, double* sigma_y, double* sigma_z) {
    double a, b;
    
    // Parámetros según la clase de estabilidad
    if (strcmp(stability_class, "A") == 0) {
        a = 0.22; b = 0.20;
    } else if (strcmp(stability_class, "B") == 0) {
        a = 0.16; b = 0.12;
    } else if (strcmp(stability_class, "C") == 0) {
        a = 0.11; b = 0.08;
    } else if (strcmp(stability_class, "D") == 0) {
        a = 0.08; b = 0.06;
    } else if (strcmp(stability_class, "E") == 0) {
        a = 0.06; b = 0.03;
    } else if (strcmp(stability_class, "F") == 0) {
        a = 0.04; b = 0.016;
    } else {
        // Valor por defecto (clase D - neutral)
        a = 0.10; b = 0.05;
    }
    
    // Cálculo de los coeficientes según fórmulas estándar
    *sigma_y = a * distance * pow(1 + 0.0001 * distance, -0.5);
    *sigma_z = b * distance * pow(1 + 0.0001 * distance, -0.5);
}

/**
 * Calcula la tasa de emisión de contaminantes de un vehículo basada en su velocidad.
 * 
 * @param vehicle_speed Velocidad del vehículo en m/s
 * @param emission_factor Factor de emisión global configurado por el usuario
 * @return Tasa de emisión calculada
 */
static double calculate_emission_rate(double vehicle_speed, double emission_factor) {
    double base_emission = 0.1;  // Emisión base para cualquier vehículo
    
    // Aumentar emisión para velocidades altas (>20 m/s)
    double speed_factor = (vehicle_speed > 20) ? 
                         (1 + 0.05 * (vehicle_speed - 20)) : 1.0;
    
    // Aplicar factor de emisión global (configurable por el usuario)
    return base_emission * speed_factor * emission_factor;
}

/**
 * Calcula la altura de la pluma de contaminación basada en la velocidad del vehículo.
 * 
 * @param vehicle_speed Velocidad del vehículo en m/s
 * @return Altura de la pluma en metros (mínimo 2 metros)
 */
static double calculate_plume_rise(double vehicle_speed) {
    // La altura aumenta con la velocidad pero tiene un mínimo de 2 metros
    return (vehicle_speed * 0.15 + 0.5 > 2.0) ? 
           (vehicle_speed * 0.15 + 0.5) : 2.0;
}

/**
 * Esta es la función principal que actualiza la cuadrícula de contaminación para un único vehículo.
 * Es llamada desde Python para cada vehículo en la simulación.
 * 
 * @param self Puntero al objeto Python (requerido por la API)
 * @param args Argumentos de Python empaquetados en una tupla
 * @return Objeto Python (None)
 */
static PyObject* update_pollution(PyObject *self, PyObject *args) {
    PyArrayObject *grid;
    int i_min, i_max, j_min, j_max, grid_resolution;
    double x, y, emission_rate, plume_height, wind_speed, wind_direction;
    double x_min, x_max, y_min, y_max;

    // Extraer argumentos de Python
    if (!PyArg_ParseTuple(args, "Oiiiiddddddddddi", 
            &grid,                         // Cuadrícula de contaminación
            &i_min, &i_max, &j_min, &j_max, // Ventana de cálculo
            &x, &y,                         // Posición del vehículo
            &emission_rate,                 // Tasa de emisión
            &plume_height,                  // Altura de la pluma
            &wind_speed,                    // Velocidad del viento
            &wind_direction,                // Dirección del viento
            &x_min, &x_max, &y_min, &y_max, // Límites del área
            &grid_resolution)) {            // Resolución de la cuadrícula
        return NULL;
    }

    // Validación de entradas para evitar errores de segmentación
    if (!PyArray_Check(grid) || PyArray_TYPE(grid) != NPY_DOUBLE || PyArray_NDIM(grid) != 2) {
        PyErr_SetString(PyExc_TypeError, "El grid debe ser un array NumPy bidimensional de tipo double");
        return NULL;
    }

    // Verificar límites de índices
    npy_intp* dims = PyArray_DIMS(grid);
    if (i_min < 0 || i_max > dims[0] || j_min < 0 || j_max > dims[1]) {
        PyErr_SetString(PyExc_IndexError, "Índices fuera de rango");
        return NULL;
    }

    // Acceso optimizado a los datos
    double *data = (double*) PyArray_DATA(grid);
    npy_intp strides[2];
    strides[0] = PyArray_STRIDE(grid, 0) / sizeof(double);
    strides[1] = PyArray_STRIDE(grid, 1) / sizeof(double);

    // Calcular tamaño de celda
    double cell_width = (x_max - x_min) / grid_resolution;
    double cell_height = (y_max - y_min) / grid_resolution;

    // Precalcular constantes comunes para optimización
    double two_pi = 2.0 * M_PI;
    double emission_factor = emission_rate / (two_pi * wind_speed);

    // Utilizar bucles optimizados con acceso eficiente a memoria
    for (int i = i_min; i < i_max; i++) {
        for (int j = j_min; j < j_max; j++) {
            // Coordenadas del centro de la celda (i,j)
            double receptor_x = x_min + (j + 0.5) * cell_width;
            double receptor_y = y_min + (i + 0.5) * cell_height;
            
            // Distancia desde el vehículo al receptor
            double dx = receptor_x - x;
            double dy = receptor_y - y;
            double distance_squared = dx * dx + dy * dy;
            
            // Optimización: evitar cálculos innecesarios para puntos muy cercanos
            if (distance_squared < 1.0) continue;
            
            double distance = sqrt(distance_squared);
            
            // Evitar cálculos para puntos muy lejanos (débil contribución)
            if (distance > 300.0) continue;

            // Ángulo entre la dirección del viento y la dirección al receptor
            double wind_dir_to_rec = atan2(dy, dx);
            double angle_diff = fabs(wind_dir_to_rec - wind_direction);
            if (angle_diff > M_PI)
                angle_diff = two_pi - angle_diff;

            // Calcular coeficientes de dispersión basados en la distancia
            double sigma_y, sigma_z;
            // Cálculo directo para evitar llamadas a función (optimización)
            double distance_factor = pow(1 + 0.0001 * distance, -0.5);
            sigma_y = 0.1 * distance * distance_factor;
            sigma_z = 0.05 * distance * distance_factor;

            // Calcular concentración usando la ecuación gaussiana de dispersión
            double lateral_dispersion = exp(-0.5 * pow(angle_diff / sigma_y, 2));
            double vertical_dispersion = exp(-0.5 * pow(plume_height / sigma_z, 2)) * 2.0; // Simplificado

            double concentration = emission_factor * lateral_dispersion * vertical_dispersion / (sigma_y * sigma_z);
            
            // Añadir la concentración a la cuadrícula (acceso optimizado)
            data[i * strides[0] + j * strides[1]] += concentration;
        }
    }

    Py_RETURN_NONE;
}

/**
 * Actualiza la cuadrícula de contaminación para múltiples vehículos en una sola llamada.
 * Esta es una versión optimizada que procesa todos los vehículos en C.
 * 
 * @param self Puntero al objeto Python
 * @param args Argumentos de Python
 * @return Objeto Python (None)
 */
static PyObject* update_pollution_multiple(PyObject *self, PyObject *args) {
    PyArrayObject *grid;
    PyObject *vehicle_list;  // Lista de tuplas (x, y, speed)
    double wind_speed, wind_direction, emission_factor;
    const char *stability_class;
    double x_min, x_max, y_min, y_max;
    int grid_resolution;

    // CORRECCIÓN: Ajustar para aceptar 11 argumentos (formato "OOdddsdddi")
    if (!PyArg_ParseTuple(args, "OOdddsdddi", 
            &grid,                // Cuadrícula de contaminación
            &vehicle_list,        // Lista de vehículos
            &wind_speed,          // Velocidad del viento
            &wind_direction,      // Dirección del viento
            &emission_factor,     // Factor de emisión
            &stability_class,     // Clase de estabilidad
            &x_min, &x_max, &y_min, &y_max, // Límites del área
            &grid_resolution)) {  // Resolución de la cuadrícula
        return NULL;
    }

    // Validar el grid
    if (!PyArray_Check(grid) || PyArray_TYPE(grid) != NPY_DOUBLE || PyArray_NDIM(grid) != 2) {
        PyErr_SetString(PyExc_TypeError, "El grid debe ser un array NumPy bidimensional de tipo double");
        return NULL;
    }

    // Validar la lista de vehículos
    if (!PyList_Check(vehicle_list)) {
        PyErr_SetString(PyExc_TypeError, "Se esperaba una lista de vehículos");
        return NULL;
    }

    // Aplicar decaimiento global (factor 0.99)
    double *data = (double*) PyArray_DATA(grid);
    npy_intp size = PyArray_SIZE(grid);
    for (npy_intp i = 0; i < size; i++) {
        data[i] *= 0.99;
    }

    // Acceso optimizado a los datos
    npy_intp strides[2];
    strides[0] = PyArray_STRIDE(grid, 0) / sizeof(double);
    strides[1] = PyArray_STRIDE(grid, 1) / sizeof(double);
    npy_intp* dims = PyArray_DIMS(grid);

    double cell_width = (x_max - x_min) / grid_resolution;
    double cell_height = (y_max - y_min) / grid_resolution;

    // Recorrer todos los vehículos
    Py_ssize_t num_vehicles = PyList_Size(vehicle_list);
    for (Py_ssize_t v = 0; v < num_vehicles; v++) {
        PyObject *vehicle_tuple = PyList_GetItem(vehicle_list, v);
        if (!PyTuple_Check(vehicle_tuple) || PyTuple_Size(vehicle_tuple) != 3) {
            PyErr_SetString(PyExc_ValueError, "Cada vehículo debe ser una tupla (x, y, speed)");
            return NULL;
        }

        double x = PyFloat_AsDouble(PyTuple_GetItem(vehicle_tuple, 0)); // trabajamos con los floats   
        double y = PyFloat_AsDouble(PyTuple_GetItem(vehicle_tuple, 1));
        double vehicle_speed = PyFloat_AsDouble(PyTuple_GetItem(vehicle_tuple, 2));

        // Calcular parámetros para este vehículo
        double emission_rate = calculate_emission_rate(vehicle_speed, emission_factor); // trabajamos con los floats, evitar tiempo en la conversion
        double plume_height = calculate_plume_rise(vehicle_speed);

        // Calcular índices de la ventana de cálculo (convertidos a enteros de forma segura)
        int i_min = (int)fmax(0.0, (y - y_min - 100.0) / (y_max - y_min) * (double)grid_resolution);
        int i_max = (int)fmin((double)dims[0], (y - y_min + 100.0) / (y_max - y_min) * (double)grid_resolution);
        int j_min = (int)fmax(0.0, (x - x_min - 100.0) / (x_max - x_min) * (double)grid_resolution);
        int j_max = (int)fmin((double)dims[1], (x - x_min + 100.0) / (x_max - x_min) * (double)grid_resolution);

        // Precalcular constantes comunes
        double two_pi = 2.0 * M_PI;
        double emission_factor_value = emission_rate / (two_pi * wind_speed);

        // Calcular la dispersión para este vehículo
        for (int i = i_min; i < i_max; i++) {
            for (int j = j_min; j < j_max; j++) {
                double receptor_x = x_min + (j + 0.5) * cell_width;
                double receptor_y = y_min + (i + 0.5) * cell_height;
                double dx = receptor_x - x;
                double dy = receptor_y - y;
                double distance_squared = dx * dx + dy * dy;
                
                if (distance_squared < 1.0) continue;
                
                double distance = sqrt(distance_squared);
                if (distance > 300.0) continue;

                double wind_dir_to_rec = atan2(dy, dx);
                double angle_diff = fabs(wind_dir_to_rec - wind_direction);
                if (angle_diff > M_PI)
                    angle_diff = two_pi - angle_diff;

                // Calcular coeficientes de dispersión
                double sigma_y, sigma_z;
                calculate_dispersion_coefficients(stability_class, distance, &sigma_y, &sigma_z);

                // Calcular concentración
                double lateral_dispersion = exp(-0.5 * pow(angle_diff / sigma_y, 2));
                double vertical_dispersion = exp(-0.5 * pow(plume_height / sigma_z, 2)) * 2.0;

                double concentration = emission_factor_value * lateral_dispersion * vertical_dispersion / (sigma_y * sigma_z);
                
                data[i * strides[0] + j * strides[1]] += concentration;
            }
        }
    }

    Py_RETURN_NONE;
}

// Métodos del módulo
static PyMethodDef CSMethods[] = {
    {"update_pollution", update_pollution, METH_VARARGS, 
     "Actualiza la cuadrícula de contaminación para un único vehículo."},
    {"update_pollution_multiple", update_pollution_multiple, METH_VARARGS, 
     "Actualiza la cuadrícula de contaminación para múltiples vehículos de manera optimizada."},
    {NULL, NULL, 0, NULL}
};

// Definición del módulo
static struct PyModuleDef csmodule = {
    PyModuleDef_HEAD_INIT,
    "cs_module",
    "Módulo C optimizado para cálculos de dispersión de contaminación",
    -1,
    CSMethods
};

// Función de inicialización del módulo
PyMODINIT_FUNC PyInit_cs_module(void) {
    import_array();  // Inicializa la API de NumPy
    return PyModule_Create(&csmodule);
}