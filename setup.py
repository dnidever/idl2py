#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages

setup(name='idl2pyr',
      version='1.0.0',
      description='Simple IDL to Python converter',
      author='David Nidever',
      author_email='dnidever@montana.edu',
      url='https://github.com/dnidever/idl2py',
      packages=find_packages(exclude=["tests"]),
      scripts=['bin/idl2py'],
      include_package_data=True,
)
