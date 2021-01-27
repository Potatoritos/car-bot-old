from distutils.core import setup, Extension

module = Extension('string_stuff', sources=['carbot/string_stuff.cpp'])

setup(name='string_stuff', ext_modules = [module])
