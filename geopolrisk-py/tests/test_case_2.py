import unittest
from .defaults import *
from assessment.utils import *
from assessment.core import *

# testcase to test the gprs_comtrade function
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(
        ListofMetalName[ListofMetals.index(n)]
    )

class TestCoreFunctions(unittest.TestCase):
    def test_regioninsertion(self):
        NewRegion = {"West Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "Belgium"]}
        result = regions(NewRegion)
        from assessment.__init__ import instance
        regionslist = instance.regionslist
        self.assertEqual(regionslist["West Europe"], NewRegion["West Europe"], msg="Region insertion failed")
        self.assertIsNotNone(result, msg="Error in region creation!" )
    
    def test_tradepathinsertion(self):
        result = settradepath("C:/Users/akoyamparamb/Documents/GitHub/geopolrisk/geopolrisk-py/tests/comtrade.xlsx")
        self.assertIsNotNone(result, msg="Error in tradepath creation!")

    def test_worldtrade(self):
        regions()
        randomresource = random.choice(Resources)
        randomcountry = random.choice(Countries)
        randomyear = random.choice(Year)
        result = worldtrade(randomyear,randomcountry,randomresource)
        self.assertIsNotNone(result, msg="Error in worldtrade calculation!")

    def test_specifictrade(self):
        result = settradepath("C:/Users/akoyamparamb/Documents/GitHub/geopolrisk/geopolrisk-py/tests/comtrade.xlsx")
        result = specifictrade(sheetname="test")
        self.assertIsNotNone(result, msg="Error in specific trade calculation!")
    
    def test_productiondata(self):
        regions()
        randomresource = random.choice(listofresourcename)
        randomcountry = random.choice(listofcountryname)
        result = ProductionData(randomresource, randomcountry)
        self.assertIsNotNone(result, msg="Error in production data calculation!")

    def test_weightedaverage(self):
        pass