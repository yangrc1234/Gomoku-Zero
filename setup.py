from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
  name = 'GameCython',
  ext_modules = cythonize(
    "gameCython.pyx",
    language = 'c++'
    ),
  include_dirs=[numpy.get_include()],
)