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
from geopolrisk.assessment.utils import *
from geopolrisk.assessment.core import *

# testcase to test the gprs_comtrade function

#Extracting samples data from a list of resources, countries and years
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(
        ListofMetalName[ListofMetals.index(n)]
    )


#Test class to test the functions in utils module
#Please note functions such as record data, extract data are excluded
class Testutilsfunctions(unittest.TestCase):
     
    #Test to verify the functionality of id creation 
    def test_verifyidcreation(self):
        Resources = [2606, 261710, 2524]
        Countries = [4, 36, 124]
        Year = [2016]
        result = [
            "xx2606xx42016",
            "xx2606x362016",
            "xx26061242016",
            "261710xx42016",
            "261710x362016",
            "2617101242016",
            "xx2524xx42016",
            "xx2524x362016",
            "xx25241242016",
        ]
        for i, n in enumerate(Resources):
            get = create_id(Resources[i], Countries[i], Year[0])
            self.assertIn(get, result, msg="Id creation failed!")

    #Test to verify the conversion of the codes
    def test_conversiontonumericcodes(self):
        __ignore, __ignore, hscode, iso = convertCodes(
            listofresourcename, listofcountryname
        )
        self.assertEqual(
            [hscode, iso],
            [Resources, Countries],
            msg="Code conversion failed!",
        )

    #Test to verify the reverse conversion of the codes
    def test_conversiontonames(self):
        resourcename, countryname, __ignore, __ignore = convertCodes(
            listofresourcename, listofcountryname
        )
        self.assertEqual(
            [resourcename, countryname],
            [listofresourcename, listofcountryname],
            msg="Code conversion failed!",
        )

    #Test to verify the functionality of the new Comtrade API
    def test_pythoncomtradeapi(self):
        randomresource = random.choice(Resources)
        randomcountry = random.choice(Countries)
        randomyear = random.choice(Year)
        TradeData, cifprice = callapirequest(randomyear, randomcountry, randomresource)
        self.assertIsNotNone(TradeData, msg="API call failed!")
        self.assertIsNotNone(cifprice, msg="API call failed!")

    #Test to verify the functionality of the old Comtrade API
    def test_oldcomtradeapi(self):
        randomresource = random.choice(Resources)
        randomcountry = random.choice(Countries)
        randomyear = random.choice(Year)
        TradeData = oldapirequest(randomyear, randomcountry, randomresource)
        self.assertIsNotNone(TradeData, msg="API call failed!")

    #Test to verify the sql verify function to check for existing data
    def test_verifydatabase(self):
        DBID = ["xx81061912014", "xx81077052003", "xx2846x562012", "2615102032017"]
        for i in DBID:
            result =  sqlverify(i)
            self.assertTrue(result, msg="SQL verification failed!")
