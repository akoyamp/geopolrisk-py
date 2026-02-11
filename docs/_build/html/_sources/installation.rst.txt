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

License
-------

The source code of ``geopolrisk-py`` is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. A copy of the license is provided in the ``LICENSE`` file at the root of the repository.

The GPL-3.0 license applies to the original software implementation developed for the GeoPolRisk method.

Structured database files distributed with this package may contain derived data originating from third-party sources (e.g. World Mining Data, BACI, and Worldwide Governance Indicators). These underlying data remain subject to the licenses and terms of use defined by their respective original providers and are not relicensed under GPL-3.0.


Third party data sources and licenses
------------------------------------

The GeoPolRisk method relies on several external data sources for mining production, international trade, and governance indicators. These data sources are provided by third parties and are subject to their respective licenses and terms of use, as defined by the original data providers.

All databases distributed with this library are structured specifically for the operational implementation of the GeoPolRisk method. They are provided solely for use within this methodological context and are not intended to serve as standalone general-purpose data repositories.

Mining production statistics are based on *World Mining Data*, published by the Austrian Federal Ministry of Finance. The production data included in this package are derived from World Mining Data and have been processed and structured specifically for use within the GeoPolRisk methodology. They do not constitute or claim to represent the official World Mining Data publication. The licensing and terms of use are specified in the official documentation and on the publisher’s website:
`World Mining Data – Austrian Federal Ministry of Finance <https://www.bmf.gv.at/en/topics/mining/mineral-resources-policy/wmd.html>`_

International trade data are sourced from the BACI database developed by CEPII and derived from UN Comtrade data. BACI is distributed under the **Etalab Open License 2.0**, as specified by CEPII:
`BACI database – CEPII <https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37>`_

Governance indicators are obtained from the Worldwide Governance Indicators project of the World Bank. These data are licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license:
`Worldwide Governance Indicators – World Bank <https://data360.worldbank.org/en/dataset/WB_WGI>`_


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
