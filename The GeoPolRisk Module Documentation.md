The GeoPolRisk Module Documentation

1. # Getting started
   1. ## Python
Python is an interpreted high-level, general-purpose programming language.  The user must download Python to the device in order to use the GeoPolRisk module. Python can be downloaded from its [official web page](https://www.python.org/downloads/) or downloaded using its user-friendly package manager [anaconda](https://www.anaconda.com/products/individual) [\[docs\]](https://docs.anaconda.com/anaconda/install/index.html).
1. ## Using Python
Python can be used within any supporting ide found online such as [PyCharm](https://www.jetbrains.com/pycharm/), [Atom](https://atom.io/), [Eclipse](https://www.eclipse.org/eclipseide/) and [others](https://wiki.python.org/moin/IntegratedDevelopmentEnvironments). Anaconda comes with a built-in ide known as [spyder](https://www.spyder-ide.org/) designed to run Python by default, while Python has its ide to use known as [idle](https://docs.python.org/3/library/idle.html) (Python's Integrated Development and Learning Environment).
1. ## Installing the GeoPolRisk Module
The GeoPolRisk module is a python package that contains methods to calculate the GeoPolitical Related Supply Risk Potential of a resource for a specific macroeconomic unit during a period. To download this package, the user can use the command prompt or if they have downloaded Python using anaconda, then use anaconda prompt. Type the following to download the GeoPolRisk Module.

pip install -i https://test.pypi.org/simple/ Geopolrisk==0.9
1. # Modules and Methods
   1. ## Main module
A module is a file containing Python definitions and statements. The file name is the module name with the suffix .py appended. A module can be imported in any python script to use the variables and methods declared within. 

To import the methods and variables to calculate the user must import the module using the following code.
1. ### The code:
geopolrisk is the name of the package that contains several modules within. One of the modules, which contain all the necessary methods, is main. Within the main module, a class named operations is instantiated in the script. 

The class contains several individual methods that inherit each other. The newclassinstance can access all the methods and variables declared in the class operations to use.

Note: The name newclassinstance is user-defined.
1. ## simplerun:
The simplerun method is an easy guided user console input-based method. The user enters all the necessary input data in a console guided by step-by-step text.

Note: Green: User Inputs


1. ## totalcalculation:
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

This method is a calculation function that uses other methods and provides the risk value and characterization factor as an exporting file. It calls run, productionQTY, traderequest.
1. ## run:
   1. ### setpath: 
A function that sets the path of production data, trade data and worldwide governance indicator data. Any user intending to use private data, especially for trade and the indicator, can modify the arguments.

**Arguments:**

- **prod\_path:** The path of the production database.
- **trade\_path:** The path of the trade database.
- **wgi\_path:** The path of the indicator database. 

Note: The trade\_path is currently under development in version 0.9.
1. ### regions:
This method sets other user-defined regions required for the study that shall be used in the assessment. 

Note: This method is not yet fully implemented in version 0.9
1. ### createTable: 
This method creates a database if the user does not possess the predefined database.

The run method calls setpath, regions and createTable methods if the user has not specifically set the path for private database or has not defined any regions. 
1. ## traderequest:
This method calls for the COMTRADE API and calculates the numerator of the GeoPolRisk formula. All the arguments of totalcalculation except for 'exportType' are used in this method. In addition:

- ` `**classification**:  Trade data classification scheme:
  - *HS:* goods* 
  - EB02: *services*
  1. ## productionQTY:
productionQTY calculates the Herfindahl Hirschman Index (HHI) and total domestic production of the resource.

**Arguments:**

- **Element:** The resource's name for assessment (ex: 'Cobalt', 'Iron', 'Manganese').
- **Economic Unit:** The name of the area in assessment [annexe].
1. # Other Methods
   1. ## endlog:
This module uses error logging using a package called 'logging'. Logging files are created when the class (main) is instantiated. However, the endlog also captures the number of API requests (both successful and failed) and total requested calculation into the log file. Another important method of this method is to export the results into the requested format. The data is generally stored in a data frame 'outputDF' and exported into a specific format requested by the user. If totalcalculation is not used, the user must explicitly assign it to the variable 'outputDFType'; else, the data frame shall be exported as csv.

Note: The data frame 'outputDF' is an empty data frame and does not record calculations if totalcalculation is not used. The users are free to use this variable to append necessary information. 
1. ## generateCF:
A straightforward method to generate the characterization factors in a specified format. It generates a file with the entire database that also contain the characterization factors.

**Arguments:**

- **exportType:** Available file export types are 'csv', 'excel', 'json'.
- **orient:** The orientation type for json. [*(json documentation)*](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html)
  1. ## Support methods (select and execute)
The databases are stored as sqlite3 database files within the module. They are copied to the document folder for easy access and the user preference database. Generally, access to the database is by using SQL. To avoid redundancy, these methods come in handy.

Note: These methods shall be depreciated in the following versions.
1. # Global Variables
   1. ## \_\_init\_\_:
The main module instance newclassinstance creates a logging file and sets the basic configuration of the logging file, resets the API request counters and creates an empty data frame to store the results and the export type. 

The calculation module requires non-variable data such as the hs codes, country names, corresponding iso codes, etc. These data are read to the script when the package is imported.
1. ## Variables
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

1. # Example Code



1. # ANNEXE
   1. ## Available Resources and the corresponding HS code used LINK Excel.Sheet.12 D:\\Projects\\GeoPolRisk\\lib\\OldRecords\\metalsg.xlsx metalsg!R1C1:R32C2 \a \f 5 \h  \\* MERGEFORMAT 

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

1. ## Country ISO codes
ISO CODES: https://www.iso.org/standard/63546.html
