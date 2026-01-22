# The geopolrisk-py library documentation

The **geopolrisk-py** library implements the Geopolitical Supply Risk (GeoPolRisk) method for assessing raw material criticality in Life Cycle Assessment. It complements traditional resource and environmental indicators and can also be applied in comparative risk assessment.

The GeoPolRisk method relies on multiple data sources and non-trivial calculations, including characterization factors and supply risk scores. The **geopolrisk-py** library operationalizes the method by providing a structured and reproducible implementation that processes inputs such as raw materials, countries, and years. In addition to generic assessments, the library supports **company specific supply risk analysis**, allowing users to evaluate risks based on their own trade data.

## Features of the `geopolrisk-py` library

The library is organised into four core modules:

1. **`database.py`**
   Handles loading and management of background data required by the method, including mining production data (World Mining Data), trade data (BACI), and governance indicators (World Bank). These datasets are stored in a SQLite database that is distributed with the repository and updated annually. Upon first use, the library creates a dedicated folder in the user’s home directory containing:

   * `databases`: input templates and background data
   * `output`: generated SQLite databases and Excel result files
   * `logs`: log files for debugging and traceability

2. **`core.py`**
   Implements the numerical core of the GeoPolRisk method, including calculation of HHI, import risk, GeoPolRisk scores, and characterization factors. This module executes the equations defining the method using structured inputs prepared by supporting modules.

3. **`utils.py`**
   Provides data preparation and harmonisation utilities. It maps raw material and country names to standardized identifiers (HS codes, ISO codes), aligns production and trade datasets, aggregates overlapping trade codes, and ensures data consistency before calculations.

4. **`main.py`**
   Provides a user-facing interface that orchestrates the full workflow. Users define raw materials, years, and economic units, and the module coordinates calls to the core and utility functions. Results are written to Excel and SQLite outputs in a structured directory layout.

## Installation

### Python requirements (important)

**geopolrisk-py requires Python ≥ 3.10 and < 3.12.**

This restriction is intentional and enforced in the package metadata.
Using a newer Python version (e.g. 3.12 or 3.13) will result in installation errors.

To avoid issues, it is strongly recommended to install the library **inside a virtual environment created with Python 3.11**. An possibility is presented in the [documentation](https://geopolrisk-py.readthedocs.io/en/latest/installation.html)

### Install from PyPI

Once the correct Python environment is active:

```bash
pip install geopolrisk-py
```

### Install from source (development version)

```bash
git clone https://github.com/akoyamp/geopolrisk-py.git
cd geopolrisk-py
pip install -e .
```
## Testing

The full automated test suite is provided **only in the source repository** and is documented separately.

Please refer to the dedicated test documentation located in:

```
tests/README.md
```

That document contains:

* The scope and structure of the test suite
* Python version requirements
* Environment creation instructions
* Exact commands required to run all tests via the provided test runner

## After installation

Detailed usage instructions are available in the official documentation:
[https://geopolrisk-py.readthedocs.io/en/latest/](https://geopolrisk-py.readthedocs.io/en/latest/)

The documentation includes module-level explanations, a step-by-step user guide, and example workflows. A Jupyter notebook demonstrating typical usage is provided both online and in the `examples` folder of the repository.

## Support and contact

For bug reports and feature requests, please use the GitHub issue tracker:
[https://github.com/akoyamp/geopolrisk-py/issues](https://github.com/akoyamp/geopolrisk-py/issues)

For questions related to the GeoPolRisk method, interpretation of results, or academic use, contact:

**Anish Koyamparambath**
Email: [anish.koyam@hotmail.com](mailto:anish.koyam@hotmail.com)