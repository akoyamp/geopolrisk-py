# The geopolrisk-py library documentation

# The library is licensed by GNU General Public License 3.0
The geopolrisk-py is a python library that allows the assessment of a geopolitical related supply risk of a resource from the perspective of a country/region/trade bloc/company.
An assessment would result in two main values; 
1. GPRS - The probability of supply risk of importing a resource (0 - 1) usefull for comparative risk assessment,
2. Characterization Factors for GSRP (Geopolitical supply risk potential indicator (Midpoint))
The library is available to download using pip package manager.

## After installation
A folder in the Documents directory of the installed user is created after importing the library for the first time named "geopolrisk". Three sub folders are created: *'database'*, *'logs'*, and *'output'*. These are important for the working of the library. The *'database'* folder must contain the library database. Copy the [library databases](https://github.com/akoyamp/geopolrisk-py/tree/main/geopolrisk-py/lib/) to the directory *'geopolrisk/database/'* created in the documents folder to use the library. 
The *'logs'* folder stores the logs of the assessment. The *'output'* folder stores a database containing the results of the assessment and also the exports of the results.
