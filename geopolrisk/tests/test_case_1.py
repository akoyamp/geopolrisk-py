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

# testcase to test the gprs_comtrade function

# Extracting samples data from a list of resources, countries and years
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(ListofMetalName[ListofMetals.index(n)])


# Test class to test the functions in utils module
# Please note functions such as record data, extract data are excluded
class Testutilsfunctions(unittest.TestCase):

    # Test to verify the functionality of id creation
    def test_verifyidcreation(self):
        Resources = [2606, 261710, 2524]
        Countries = [4, 36, 124]
        Year = [2016]
        result = [
            "260642016",
            "2606362016",
            "26061242016",
            "26171042016",
            "261710362016",
            "2617101242016",
            "252442016",
            "2524362016",
            "25241242016",
        ]
        for i, n in enumerate(Resources):
            get = create_id(Resources[i], Countries[i], Year[0])
            self.assertIn(get, result, msg="Id creation failed!")

    # Test to verify the results dataframe creation
    def test_create_results_df(self):
        df = createresultsdf()
        self.assertIsInstance(
            df, pd.DataFrame, msg="Results dataframe creation failed!"
        )
        self.assertEqual(
            len(df.columns), 9, msg="Results dataframe has incorrect number of columns"
        )

    # Test to verify the BACI data retrieval
    def test_get_baci_data(self):
        sample_data = pd.DataFrame(
            {
                "period": ["2016"],
                "reporterCode": ["4"],
                "cmdCode": ["2606"],
                "qty": ["1000"],
                "cifvalue": ["500"],
            }
        )
        ksample_data = getbacidata(2016, 4, 2606, sample_data)
        self.assertIsInstance(
            ksample_data, pd.DataFrame, msg="BACI data retrieval failed!"
        )
        self.assertEqual(
            ksample_data["qty"].iloc[0], 1000.0, msg="Quantity conversion failed!"
        )
        self.assertEqual(
            ksample_data["cifvalue"].iloc[0], 500.0, msg="CIF value conversion failed!"
        )
        baci_data = getbacidata(2016, 4, 260600)
        self.assertIsInstance(
            baci_data, pd.DataFrame, msg="BACI data retrieval failed!"
        )

    # Test to verify the sql verify function to check for existing data
    def test_verifydatabase(self):
        DBID = ["xx81061912014", "xx81077052003", "xx2846x562012", "2615102032017"]
        for i in DBID:
            result = sqlverify(i)
            self.assertTrue(result, msg="SQL verification failed!")

    # Test to verify the production data retrieval
    def test_get_prod(self):
        resource = "Graphite"
        prod_data = getProd(resource)
        self.assertIsInstance(
            prod_data, pd.DataFrame, msg="Production data retrieval failed!"
        )

    # Test to verify the region creation
    def test_regions_creation(self):
        region_dict = {
            "RegionX": Countries,
            "RegionY": ["Bulgaria", "Croatia", "Czechia", "Czechoslovakia"],
        }
        created_regions = regions(region_dict)
        self.assertIsInstance(created_regions, dict, msg="Region creation failed!")
        self.assertIn(
            "RegionX", created_regions, msg="Region creation did not include Region1"
        )
        self.assertIn(
            "RegionY", created_regions, msg="Region creation did not include Region2"
        )
