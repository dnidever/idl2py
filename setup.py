#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages

setup(name='idl2py',
      version='1.0.5',
      description='Simple IDL to Python converter',
      author='David Nidever',
      author_email='dnidever@montana.edu',
      url='https://github.com/dnidever/idl2py',
      packages=find_packages(exclude=["tests"]),
      #package_dir={'idl2py':'python/idl2py'},
      scripts=['bin/idl2py'],
      requires=['numpy'],
      include_package_data=True,
)
