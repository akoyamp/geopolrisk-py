# Test Suite for geopolrisk-py

This directory contains the automated test suite for **geopolrisk-py**.
The tests are designed to verify the correctness, internal consistency, and
stability of the GeoPolRisk implementation.

The test suite includes unit tests for core computational functions as well as
integration and regression tests that validate the full calculation workflow
against reference results.

## Test structure

The test suite is organised by functional scope:

- **`test_core.py`**  
  Tests the numerical core of the GeoPolRisk method, including HHI, import risk,
  GeoPolRisk scores, and characterization factor calculations.

- **`test_database.py`**  
  Tests low-level database utilities, ensuring correct execution of SQLite
  queries used internally by the library.

- **`test_util.py`**  
  Tests supporting utility functions for data handling, country conversion,
  aggregation, and result formatting.

- **`test_main.py`**  
  Tests the main user-facing workflow (`gprs_calc`), verifying that complete
  calculations return results with the expected structure for both country-level
  and regional assessments.

- **`test_geopolrisk_data_results_from_excelfile.py`**  
  Provides regression tests that compare computed results against reference
  values extracted from a tool-based Excel test case. These tests ensure that
  end-to-end results remain consistent with a known reference implementation.

---

## Running the tests

Tests are not included in the PyPI distribution and must be run from a cloned
copy of the repository.

Clone the repository locally:

```bash
git clone https://github.com/akoyamp/geopolrisk-py.git
cd geopolrisk-py
```

From the repository root:

```bash
pip install -e ".[testing]"
cd tests
python run_test.py
```

The `run_test.py` script executes the full test suite in a controlled and
reproducible manner and reports any failures directly to the console.


## Purpose of the tests

The tests are intended to:

* Detect unintended changes in numerical results
* Ensure reproducibility of GeoPolRisk calculations
* Validate that refactoring or extensions do not break existing functionality

## Notes for contributors

Contributors are encouraged to run the full test suite before submitting pull
requests. New features or bug fixes should include corresponding tests where
appropriate.