"""
Script de configuración para compilar el módulo C optimizado para cálculos de contaminación.

Este script detecta automáticamente el sistema operativo y configura las opciones de compilación
adecuadas para Windows (MSVC) o Linux/Mac (GCC/Clang).

Uso:
    python cs_setup.py build_ext --inplace
"""

from setuptools import setup, Extension
import numpy
import sys
import os
import platform

# Detectar sistema operativo y configurar opciones de compilación adecuadas
if sys.platform == 'win32':
    # Opciones para Windows con MSVC
    extra_compile_args = ['/O2']  # Optimización nivel 2
    extra_link_args = []
    print("Configurando para Windows con MSVC")
else:
    # Opciones para Linux/MacOS con GCC/Clang
    extra_compile_args = ['-O3', '-ffast-math', '-fopenmp']
    extra_link_args = ['-fopenmp']
    print("Configurando para Linux/MacOS con GCC/Clang")

# Definir el módulo de extensión
module = Extension('cs_module',
                  sources=['src/modules/cs_module.c'],
                  include_dirs=[numpy.get_include()],
                  extra_compile_args=extra_compile_args,
                  extra_link_args=extra_link_args)


# Configuración del paquete
setup(
    name='cs_module',
    version='1.0',
    description='Módulo C optimizado para cálculos de dispersión de contaminación',
    author='Mario Díaz Gómez',
    ext_modules=[module]
)

print(f"Configuración completada para {platform.system()} ({platform.architecture()[0]})")
print("Ejecute 'python cs_setup.py build_ext --inplace' para compilar el módulo")