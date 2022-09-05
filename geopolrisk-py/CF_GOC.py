# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 10:10:17 2022
@author: akoyamparamb
Save this file in the geopolrisk-py folder.
"""

#Step 1: Import the geopolrisk-py library or import the module
from assessment.core import regions #Regions is a function in the core module that is used to declare the new regions.
from assessment.operations import gprs_regional #gprs_regional is an aggregate function to calculate GPRS values for countries including regions.

#Step 2: Define new region
"""
Create a python dictionary with the new region name as its key and a list of 
countries in the region in their ISO nomenclature or ISO numeric format. 
Refer to https://unstats.un.org/wiki/display/comtrade/Comtrade+Country+Code+and+Name
"""
NewRegion = {"G7" : [124, 251, 276, 381, 392, 826, 842]}
#NewRegion = {"G7" : ["Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "USA"]}

#Step 3: Create list of resources, period, countries
ListofResources = [810520, 2603] #Visit https://github.com/akoyamp/geopolrisk-py for HS codes of resources

ListofCountries = [36, 124, "G7"] #Use ISO Numeric code. Downloadable from https://unstats.un.org/wiki/display/comtrade/Comtrade+Country+Code+and+Name

ListofYear = [2010, 2011] #List of all the years for assessment


#Step 4: Call the regions
regions(NewRegion)

#Step 5: Call the gprs_regional function to calcualte for countries including G7 group
gprs_regional(ListofResources, ListofCountries, ListofYear, 0, 0) #The 0, 0 are values for recycling rate and recycling scenario