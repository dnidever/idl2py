***************
Getting Started
***************

Quickstart
==========

This is how you can run |idl2py| directly from the unix command line.

.. code-block:: bash

	idl2py program.pro

The translated code will then appear in a file called ``program.py``.
	
You can also run |idl2py| from python.

.. code-block:: python

	from idl2py import idl2py
	idl2py.convert('program.pro')

