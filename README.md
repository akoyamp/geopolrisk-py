# The geopolrisk-py library documentation


# Getting started
## Installing the GeoPolRisk Module
The geopolrisk-py is a python library that allows the assessment of a geopolitical related supply risk of a resource from the perspective of a country/region/trade bloc/company.
An assessment would result in two main values; GPRS - the share of commodity imports at risk (0 - 1) usefull for comparative risk assessment,
characterization Factors for GSRP (Geopolitical supply risk potential indicator (Midpoint))
The library is available to download using pip package manager.
~~~
pip install -i https://test.pypi.org/simple/ Geopolrisk==1.3
~~~

# Modules and Methods
The library has following four modules preceded by an init that performs some actions required to smoothly perform a calculation.
##__init__ module:
    Reads static databases : resource price data, normalized governance indicator data, commodity hs codes, country iso codes
    Creates a directory in documents folder (only for windows users): Output folder for database to record calculations and exporting results as csv, Log folder for storing logs
    Loads several functions such as logging, sql and some global variables
    
## core module
Contains functions that calculate the components of the geopolrisk method
1. settradepath(path): To declare the path of the company trade data as an excel file. Must provide path an abosolute trade path. ex. c:/Users/UBx/Documents/tradepath.xlsx

### Format for company trade data
Follow the format listed below:

| Reporter    | ptCode      | ptTitle     | TradeQuantity    |
| ----------- | ----------- | ----------- | ---------------- |
| Germany     | 76          | Brazil      | 53399700         |
| Germany     | 156         | China       | 73139615         |

ptCode, ptTitle and TradeQuantity are mandatory data that needs to be in the excel file.
ptCode: ISO 3 digit code of the country from where a resource is imported
ptTitle: The name of the country from where a resource is imported.
TradeQuantity: Quantity of resource imported in kilograms.

2. regions(*args): Define additional regions of assessment. By default all the countries and EU is included in the database. 
To define a new region, a dictionary must be provided with key as the name of the region and values is a list of countries in the region.
All the values must be in string and must be exactly as in the ISO.
~~~
{"West Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "Belgium"]}
~~~

3. COMTRADE_API(classification = "HS", period = "2010", partner = "all", reporter = "276", HSCode = "2602", TradeFlow = "1", recyclingrate = 0, scenario = 0):
Function to call the UN COMTRADE api for fetching the trade data.
**Mandatory arguments:**
- **period** : The year of assessment (integer)
- **reporter**: The area of assessment (integer*: ISO code of the area [annexe])*
- **HSCode**: The HS code of the commodity under assessment (integer)
- **recyclingrate**: The recycling input rate of the resource (float)
- **scenario**: Type of scenario under assessment.
  - 0: Assessment without recycling
  - 1: Assessment under the best-case scenario of recycling redistribution.
  - 2: Assessment under the worst-case scenario of recycling redistribution

Note: The scenario does not affect the assessment if the value for recyclingrate is '0'.

4. InputTrade(sheetname = None): Function to calculate the trade data using specific company data.
Function settradepath must be called to define the path of the company data.

5. WTA_calculation(period, TradeData = None, PIData = None, scenario = 0, recyclingrate = 0.00): Function to calculate the second component of the GeoPolRisk method.
The trade data from either the COMTRADE function or InputTrade function is required as an argument. PIData is the world governance indicator that is stored in a variable by the init module.
However, the argument is provided in case of use of other governance indicators.

6. productionQTY(Resource, EconomicUnit): Function to calculate the HHI (first component of the GeoPolRisk Method) and local production quantity. 
Arguments required are the name of the resource (not HS code) and the economic unit (country/existing or defined regions/defined economic blocs)

7. GeoPolRisk(ProductionData, WTAData, Year, AVGPrice): Function to calculate the values of the GeoPolRisk method. The ProductionData is a list of HHi and local production quantity.
The WTAData is a list of the calculation involving trade. AVGPrice is the yearly average price of the resource. It provides a list of four values.
[ HHI, WTA, GPRS, CF]

###samplecode on how to use the functions from core module
~~~
from geopolrisk.assessment.core import *
from geopolrisk.assessment.__init__ import _wgi, _price #Optional

Resource = "Nickel"
HS = 2604
Country = Germany
ISO = 276
Year = 2016

TradeData = COMTRADE_API(classification = "HS", period = Year, partner = "all", reporter = ISO, HSCode = HS, TradeFlow = "1", recyclingrate = 0, scenario = 0)
WTAData = WTA_calculation(period, TradeData = TradeData, PIData = _wgi, scenario = 0, recyclingrate = 0.00)
ProductionData = productionQTY(Resource, Country)

YearlyAveragePrice = 10203.98
YearlyAveragePrice =  _price[Year].tolist()[_price.hs.to_list().index(HS)] #Optional - A database already exists that can be used to fetch the price data.

GeoPolRisk(ProductionData, WTAData, Year, YearlyAveragePrice)

~~~

## operations module:
Contains aggregate functions to simplify assessment.
Functions converCodes, sqlverify, recorddata, updatedata are helper methods for other aggregate functions.

1. gprs_comtrade(resourcelist, countrylist, yearlist, recyclingrate, scenario, database="record"): An aggregate function for a complete geopolitical related supply risk assessment using COMTRADE database (ie at macro level).
Instead of using the functions from the core module, a list of all the data is provided to get an output file with the results. This function records all the assessment into a database in the documents directory.
This is to prevent repeated API calls to the COMTRADE as there is a limit to use the free API.
This function allows to either record or update the database. Database update might be necessary in some cases where the API requests result in a null response. The function considers it as a successfull API request and stores null in the database.
**Arguments:**
**resourcelist**: A list of all the resources for the assessment as HS commodity codes.
**countrylist**: A list of all the countries under assessment as 3 digit ISO codes.
**yearlist**: A list of all the years in integers.
**recyclingrate**: The ratio of domestic recycling of the resource (typically 0 to 1) also can provide from 0 to 100.
**scenario**: As defined above
**database**: Two options "record" or "update" 

### Example to demonstrate the use of aggregate function.
~~~
ListofMetals = [2602, 2601, 2603, 2846, 2614,]
ListofCountries = [36, 124, 97, 251, 276, 392, 826, 842,] 
ListofYear = [2017, 2018, 2019, 2020]

from geopolrisk.assessment.operations import gprs_comtrade

gprs_comtrade(ListofMetals, ListofCountries, ListofYear, 0, 0)

~~~
2. gprs_regional(resourcelist, countrylist, yearlist, recyclingrate, scenario): Similar function to that of the above but for in case of newly defined regions.

3. gprs_organization(resourcelist, countrylist, yearlist, recyclingrate, scenario, sheetname): Aggregate function using specific trade data. Additional argument is to provide the sheetname.
The list of resources and year should match the provided trade data.

4. udpate_cf, updateprice are functions to automatically update null data stored as a result of a failed API request and changes in price data (or updates).

5. endlog(): A counter is mainted to read the number of API requests
6. generateCF(): A function to extract all the data into csv, excel or json files from the database stored in documents folder.

# Other Modules
1. The gcalc module has one method guided for a console input based assessment.
2. The functions in gprsplots module read the output file. An assessment must be done before using this module. There are three ways of plotting the results.
trendplot for plotting the evolution of supply risk. Must have more than three years assessed.
indplot for comparing each resource or country for ONE particular year.
compareplot for stacked graphs for comparison for one year.
   
# ANNEXE
 

|**id**|**hs**|
| - | - |
|Aluminium|2606|
|Antimony|261710|
|Asbestos|2524|
|Barytes|2511|
|Bismuth|8106|
|Cadmium|8107|
|Chromium|2610|
|Coal|2701|
|Cobalt|810520|
|Copper|2603|
|Gold|7108|
|Graphite|2504|
|Iron|2601|
|Lead|2607|
|Lithium|283691|
|Magnesite|251910|
|Magnesium|251910|
|Manganese|2602|
|Mercury|280540|
|Molybdenum|2613|
|Natural gas|271111|
|Nickel|2604|
|Petroleum|2709|
|Rare earth|2846|
|Silver|261610|
|Tin|2609|
|Titanium|2614|
|Tungsten|2611|
|Uranium|261210|
|Zinc|2608|
|Zirconium|261510|

## Country ISO codes
ISO CODES: https://www.iso.org/standard/63546.html
