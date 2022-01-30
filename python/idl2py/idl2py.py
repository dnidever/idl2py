#!/usr/bin/env python

"""IDL2PY.PY - Simple IDL to Python converter

"""

import os
import re

def datadir():
    """ Return the repo data directory."""
    fil = os.path.abspath(__file__)
    codedir = os.path.dirname(fil)
    datadir = codedir+'/data/'
    return datadir

def readfile(filename):
    # Load the file
    with open(filename,'r') as f:
        lines = f.readlines()
    return lines

def convert(filename):
    """
    Convert an IDL file to Python
    """

    if os.path.exists(filename)==False:
        raise ValueError(filename,' NOT FOUND')
    
    # Load the file
    lines = readfile(filename)
    
    # Load the search/replace values
    replace = readfile(datadir()+'idl2py_sed.txt')
    
    # Add import statements at the beginning
    
