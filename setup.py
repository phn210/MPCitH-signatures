import numpy as np
from setuptools import setup, Extension
from Cython.Build import cythonize
import Cython.Compiler.Options
import glob
import os

# os.environ["CC"] = "clang++"
Cython.Compiler.Options.annotate = True
def cythonize_extensions():
    pyx_files = glob.glob("*/**/*.pyx", recursive=True)
    extensions = [
        Extension(
            pyx_file.replace("/", ".").replace(".pyx", "_c"),
            [pyx_file],
            # extra_compile_args=['-fopenmp'],
            # extra_link_args=['-fopenmp'],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
        ) for pyx_file in pyx_files
    ]
    setup(
        ext_modules=cythonize(
            extensions,
            annotate=True,              # Enable annotation
            compiler_directives={
                'boundscheck': False,   # Disable bounds checking
                'wraparound': False,    # Disable negative indexing
                'nonecheck': False,     # Disable none checking
            }
        ),
        include_dirs=[np.get_include()],
    )

# cythonize_extensions()
