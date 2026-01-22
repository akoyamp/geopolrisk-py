Installation and Requirements
=============================

Requirements
------------

- Python **≥ 3.10 and < 3.12**
- ``pip``

The Python version is intentionally restricted to this range and is strictly enforced by the package metadata.
Installing ``geopolrisk-py`` with a newer Python version (for example Python 3.12 or 3.13) will result in an installation error.

``geopolrisk-py`` depends on scientific Python libraries that are stable and well tested within these versions.
This ensures compatibility with integration into other Python-based life cycle assessment tools, in particular Brightway.

The library relies on common scientific Python packages such as ``pandas`` and ``openpyxl``, as well as standard library modules (e.g. ``sqlite3``).
All required runtime dependencies are declared in the package metadata and are installed automatically.

Installation
------------

Create a virtual environment (recommended)
-------------------------------------------

It is strongly recommended to install ``geopolrisk-py`` inside a virtual environment created
explicitly with Python 3.10 or 3.11.

Using ``venv`` (pip-based workflow):

.. code-block:: bash

   python3.11 -m venv venv
   source venv/bin/activate
   python --version

Using ``conda``:

.. code-block:: bash

   conda create -n geopolrisk-env python=3.11
   conda activate geopolrisk-env
   python --version

Install from PyPI
-----------------

The recommended way to install ``geopolrisk-py`` is via PyPI using ``pip``.
Ensure that the active Python interpreter satisfies the version requirement.

.. code-block:: bash

   pip install geopolrisk-py

Install from source (development version)
-----------------------------------------

To install the development version from the GitHub repository:

.. code-block:: bash

   git clone https://github.com/akoyamp/geopolrisk-py.git
   cd geopolrisk-py
   pip install -e .

This option is intended for developers or users who wish to inspect, modify, or test the source code directly.

Package availability
--------------------

``geopolrisk-py`` is currently distributed via **PyPI**.
A ``conda-forge`` package is not available at this time.
