// spam_module.c
#define PY_SSIZE_T_CLEAN
#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif
#include <Python.h>
#include <math.h>
#include <numpy/arrayobject.h>

static PyObject* update_pollution(PyObject *self, PyObject *args) {
    PyArrayObject *grid;
    int i_min, i_max, j_min, j_max, grid_resolution;
    double x, y, emission_rate, plume_height, wind_speed, wind_direction;
    double x_min, x_max, y_min, y_max;

    /*
       Se espera recibir 16 argumentos:
         1. grid (objeto NumPy)
         2. i_min (int)
         3. i_max (int)
         4. j_min (int)
         5. j_max (int)
         6. x (double)
         7. y (double)
         8. emission_rate (double)
         9. plume_height (double)
        10. wind_speed (double)
        11. wind_direction (double)
        12. x_min (double)
        13. x_max (double)
        14. y_min (double)
        15. y_max (double)
        16. grid_resolution (int)
    */
    if (!PyArg_ParseTuple(args, "Oiiiiddddddddddi", 
            &grid, 
            &i_min, &i_max, &j_min, &j_max,
            &x, &y,
            &emission_rate,
            &plume_height,
            &wind_speed,
            &wind_direction,
            &x_min, &x_max, &y_min, &y_max,
            &grid_resolution)) {
        return NULL;
    }

    // Se asume que 'grid' es un arreglo contiguo de double
    double *data = (double*) PyArray_DATA(grid);
    double cell_width = (x_max - x_min) / grid_resolution;
    double cell_height = (y_max - y_min) / grid_resolution;

    // Coeficientes fijos (puedes ajustarlos si lo deseas)
    double a = 0.10, b = 0.05;

    for (int i = i_min; i < i_max; i++) {
        for (int j = j_min; j < j_max; j++) {
            double receptor_x = x_min + (j + 0.5) * cell_width;
            double receptor_y = y_min + (i + 0.5) * cell_height;
            double dx = receptor_x - x;
            double dy = receptor_y - y;
            double distance = sqrt(dx * dx + dy * dy);
            if (distance < 1.0)
                continue;

            double wind_dir_to_rec = atan2(dy, dx);
            double angle_diff = fabs(wind_dir_to_rec - wind_direction);
            if (angle_diff > M_PI)
                angle_diff = 2 * M_PI - angle_diff;

            double sigma_y = a * distance * pow(1 + 0.0001 * distance, -0.5);
            double sigma_z = b * distance * pow(1 + 0.0001 * distance, -0.5);

            double concentration = (emission_rate / (2 * M_PI * wind_speed * sigma_y * sigma_z)) *
                                     exp(-0.5 * pow(angle_diff / sigma_y, 2)) *
                                     (exp(-0.5 * pow(plume_height / sigma_z, 2)) +
                                      exp(-0.5 * pow(plume_height / sigma_z, 2)));

            data[i * grid_resolution + j] += concentration;
        }
    }

    Py_RETURN_NONE;
}

static PyMethodDef SpamMethods[] = {
    {"update_pollution", update_pollution, METH_VARARGS, "Actualiza la cuadrícula de contaminación."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",
    NULL,
    -1,
    SpamMethods
};

PyMODINIT_FUNC PyInit_spam(void) {
    import_array();  // Inicializa la API de NumPy
    return PyModule_Create(&spammodule);
}
