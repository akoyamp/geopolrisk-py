# The geopolrisk-py library documentation

The Geopolitical Supply Risk (GeoPolRisk) method assesses raw material criticality in Life Cycle Assessment, complementing traditional resource and environmental impact indicators. It is also applied for comparative risk assessment. However, calculating values for the GeoPolRisk method, such as characterization factors for the Geopolitical Supply Risk indicator and the supply risk score for comparative assessment, can be complex. To address this, the _'geopolrisk-py'_ library has been developed to operationalize the method, simplifying the calculation process. This library processes data inputs like raw material names, countries, and years, making it more accessible. A notable feature is its ability to serve as a company-specific supply risk assessment tool.

# Features of the 'geopolrisk-py' Library

The _geopolrisk-py_ library is organized into four modules: **'database.py'**, **'core.py'**, **'main.py'**, and **'utils.py'**, each with specific roles to facilitate the calculation of the GeoPolRisk method.

1. **database.py**: This module is responsible for loading all the essential background data required for the library’s operations. The necessary data includes mining production data (from world mining data), trade data (from BACI for past years), and governance indicators (from the World Bank). These datasets are stored in a SQLite3 database, which is updated annually and available in the repository. Upon installation, the library sets up a folder in the Document folder in the user's home directory with three subfolders:

   - **databases**: Users should place the downloaded background database here.
   - **output**: This folder stores the SQLite3 database and Excel output files generated after calculations.
   - **logs**: For debugging errors encountered during the process.

2. **core.py**: This module contains functions that compute each component of the GeoPolRisk method, following the structure of the formula. The functions accept specific inputs like raw material names, countries, and years. To simplify input, the library matches raw materials to their Harmonized System (HS) codes, which are commonly used in trade. Similarly, it maps country names to their three-digit ISO codes, both stored in the background database. This helps standardize inputs, making it easier for users to perform calculations. Additionally, the **'utils.py'** functions assist in transforming names into the required HS and ISO codes for internal processing.

3. **utils.py**: This module supports data transformation, ensuring compatibility between user input and database requirements. It handles the conversion between names (strings) and codes (HS and ISO), aligning user inputs with the functions in **'core.py'**. For example, if a user defines a new region or group of countries, **'utils.py'** functions can aggregate trade and production data accordingly. The module also provides the **'transformdata'** function, allowing users to load company-specific trade data in an Excel format. This function extracts HS codes and ISO codes from the background database and reformats the trade data to the structure required for calculations.

4. **main.py**: The central module of the library, **'main.py'**, simplifies the use of the GeoPolRisk method through the **'gprs_calc'** function. Users can input a _'list'_ of raw materials, countries, and years to compute GeoPolRisk values. The **'gprs_calc'** function calls relevant functions from **'core.py'** to calculate the supply risk score (using the first two components of the GeoPolRisk formula) and the characterization factors for Life Cycle Assessment (using all three components). Results are stored in an Excel file and a SQLite3 database, which are then exported to the "outputs" folder for easy access.

### Unique Features of the _geopolrisk-py_ Library

The _'geopolrisk-py'_ library offers several features to enhance its functionality:

- **Custom Region Creation**: Users can define regions or groups of countries not available in the background database. This allows for trade aggregation and region-specific supply risk analysis, a capability supported by **'utils.py'** and **'core.py'** functions.
- **Company-Specific Risk Assessment**: A standout feature is the ability to calculate supply risk based on company-specific trade data. Using a predefined Excel template available in the repository, users can input their trade data, which the library then processes using **'transformdata'** and other relevant functions. For example, **'importrisk_company'** in **'core.py'** calculates the second component of the GeoPolRisk method (weighted import risk), tailored to the company's unique trade mix. This feature enables companies to model different supply risk scenarios based on their specific supply chains and compare them to national averages.

# After installation

A folder in the Documents directory of the installed user is created after importing the library for the first time named "geopolrisk". Three sub folders are created: _'database'_, _'logs'_, and _'output'_. Copy the [Company data.xlsx](https://github.com/akoyamp/geopolrisk-py/tree/main/geopolrisk-py/lib/) to the directory _'geopolrisk/database/'_ created in the documents folder to use it.
The _'logs'_ folder stores the logs of the assessment.
The _'output'_ folder stores a database containing the results of the assessment and also the exports of the results.
