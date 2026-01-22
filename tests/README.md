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

**Python 3.11 is mandatory.**
Always specify the version explicitly when creating the environment.

Choose **one** of the following methods.

---

### Option A — `venv` (recommended)

Requires Python 3.11 to be installed on the system.

```bash
# Windows
py -3.11 -m venv venv

# macOS / Linux
python3.11 -m venv venv
```

---

### Option B — Conda (Anaconda / Miniconda)

Recommended for users already working in Conda-based workflows.

```bash
conda create -n geopolrisk-env python=3.11
conda activate geopolrisk-env
```

---

### Option C — `virtualenv`

Requires Python 3.11 to be installed.

```bash
pip install virtualenv
virtualenv -p python3.11 venv
```

---

### Option D — `pipenv`

Requires Python 3.11 to be installed.

```bash
pip install pipenv
pipenv --python 3.11 install -e ".[testing]"
```

---

## 3. Activate and verify the environment

Activate the environment created above and **verify the Python version**.

```bash
python --version
```

The output **must** be:

```
Python 3.11.x
```

> **Important**
> If the version is incorrect:
>
> * Deactivate the environment
> * Delete it
> * Recreate it using an explicit Python 3.11 command
> * Verify the version *before* installing any packages

---

## 4. Install test dependencies

If dependencies were not installed during environment creation:

```bash
pip install -e ".[testing]"
```

---

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
