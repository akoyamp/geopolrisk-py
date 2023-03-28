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

import unittest, os
from .defaults import *
from geopolrisk.assessment.utils import *
from geopolrisk.assessment.core import *
from geopolrisk.assessment.__init__ import instance

_wgi = instance.wgi
# testcase to test the gprs_comtrade function
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(ListofMetalName[ListofMetals.index(n)])


class TestCoreFunctions(unittest.TestCase):
    def test_regioninsertion(self):
        NewRegion = {
            "West Europe": [
                "France",
                "Germany",
                "Italy",
                "Spain",
                "Portugal",
                "Belgium",
            ]
        }
        result = regions(NewRegion)
        from geopolrisk.assessment.__init__ import instance

        regionslist = instance.regionslist
        self.assertEqual(
            regionslist["West Europe"],
            NewRegion["West Europe"],
            msg="Region insertion failed",
        )
        self.assertIsNotNone(result, msg="Error in region creation!")

    def test_tradepathinsertion(self):
        result = settradepath("geopolrisk/tests/sample trade data.xlsx")
        self.assertIsNotNone(result, msg="Error in tradepath creation!")

    def test_worldtrade(self):
        regions()
        randomresource = random.choice(Resources)
        randomcountry = random.choice(Countries)
        randomyear = random.choice(Year)
        result = worldtrade(randomyear, randomcountry, randomresource)
        self.assertIsNotNone(result, msg="Error in worldtrade calculation!")

    def test_specifictrade(self):
        xxx = settradepath("geopolrisk/tests/sample trade data.xlsx")
        result = specifictrade(sheetname="test")
        self.assertIsNotNone(result, msg="Error in specific trade calculation!")

    def test_productiondata(self):
        regions()
        randomresource = random.choice(listofresourcename)
        randomcountry = random.choice(listofcountryname)
        result = ProductionData(randomresource, randomcountry)
        self.assertIsNotNone(result, msg="Error in production data calculation!")

    def test_weightedaverage(self):
        TradeData = [
            [
                40,
                56,
                76,
            ],
            [
                "Austria",
                "Belgium",
                "Brazil",
            ],
            [
                1723782,
                2155207,
                53399700,
            ],
        ]
        PIData = _wgi
        Year = "2015"
        recyclingrate = 0
        scenario = 0
        numerator, tradetotal = weightedtrade(
            Year,
            TradeData=TradeData,
            PIData=PIData,
            scenario=scenario,
            recyclingrate=recyclingrate,
        )
        res_num, res_total = [31532151.035755564, 57278689]
        self.assertEqual(
            [numerator, tradetotal],
            [res_num, res_total],
            msg="Weighted average calculation failed!",
        )
        self.assertIsNotNone(numerator, msg="Weighted average calculation failed!")

    def test_GeoPolRisk(self):
        ProductionData = [
            [   0.289,
                0.304,
                0.287,
                0.258,
                0.213,
                0.222,
                0.218,
            ],
            [   23659.0,
                25000.0,
                25000.0,
                21000.0,
                20000.0,
                20000.0,
                20000.0,
            ],
            [   2014,
                2015,
                2016,
                2017,
                2018,
                2019,
                2020,
            ],
        ]
        WTAData = [31532151.035755564, 57278689]
        Year = "2015"
        AVGPrice = 2010.22
        result = GeoPolRisk(ProductionData, WTAData, Year, AVGPrice)
        theresult = [0.304, 0.3832359438269072, 0.11650372692337978, 234.1981219359165]
        self.assertEqual(result, theresult, msg = "The GeoPolRisk calculation failed!")

    def test_redistribution(self):
        TradeData = [
            [
                40,
                56,
                76,
            ],
            [
                "Austria",
                "Belgium",
                "Brazil",
            ],
            [
                1723782,
                2155207,
                53399700,
            ],
        ]
        PIData = _wgi
        Year = "2015"
        recyclingrate = 10
        scenario = 1
        numerator, tradetotal = weightedtrade(
            Year,
            TradeData=TradeData,
            PIData=PIData,
            scenario=scenario,
            recyclingrate=recyclingrate,
        )
        res_num, res_total = [31532151.035755564, 57278689]
        self.assertLessEqual(
            numerator,
            res_num,
            msg="Weighted average calculation failed!"
        )
        self.assertIsNotNone(numerator, msg="Weighted average calculation failed!")
