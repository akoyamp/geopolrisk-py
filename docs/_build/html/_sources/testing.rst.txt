.. _Testing:

Testing
========

The test suite is included in the source repository and is intended to verify
the correctness and internal consistency of the GeoPolRisk implementation.

What is tested
---------------

The tests validate:

- Core GeoPolRisk calculations, including HHI, import risk, GeoPolRisk scores,
  and characterization factors
- Data handling and mapping utilities
- Correct interaction between the main components of the library

The tests are designed to ensure that numerical results are reproducible and
that changes to the code do not break existing functionality.

How to run the tests
---------------------

Tests are not included in the PyPI distribution and must be run from a cloned
copy of the repository.

1. Clone the repository and move into it:

.. code-block:: bash

   git clone https://github.com/akoyamp/geopolrisk-py.git
   cd geopolrisk-py

2. Install the package together with test dependencies:

.. code-block:: bash

   pip install -e ".[testing]"

3. Run the full test suite **from the repository root directory**:

.. code-block:: bash

   python tests/run_tests.py

The test runner must be executed from the project root (i.e. the directory
containing ``pyproject.toml``). Running the script from inside the ``tests/``
directory may lead to file path resolution errors, in particular when tests
access reference Excel files stored under ``tests/data/``.

This script executes the complete test suite and reports any failures directly
to the console.

Test suite overview
---------------------

The test suite is organised into multiple modules, each targeting a specific
layer of the library. Together, they provide a mix of unit tests (individual
functions) and integration or regression tests (end-to-end consistency against
a reference calculation).

Core computation tests
------------------------------------------

This module focuses on the numerical core of the GeoPolRisk method.

- Validates that ``HHI`` returns values of the expected type and that the HHI
  value is normalised (between 0 and 1) for valid inputs.
- Confirms that invalid inputs (e.g., an unknown or unsupported country) raise
  appropriate errors rather than producing silent failures.
- Validates that ``importrisk`` returns the expected tuple structure
  (numerator, total trade, price) and that returned values are numeric.
- Checks that ``GeoPolRisk`` returns numeric outputs (score, CF, WTA) and that
  the score matches the implemented equation for a controlled input case.
- Includes a negative-input test to confirm that the function behaviour is
  explicit when provided with non-physical values (for example, negative
  numerators), rather than masking them.

Database utility tests
----------------------------------------------

This module tests the low-level SQLite interaction utilities used by the
library.

- Creates a temporary SQLite database and verifies that ``execute_query`` can
  successfully run INSERT operations.
- Verifies that SELECT queries return the expected number of rows and expected
  content, confirming that query execution and retrieval behave correctly.

Utility and data-handling tests
--------------------------------------------------

This module tests the supporting functions in ``utils.py`` that prepare and
transform data for the GeoPolRisk computations.

- ``replace_func``: verifies consistent handling of missing values
  (e.g., ``"NA"``, ``None``, whitespace).
- ``cvtcountry``: verifies conversion of country names to ISO numeric codes and
  validates error handling for invalid inputs.
- ``sumproduct`` and ID utilities: validates basic helper logic such as dot
  products and deterministic ID creation.
- Result framing: checks that result DataFrame creation utilities return
  correctly shaped pandas objects with expected columns.
- Trade data handling: uses small mocked trade DataFrames to validate key steps
  such as filtering, aggregation, and price calculation.
- Region creation: verifies that user-defined regions are added to the internal
  region registry in a consistent manner.

Main workflow tests
--------------------------------------

This module tests the user-facing orchestration function ``gprs_calc`` in
``main.py``.

- Confirms that the returned object is a DataFrame with the expected output
  schema for a non-regional run (country-level assessment).
- Confirms that a regional run (using a provided region dictionary) produces
  the same expected output schema.
- Confirms that an empty raw material list returns an empty result rather than
  failing unexpectedly.

Regression tests against a reference tool case:
------------------------------------------------------------------------------------------------------

This module provides higher-confidence checks by comparing computed results
against a fixed reference dataset extracted from a tool-based Excel test case.

- Loads a reference Excel test case and compares outputs for a selected set of
  raw materials (e.g., Nickel, Manganese, Graphite) across years and importers.
- Validates ``HHI`` by comparing both domestic production quantities and HHI
  values against the reference values.
- Validates ``importrisk`` by comparing numerator, total trade, and price
  against the reference values.
- Validates ``GeoPolRisk`` end-to-end by comparing the final score and derived
  outputs against the reference values, ensuring that the full calculation chain
  remains consistent with the documented tool case.
