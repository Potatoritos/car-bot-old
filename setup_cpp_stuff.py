from distutils.core import setup, Extension

module = Extension('string_stuff', sources=['carbot/string_stuff.cpp'])
setup(name='string_stuff', ext_modules = [module])

module = Extension('simulations', sources=['carbot/simulations.cpp'])
setup(name='simulations', ext_modules = [module])

