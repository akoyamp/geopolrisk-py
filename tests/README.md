# Test Suite for geopolrisk-py

This directory contains the automated test suite for **geopolrisk-py**. The tests are designed to verify the correctness, internal consistency, and long-term stability of the GeoPolRisk implementation.

The suite includes unit tests for core computational components, as well as integration and regression tests that validate the full calculation workflow against established reference results.

## Test scope and structure

The test suite is organised by functional scope as follows:

* **`test_core.py`**
  Validates the numerical core of the GeoPolRisk method, including HHI calculations, import risk metrics, GeoPolRisk scores, and characterization factor computation.

* **`test_database.py`**
  Tests low-level database utilities, ensuring correct execution of internal SQLite queries and database interactions.

* **`test_util.py`**
  Covers supporting utility functions related to data handling, country and region conversion, aggregation logic, and result formatting.

* **`test_main.py`**
  Tests the main user-facing workflow (`gprs_calc`), verifying that complete calculations return results with the expected structure for both country-level and regional assessments.

* **`test_geopolrisk_data_results_from_excelfile.py`**
  Provides regression tests that compare computed results against reference values derived from an Excel-based test case. These tests ensure that end-to-end results remain consistent with a known reference implementation.

## Running the tests

Tests are not included in the PyPI distribution and must be executed from a cloned copy of the repository.

### 1. Clone the repository

```bash
git clone https://github.com/akoyamp/geopolrisk-py.git
cd geopolrisk-py
```

## 2. Create a Python environment (Python 3.11 required)

**Python 3.11 is required for running the test suite.**
The Python version must be specified explicitly when creating the environment.

## 3. Activate and verify the environment

Activate the environment created above and **verify the Python version**.

```bash
python --version
```

## 4. Install test dependencies

If test dependencies were not installed during environment creation:

```bash
pip install -e ".[testing]"
```

## 5. Run the test suite

```bash
python tests/run_test.py
```

The `run_test.py` script executes the full test suite in a controlled and reproducible manner and reports all failures directly to the console.

## Purpose of the tests

The test suite is intended to:

* Detect unintended numerical changes
* Ensure reproducibility of GeoPolRisk results
* Safeguard against regressions introduced by refactoring or feature extensions

## Notes for contributors

Contributors are strongly encouraged to run the full test suite before submitting pull requests. New features or bug fixes should include corresponding tests where appropriate.

Best practices:

* Always specify the Python version explicitly during environment creation
* Verify the active Python version immediately after activation
* Never commit environment directories (`venv/`, `env/`, `.venv/`) to version control

Recommended setup:

* General users: `python3.11 -m venv venv`
* Data science workflows: `conda create -n geopolrisk-env python=3.11`
