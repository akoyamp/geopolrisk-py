The GeoPolRisk Module Documentation

# Getting started
## Installing the GeoPolRisk Module
The GeoPolRisk module is a python package that contains methods to calculate the GeoPolitical Related Supply Risk Potential of a resource for a specific macroeconomic unit during a period. To download this package, the user can use the command prompt or if they have downloaded Python using anaconda, then use anaconda prompt. Type the following to download the GeoPolRisk Module.

pip install -i https://test.pypi.org/simple/ Geopolrisk==0.9
# Modules and Methods
   ## Main module
A module is a file containing Python definitions and statements. The file name is the module name with the suffix .py appended. A module can be imported in any python script to use the variables and methods declared within. 

To import the methods and variables to calculate the user must import the module using the following code.
### The code:
~~~
pip install -i https://test.pypi.org/simple/ Geopolrisk==0.9
~~~
geopolrisk is the name of the package that contains several modules within. One of the modules, which contain all the necessary methods, is main. Within the main module, a class named operations is instantiated in the script. 

The class contains several individual methods that inherit each other. The newclassinstance can access all the methods and variables declared in the class operations to use.

Note: The name newclassinstance is user-defined.
## simplerun:
The simplerun method is an easy guided user console input-based method. The user enters all the necessary input data in a console guided by step-by-step text.
~~~
from geopolrisk import main

newclassinstance = main.operations()

newclassinstance.simplerun()

~~~

Note: Green: User Inputs


## totalcalculation:
Similar to simplerun, totalcalculation is a one-stop method to calculate the GeoPolRisk value. However, the inputs for this method are not direct. Unlike simplerun, this method uses ISO codes and HS codes to define the country and resource as arguments [annexe]. For example, using the same as above, the HS code used for cobalt is 810520, and the ISO code for European Union is 97. 

**Mandatory arguments:**

- **period** : The year of assessment (integer)
- **reporter**: The area of assessment (integer*: ISO code of the area [annexe])*
- **HSCode**: The HS code of the commodity under assessment (integer)
- **recyclingrate**: The recycling input rate of the resource (float)
- **scenario**: Type of scenario under assessment.
  - 0: Assessment under the worst-case scenario of recycling redistribution
  - 1: Assessment under the best-case scenario of recycling redistribution.

Note: The scenario does not affect the assessment if the value for recyclingrate is '0'.

**Other arguments:** 

- **frequency:** Data set frequencies:
  - A: Annual
  - M: Monthly
- **partner:** The area receiving the trade. The default value is 'all'. If the user wants a specific trade route, specify the ISO code of the area.
- **Tradeflow:** The most common values are 
  - 1: imports 
  - 2: exports
- **exportType:** The results of the assessment are downloaded into an output folder created in the user's documents folder. The available file format of the results are 'csv'; 'excel', 'json'.
~~~
from geopolrisk import main

newclassinstance = main.operations()
newclassinstance.TotalCalculation(period = 2010,reporter = 97,HSCode = 810520,recyclingrate = 0,scenario = 0,)

~~~
This method is a calculation function that uses other methods and provides the risk value and characterization factor as an exporting file. It calls run, productionQTY, traderequest.
## run:
### setpath: 
A function that sets the path of production data, trade data and worldwide governance indicator data. Any user intending to use private data, especially for trade and the indicator, can modify the arguments.

**Arguments:**

- **prod\_path:** The path of the production database.
- **trade\_path:** The path of the trade database.
- **wgi\_path:** The path of the indicator database. 

Note: The trade\_path is currently under development in version 0.9.
### regions:
This method sets other user-defined regions required for the study that shall be used in the assessment. 

Note: This method is not yet fully implemented in version 0.9
### createTable: 
This method creates a database if the user does not possess the predefined database.

The run method calls setpath, regions and createTable methods if the user has not specifically set the path for private database or has not defined any regions. 
## traderequest:
This method calls for the COMTRADE API and calculates the numerator of the GeoPolRisk formula. All the arguments of totalcalculation except for 'exportType' are used in this method. In addition:

- ` `**classification**:  Trade data classification scheme:
  - *HS:* goods* 
  - EB02: *services*
  ## productionQTY:
productionQTY calculates the Herfindahl Hirschman Index (HHI) and total domestic production of the resource.

**Arguments:**

- **Element:** The resource's name for assessment (ex: 'Cobalt', 'Iron', 'Manganese').
- **Economic Unit:** The name of the area in assessment [annexe].
# Other Methods
   1. ## endlog:
This module uses error logging using a package called 'logging'. Logging files are created when the class (main) is instantiated. However, the endlog also captures the number of API requests (both successful and failed) and total requested calculation into the log file. Another important method of this method is to export the results into the requested format. The data is generally stored in a data frame 'outputDF' and exported into a specific format requested by the user. If totalcalculation is not used, the user must explicitly assign it to the variable 'outputDFType'; else, the data frame shall be exported as csv.

Note: The data frame 'outputDF' is an empty data frame and does not record calculations if totalcalculation is not used. The users are free to use this variable to append necessary information. 
## generateCF:
A straightforward method to generate the characterization factors in a specified format. It generates a file with the entire database that also contain the characterization factors.

**Arguments:**

- **exportType:** Available file export types are 'csv', 'excel', 'json'.
- **orient:** The orientation type for json. [*(json documentation)*](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html)
  1. ## Support methods (select and execute)
The databases are stored as sqlite3 database files within the module. They are copied to the document folder for easy access and the user preference database. Generally, access to the database is by using SQL. To avoid redundancy, these methods come in handy.

Note: These methods shall be depreciated in the following versions.
# Global Variables
   1. ## \_\_init\_\_:
The main module instance newclassinstance creates a logging file and sets the basic configuration of the logging file, resets the API request counters and creates an empty data frame to store the results and the export type. 

The calculation module requires non-variable data such as the hs codes, country names, corresponding iso codes, etc. These data are read to the script when the package is imported.
## Variables
Pre requires calling traderequest method

- **numerator:** Product sum of the trade to its corresponding worldwide governance indicator
- **tradetotal:** The sum of trade values of importing the resource.

Pre requires calling productionQTY method

- **HHI:** The Herfindahl Hirschman index [list of values for the entire available period]
- **Prod\_Qty:** Total domestic production of the resource.

Pre requires calling totalcalculation method

- **WA:** The weighted trade average (second factor of the GeoPolRisk equation)
- **GPRS:** The GeoPolRisk score of importing a resource during a period.
- **GPSRP:** The characterization factor for the GeoPolRisk method.

# Example Code

~~~
from geopolrisk import main

newclassinstance = main.operations()

newclassinstance.setpath() 
#newclassinstance.run() Do not run this method if you have predefined data (production, trade)

newclassinstance.traderequest(frequency = "A", 
    classification = "HS",
    period = "2010",
    partner = "all",
    reporter = "97",
    HSCode = "810520",
    TradeFlow = "1",
    recyclingrate = 0,
    scenario = 0
    ) #API call for trade data on imports of cobalt to European Union in 2010

newclassinstance.productionQTY('Cobalt', 'EU28') #Fetch all productiond data for Cobalt to calculate HHI 
                                                 #Fetch data of cobalt production in the EU
                                                 
"""
Now necessary methods are called to calculate the geopolitical supply risk of
importing cobalt to European Union. 
The variables numerator, tradetotal, HHI, Prod_Qty are required to calculate the 
value.
"""
numerator = newclassinstance.numerator
totaltrade = newclassinstance.tradetotal
HHI = newclassinstance.HHI
productionquantity = newclassinstance.Prod_Qty

WeightedTradeAverage = numerator/(totaltrade + productionquantity[40])
HHI = HHI[40] #2010 is in the 40th row of the database.

GeoPolRisk = HHI * WeightedTradeAverage

print(GeoPolRisk)

~~~

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
