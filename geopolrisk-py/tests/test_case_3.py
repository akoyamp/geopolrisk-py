import unittest
from .defaults import *
from assessment.core import regions
from assessment.main import main
from assessment.__init__ import instance

_wgi = instance.wgi
# testcase to test the gprs_comtrade function
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(ListofMetalName[ListofMetals.index(n)])

class Testmainfunctions(unittest.TestCase):
    def test_aggregion(self):
        NewRegion = {"Custom Region" : listofcountryname }
        xx = regions(NewRegion)
        try:
            main(Resources,Year,["Custom Region"],0,0,None,_wgi)
            assert True
        except:
            assert False        