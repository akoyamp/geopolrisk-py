import unittest
from .defaults import *
from assessment.core import regions
from assessment.main import startmain, endmain, main_complete
from assessment.__init__ import instance

_wgi = instance.wgi
# testcase to test the gprs_comtrade function
Resources = random_sampler(ListofMetals, 2)
Countries = random_sampler(ListofCountries, 2)
Year = random_sampler(ListofYears, 2)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(ListofMetalName[ListofMetals.index(n)])

class Testmainfunctions(unittest.TestCase):
    def test_aggregion(self):
        NewRegion = {"Custom Region" : listofcountryname }
        xx = regions(NewRegion)
        try:
            main_complete(Resources,Year,["Custom Region"],0,0,None,_wgi)
            assert True
        except Exception as e:
            print(e)
            assert False

    def test_mainfunction(self):
        try:
            startmain(
            Resources,
            Year,
            Countries,
            recyclingrate=0.0,
            scenario=0,
            sheetname=None,
            PIindicator=None,
            )
            endmain()
        except Exception as e:
            print(e)
            assert False
