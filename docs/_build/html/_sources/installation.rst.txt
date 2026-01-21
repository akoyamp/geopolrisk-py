Installation and Requirements
=============================

Requirements
------------

- Python **≥ 3.10 and < 3.12**
- ``pip``

The Python version is intentionally restricted to this range.
``geopolrisk-py`` depends on scientific Python libraries that are stable and well tested within these versions.
This ensures compatibility with integration into other Python-based life cycle assessment tools, in particular Brightway.

The library relies on common scientific Python packages such as ``pandas`` and ``openpyxl``, as well as standard library modules (e.g. ``sqlite3``).
All required runtime dependencies are declared in the package metadata and are installed automatically.

Installation
------------

Install from PyPI (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The recommended way to install ``geopolrisk-py`` is via PyPI using ``pip``:

.. code-block:: bash

   pip install geopolrisk-py

This installs the latest released version together with all required dependencies.

Install from source (development version)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
