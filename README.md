# The geopolrisk-py library documentation


# Getting started

- Install with `poetry install`.
- Get a free subscription key on https://comtradedeveloper.un.org/ and set it as `COMTRADE_SUBSCRIPTION_KEY` environment variable
- Create a folder for your work and set its absolute path in the environment variable `GEOPOLRISK_FOLDER`
- Copy [the library](https://github.com/akoyamp/geopolrisk-py/tree/main/geopolrisk-py/lib/library.db) under `{GEOPOLRISK_FOLDER}/databases/Library.db`

## Installing the GeoPolRisk Module
The geopolrisk-py is a python library that allows the assessment of a geopolitical related supply risk of a resource from the perspective of a country/region/trade bloc/company.
An assessment would result in two main values; 
1. GPRS - The probability of supply risk of importing a resource (0 - 1) usefull for comparative risk assessment,
2. Characterization Factors for GSRP (Geopolitical supply risk potential indicator (Midpoint))
The library is available to download using pip package manager.
~~~
pip install geopolrisk-py
~~~

## After installation
A folder in the Documents directory of the installed user is created after importing the library for the first time named "geopolrisk". Three sub folders are created: *'database'*, *'logs'*, and *'output'*. These are important for the working of the library. The *'database'* folder must contain the library database. Copy the library database to the directory created in the documents folder to use the library (https://github.com/akoyamp/geopolrisk-py/tree/main/geopolrisk-py/lib/library.db). Or you can provide the location of the database in the prompt asked when importing the library for the first time.
The *'logs'* folder stores the logs of the assessment. The *'output'* folder stores a database containing the results of the assessment and also all the exports of the results.

# Modules and Methods
The library has following five modules preceded by an init that performs some actions required to smoothly perform an assessment.
## __init__ module:
--> Reads static databases : resource price data, normalized governance indicator data, commodity hs codes, country iso codes

--> Creates a directory in documents folder (only for windows users): Output folder for database to record calculations and exporting results as csv, Log folder for storing logs

--> Loads several functions such as logging, sql and some global variables

--> The module has a class called instance. Variables in the instance class can be manipulated or used in specific applications. Important variables such as regionslist, price and wgi are manipulated in specific applications.
    
## core module
Contains functions that calculate the components of the geopolrisk method
1. *settradepath(path):* 
    Function to declare the path of the trade data as an excel or csv file.
    To declare the path of the company trade data as an excel file. Must provide path an abosolute trade path. ex. c:/Users/UBx/Documents/tradepath.xlsx

    ### Format for company trade data
    Follow the format listed below:

    | Reporter | ptCode | ptTitle | TradeQuantity |
    | -------- | ------ | ------- | ------------- |
    | Germany  | 76     | Brazil  | 53399700      |
    | Germany  | 156    | China   | 73139615      |

    ptCode, ptTitle and TradeQuantity are mandatory data that needs to be in the file.
    | code          | Description                                               |
    |---------------|---------------------------------------------------------- |
    | ptCode        | ISO 3 digit code of the country from where a resource is imported.                                                                   |
    | ptTitle       | The name of the country from where a resource is imported.|
    | TradeQuantity | Quantity of resource imported in kilograms.               |

2. regions(*args): 
    
    Define additional regions of assessment. By default all the countries and EU is included in the database. 
    To define a new region, a dictionary must be provided with key as the name of the region and values is a list of countries in the region.
    All the values must be in string and must be exactly as in the ISO.
    ~~~
    {"West Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "Belgium"]}
    ~~~

3. *worldtrade(year = "2010", country = "276", commodity = "2602"):*
    
    Function to call the UN COMTRADE api for fetching the trade data.
    **Mandatory arguments:**
    - **year** : The year of assessment (integer)
    - **country**: The area of assessment (integer*: ISO code of the area [annexe])*
    - **commodity**: The HS code of the commodity under assessment (integer)

4. *specifictrade(sheetname = None):* 
    
    Function to calculate the trade data using specific company data.
    Function settradepath must be called to define the path of the company data.

5. *weightedtrade(period, TradeData = None, PIData = None, scenario = 0, recyclingrate = 0.00):* 
    
    Function to calculate the second component of the GeoPolRisk method.
    The trade data from either the COMTRADE function or InputTrade function is required as an argument. PIData is the world governance indicator that is stored in a variable by the init module.
    However, the argument is provided in case of use of other indicators.

    Note: The scenario does not affect the assessment if the value for recyclingrate is '0'.

6. *ProductionData(Resource, EconomicUnit):* 
    
    Function to calculate the HHI (first component of the GeoPolRisk Method) and local production quantity. 
    Arguments required are the name of the resource (not HS code) and the economic unit (country/existing or defined regions/defined economic blocs)

7. *GeoPolRisk(ProductionData, WTAData, Year, AVGPrice):* 
   
    Function to calculate the values of the GeoPolRisk method. The ProductionData is a list of HHi and local production quantity (result from the *ProductionData* function).
    The WTAData is a list of the calculation involving trade. AVGPrice is the yearly average price of the resource. It provides a list of four values.
    [HHI, WTA, GPRS, CF]

### Example to use the core module
~~~
from geopolrisk.assessment.core import *
from geopolrisk.assessment.__init__ import instance #Optional
_price = instance.price
_wgi = instance.wgi
Resource = "Nickel"
HS = 2604
Country = "Germany"
ISO = 276
Year = "2016"

regions()
TradeData = worldtrade(year = "2016", country = "276", commodity = "2604")
ProductionData = ProductionData(Resource, Country)
WTAData = weightedtrade(Year, TradeData = TradeData, PIData = _wgi, scenario = 0, recyclingrate = 0.00)


YearlyAveragePrice = 10203.98
YearlyAveragePrice =  _price[Year].tolist()[_price.HS.to_list().index(HS)] #Optional - A database already exists that can be used to fetch the price data.

result = GeoPolRisk(ProductionData, WTAData, Year, YearlyAveragePrice)

~~~

## main module:
Contains aggregate functions to simplify assessment.

1. *main_complete (resourcelist, yearlist, countrylist, recyclingrate=0.0, scenario=0,sheetname=None,PIindicator=None):*

    An aggregate function for a complete geopolitical related supply risk assessment. Instead of using the functions from the core module, a list of all the data is provided to get an output file with the results. This function records all the assessment into a database in the documents directory. This is to prevent repeated API calls to the COMTRADE as there is a limit to use the free API. 
    Its a complete function that acknowledges, regional and company level assessment. Two functions from the core module must be called before this function is called. If a custom region is considered for the assessment such as example below, the regions function must be called and the new custom region must be declared.
    ~~~
    CustomRegion = {"West Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "Belgium"]}
    from geopolrisk.assessment.core import regions
    regions(CustomRegion)
    ~~~
    In case the data for the custom region is provided using an excel or csv file, the path to the file should be declared using settradepath function from the core module. (Must use the template provided in the tests folder: https://github.com/akoyamp/geopolrisk-py/tree/main/geopolrisk-py/tests). The sheetname should be provided in the sheetname argument in the function.
    ~~~
    {"West Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "Belgium"]}
    from geopolrisk.assessment.core import regions
    regions(CustomRegion)
    locationtotheexcelfile = "user/documents/folder/tradedata.xlsx"
    settradepath(locationtotheexcelfile)
    ~~~

    **Arguments:**
    1. **resourcelist**: A list of all the resources for the assessment as HS commodity codes.
    2. **countrylist**: A list of all the countries under assessment as 3 digit ISO codes.
    3. **yearlist**: A list of all the years in integers.
    4. **recyclingrate**: The ratio of domestic recycling of the resource (typically 0 to 1) also can provide from 0 to 100.
    5. **scenario**: Refer to https://doi.org/10.1016/j.resconrec.2020.105108 for more data. In this function, three scenarios are considered: 0 for no scenario, 1 for best case scenario, 2 for worst case scenario
    6. **sheetname**: In case data is provided through excel sheet, provide the sheetname (mandatory argument)
    7. **PIindicator**: In case of using other political instability indicator, provide the json or dataframe containing normalized values.  

    ### Example to demonstrate the use of main_complete function.
    ~~~
    ListofMetals = [2602, 2601, 2603, 2846, 2614,]
    ListofCountries = [36, 124, 97, 251, 276, 392, 826, 842,] 
    ListofYear = [2017, 2018, 2019, 2020]

    from geopolrisk.assessment.main import main_complete

    main_complete(ListofMetals, ListofYear, ListofCountries, 0, 0, sheetname= None, PIindicator = None)
    ~~~

    ### Example to demonstrate the use of main_complete function using custom region and specific trade data.
    ~~~
    ListofMetals = [2602, 2601, 2603, 2846, 2614,]
    ListofYear = [2017, 2018, 2019, 2020]
    CustomRegion = {"West Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "Belgium"]}
    locationtotheexcelfile = "user/documents/folder/tradedata.xlsx" #Avoid if using COMTRADE
    ListofCountries = ["West Europe"] 

    from geopolrisk.assessment.main import main_complete
    from geopolrisk.assessment.core import regions

    regions(CustomRegion)

    settradepath(locationtotheexcelfile) #Do not use if using COMTRADE

    main_complete(ListofMetals, ListofYear, ListofCountries, 0, 0, sheetname= "test", PIindicator = None)
    ~~~
2. *startmain (resourcelist, yearlist, countrylist, recyclingrate=0.0, scenario=0,sheetname=None,PIindicator=None):* 
    
    Function to calculate the GeoPolRisk but doesnt have the ability to aggregate data for regional calculation. In case of company level assessment, declare the path to the trade data as above before calling this function.

3. *endmain():*

    Exports the results of the assessment from the *startmain* function to the output folder.
    ### Example to demonstrate the use of main_complete function using custom region and specific trade data.
    ~~~
    ListofMetals = [2602, 2601, 2603, 2846, 2614,]
    ListofCountries = [36, 124, 97, 251, 276, 392, 826, 842,] 
    ListofYear = [2017, 2018, 2019, 2020]
    locationtotheexcelfile = "user/documents/folder/tradedata.xlsx" #Avoid if using COMTRADE


    from geopolrisk.assessment.main import main_complete
    from geopolrisk.assessment.core import regions

    regions()
    settradepath(locationtotheexcelfile) #Do not use if using COMTRADE

    startmain(ListofMetals, ListofYear, ListofCountries, 0, 0, sheetname= "test", PIindicator = None)
    endmain()
    ~~~


4. udpate_cf, updateprice are functions to automatically update null data stored as a result of a failed API request and changes in price data (or updates).


# Other Modules
1. utils module has some functions that are useful for the working of library. It has functions that record data, convert data and exports data.
   1. *generateCF(exportType="csv", orient=""):*
    Usefull function to export all calculated data from the database to one of three formats: csv, excel, json.
2. The console module has one method guided for a console input based assessment.
3. The functions in gprsplots module read the output file. An assessment must be done before using this module. There are three ways of plotting the results.
trendplot for plotting the evolution of supply risk. Must have more than three years assessed.
indplot for comparing each resource or country for ONE particular year.
compareplot for stacked graphs for comparison for one year.
   
# ANNEXE
 

| **id**      | **hs** |
| ----------- | ------ |
| Aluminium   | 2606   |
| Antimony    | 261710 |
| Asbestos    | 2524   |
| Barytes     | 2511   |
| Bismuth     | 8106   |
| Cadmium     | 8107   |
| Chromium    | 2610   |
| Coal        | 2701   |
| Cobalt      | 810520 |
| Copper      | 2603   |
| Gold        | 7108   |
| Graphite    | 2504   |
| Iron        | 2601   |
| Lead        | 2607   |
| Lithium     | 283691 |
| Magnesite   | 251910 |
| Magnesium   | 251910 |
| Manganese   | 2602   |
| Mercury     | 280540 |
| Molybdenum  | 2613   |
| Natural gas | 271111 |
| Nickel      | 2604   |
| Petroleum   | 2709   |
| Rare earth  | 2846   |
| Silver      | 261610 |
| Tin         | 2609   |
| Titanium    | 2614   |
| Tungsten    | 2611   |
| Uranium     | 261210 |
| Zinc        | 2608   |
| Zirconium   | 261510 |

## Country ISO codes
ISO CODES: https://www.iso.org/standard/63546.html

# New Comtrade API

Correspondance after getting a subscription key

```python
# os.environ["COMTRADE_SUBSCRIPTION_KEY"] must be set

import requests

period=2016
country=276
commoditycode=2604
a_type="C"
a_freq="A"
a_cl="HS"
a_p="all"
a_rg=1

url = f"https://comtrade.un.org/api/get?max=50000&type={a_type}&freq={a_freq}&px={a_cl}&ps={period}&r={country}&p={a_p}&cc={commoditycode}&rg={a_rg}&fmt=json"
url = f"https://comtradeapi.un.org/data/v1/get/{a_type}/{a_freq}/{a_cl}?period={period}&partnerCode={country}&cmdCode={commoditycode}&period={period}&subscription-key={os.environ['COMTRADE_SUBSCRIPTION_KEY']}"
requests.get(url).json()
```

returns 

```javascript
{'elapsedTime': '4.01 secs',
 'count': 56,
 'data': [{'typeCode': 'C',
   'freqCode': 'A',
   'refPeriodId': 20160101,
   'refYear': 2016,
   'refMonth': 52,
   'period': '2016',
   'reporterCode': 203,
   'reporterISO': None,
   'reporterDesc': None,
   'flowCode': 'X',
   'flowDesc': None,
   'partnerCode': 276,
   'partnerISO': None,
   'partnerDesc': None,
   'partner2Code': 0,
   ...
 }
}
```