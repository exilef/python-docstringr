# python-gen-docstrings

For the lazy.

Automatically generates numpy-style docstrings for Python scripts and inserts them into the source code using lib2to3.

Currently very hacky proof of concept.

Feel free to adapt. If you have made changes that you would like to contribute, just create a pull request.

Some type guessing is done if parameters have default values. Generated docstrings have the following format:

.. code:: python

    """
    Missing documentation
    
    Parameters
    ----------
    param1 : Type
        Description
    param2 : Type, optional
        Description (default None)
    
    Returns
    -------
    Value : Type
        Description
    """
    
Usage
-----

.. code::
    python gen_docstrings.py PATH_TO_PYTHON_FILES
    
Recursively (!) lists all `.py` files in directory and inserts docstrings
at function bodies, writing result to file suffixed with `_docstringed`.


TODO
----

* Respect existing docstrings
* More flexibility
* Other docstring formats (Google, ..)
* Fix bugs
