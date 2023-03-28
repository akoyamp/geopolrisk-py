# Copyright (C) 2023 University of Bordeaux, CyVi Group & Anish Koyamparambath
# This file is part of geopolrisk-py library.
#
# geopolrisk-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# geopolrisk-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with geopolrisk-py.  If not, see <https://www.gnu.org/licenses/>.

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
