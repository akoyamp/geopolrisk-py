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

To avoid issues, it is strongly recommended to install the library **inside a virtual environment created with Python 3.11**.

### Create a virtual environment with Python 3.11 (recommended)

Choose **one** of the following methods.

#### Option A — `venv` (recommended for most users)

Requires Python 3.11 to be installed on the system.

```bash
# Windows
py -3.11 -m venv venv

# macOS / Linux
python3.11 -m venv venv
```

Activate the environment:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Verify the Python version **before installing anything**:

```bash
python --version
# Must show Python 3.11.x
```

---

#### Option B — Conda (Anaconda / Miniconda)

```bash
conda create -n geopolrisk-env python=3.11
conda activate geopolrisk-env
python --version
```

---

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

The full test suite is included in the source repository and must be run from a local clone. Tests are **not** distributed via PyPI.

### Prerequisites

* Python **3.11** virtual environment active
* Repository cloned locally

Install test dependencies:

```bash
pip install -e ".[testing]"
```

> **Note**
> If you encounter an error stating that your Python version is not supported, verify that `python --version` reports **Python 3.11.x**. The test dependencies enforce the same version constraints as the library itself.

### Running the tests

Tests are executed via a single entry-point script to ensure deterministic execution.

```bash
cd tests
python run_test.py
```

This runs the complete test suite and reports any failures directly to the console.

## Purpose of the tests

The test suite is designed to:

* Detect unintended numerical changes
* Ensure reproducibility of GeoPolRisk calculations
* Validate end-to-end workflows against reference results
* Protect existing functionality during refactoring or extension

## Notes for contributors

* Always create environments with an explicit Python version (`python3.11`)
* Verify the Python version immediately after activation
* Never commit virtual environment directories (`venv/`, `.venv/`, `env/`)
* New features or bug fixes should include corresponding tests

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

