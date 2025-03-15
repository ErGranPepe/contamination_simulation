from setuptools import setup, Extension
import numpy

module = Extension('spam',
                   sources=['spam_module.c'],
                   include_dirs=[numpy.get_include()])

setup(
    name='spam',
    version='1.0',
    description='Módulo en C para cálculos de dispersión de contaminación',
    ext_modules=[module]
)
