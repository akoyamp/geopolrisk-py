# The geopolrisk-py library documentation

The Geopolitical Supply Risk (GeoPolRisk) method assesses raw material criticality in Life Cycle Assessment, complementing traditional resource and environmental impact indicators. It is also applied for comparative risk assessment. However, calculating values for the GeoPolRisk method, such as characterization factors for the Geopolitical Supply Risk indicator and the supply risk score for comparative assessment, can be complex. To address this, the _'geopolrisk-py'_ library has been developed to operationalize the method, simplifying the calculation process. This library processes data inputs like raw material names, countries, and years, making it more accessible. A notable feature is its ability to serve as a company-specific supply risk assessment tool.

# Features of the `geopolrisk-py` Library

The _geopolrisk-py_ library is organized into four modules: `database.py`, `core.py`, `main.py`, and `utils.py`, each with specific roles to facilitate the calculation of the GeoPolRisk method.

1. **database.py**: This module is responsible for loading all the essential background data required for the library’s operations. The necessary data includes mining production data (from world mining data) [@FMRA2023], trade data (from BACI for past years) [@cepii_baci_2024], and governance indicators (from the World Bank) [@WorldBank2024]. These datasets are stored in a SQLite3 database, which is updated annually and available in the repository. Upon installation, the library sets up a folder in the Document folder in the user's home directory with three subfolders:

   - **databases**: - Contains the input template (company_data.xlsx), which users can populate for company-level risk assessments.
   - **output**: This folder stores the SQLite3 database and Excel output files generated after calculations.
   - **logs**: For debugging errors encountered during the process.

2. **core.py**: This module implements the main computational logic of the GeoPolRisk method. It calculates each component of the method, including HHI, import risk, and the resulting GeoPolRisk score and the CFs. These calculations rely on background data that links raw material and country names to standardized identifiers. The module is responsible for executing the equations that define the method, using pre-processed and structured inputs provided by the supporting modules.

3. **utils.py**: This module handles the data preparation required for GeoPolRisk calculations. It maps defined raw material and country names to Harmonized System codes and ISO 3-digit codes, ensuring compatibility with the underlying database. It also aligns raw material production data with corresponding commodity trade data, which may include multiple overlapping HS codes, and aggregates them into a consolidated dataset. In effect, `utils.py` performs all the backend transformation and standardization needed to bridge data with the model’s requirements. It supports core.py by ensuring that inputs are clean, consistent, and ready for computation.

4. **main.py**: This module provides a one-stop interface that integrates the entire workflow. It allows users to define a list of raw materials, years, and economic units, and then manages the process of calling the appropriate functions from core.py, using data handled by utils.py. The outputs including the components of the GeoPolRisk method (HHI, import risk & price) along with the values (GeoPolRisk score & CF) are saved in both Excel and SQLite formats in an organized folder structure. This module is designed to simplify the application of the method for larger-scale or repeated assessments.

### Unique Features of the _geopolrisk-py_ Library

The _'geopolrisk-py'_ library offers several features to enhance its functionality:

- **Custom Region Creation**: Users can define regions or groups of countries not available in the background database. This allows for trade aggregation and region-specific supply risk analysis, a capability supported by **'utils.py'** and **'core.py'** functions.
- **Company-Specific Risk Assessment**: A standout feature is the ability to calculate supply risk based on company-specific trade data. Using a predefined Excel template available in the repository, users can input their trade data, which the library then processes using **'transformdata'** and other relevant functions. For example, **'importrisk_company'** in **'core.py'** calculates the second component of the GeoPolRisk method (weighted import risk), tailored to the company's unique trade mix. This feature enables companies to model different supply risk scenarios based on their specific supply chains and compare them to national averages.

## Installation

### Requirements

* Python >= 3.10 and < 3.12
* pip

The Python version is intentionally restricted to this range because geopolrisk-py depends on scientific Python libraries that are stable and well tested within these versions, and because this range aligns with integration into other tools (for example, Brightway-based workflows).

### Install from PyPI

```bash
pip install geopolrisk-py
```

### Install from source (development version)

```bash
git clone https://github.com/akoyamp/geopolrisk-py.git
cd geopolrisk-py
pip install -e .
```

Below is a **clean, copy-paste-ready README section**, written to **end this entire pytest/conda confusion** by giving users **one deterministic Git-based way** to run the full test suite via `run_test.py`.

No assumptions, no extras knowledge required.

---

## Testing

The full test suite is provided in the source repository and is executed via a single entry-point script.
This ensures that all tests are run in a controlled and reproducible way, independent of how `pytest` discovers files.

### What the test suite does

Running the test suite verifies that:

* Core GeoPolRisk calculations (HHI, import risk, GeoPolRisk score, characterization factor) behave as expected
* Data handling, mappings, and utility functions operate correctly
* The library functions correctly as an integrated system, not just at the individual function level

The tests are intended to validate numerical correctness and internal consistency of the implementation.

### How to run the tests

1. Move into the tests directory:

```bash
cd tests
```

2. Run the full test suite using the provided script:

```bash
python run_test.py
```

This command executes all tests and reports any failures directly to the console.

# After installation

For detailed guidance on how to use the library, please refer to the official documentation at https://geopolrisk-py.readthedocs.io/en/latest/. It includes explanations of each module, a step-by-step user guide, and a description of the underlying method. An example Jupyter notebook is also provided to demonstrate a typical workflow. This notebook is available both in the online documentation and in the `examples` folder of the repository.


## Support and Contact

For bug reports, feature requests, and technical questions, please use the
GitHub issue tracker:

https://github.com/akoyamp/geopolrisk-py/issues

For questions related to the GeoPolRisk method, interpretation of results,
or academic use of the software, you may also contact the corresponding author:

Anish Koyamparambath  
Email: anish.koyam@hotmail.com
