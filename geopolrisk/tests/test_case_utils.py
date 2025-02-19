# Copyright (C) 2024 University of Bordeaux, CyVi Group & University of Bayreuth,
# Ecological Resource Technology & Anish Koyamparambath, Christoph Helbig, Thomas Schraml
# This file is part of geopolrisk-py library.
# geopolrisk-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# geopolrisk-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with geopolrisk-py.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from unittest.mock import patch
from .defaults import *
import pandas as pd
from geopolrisk.assessment.utils import (
    replace_func,
    cvtresource,
    cvtcountry,
    sumproduct,
    create_id,
    createresultsdf,
    writetodb,
    getbacidata,
    aggregateTrade,
    getProd,
    regions,
)

# Extracting samples data from a list of resources, countries and years
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(ListofMetalName[ListofMetals.index(n)])


class TestGeoPolRisk(unittest.TestCase):

    def test_cvtresource(self):
        self.assertEqual(cvtresource(listofresourcename[0], type="HS"), Resources[0])
        self.assertRaises(ValueError, cvtresource, "Unknown", type="HS")
        self.assertEqual(cvtresource(Resources[0], type="Name"), listofresourcename[0])
        self.assertRaises(ValueError, cvtresource, "Unknown", type="Name")

    def test_cvtcountry(self):
        self.assertEqual(cvtcountry(listofcountryname[0], type="ISO"), Countries[0])
        self.assertRaises(ValueError, cvtcountry, "Unknown", type="ISO")
        self.assertEqual(cvtcountry(Countries[0], type="Name"), listofcountryname[0])
        self.assertRaises(ValueError, cvtcountry, "Unknown", type="Name")

    def test_sumproduct(self):
        self.assertEqual(sumproduct([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(sumproduct([], []), 0)

    def test_create_id(self):
        self.assertEqual(create_id("1001", "FRA", "2022"), "1001FRA2022")

    @patch("geopolrisk.assessment.database.execute_query")
    @patch("geopolrisk.assessment.database.databases")
    def test_createresultsdf(self, mock_databases, mock_execute_query):
        mock_databases.directory = "/mock/path"
        mock_databases.Output = "mock_output.db"
        df = createresultsdf()
        self.assertTrue(isinstance(df, pd.DataFrame))

    @patch("geopolrisk.assessment.database.execute_query")
    @patch("geopolrisk.assessment.database.databases")
    def test_writetodb(self, mock_databases, mock_execute_query):
        mock_databases.directory = "/mock/path"
        mock_databases.Output = "mock_output.db"
        mock_df = pd.DataFrame(
            {
                "DBID": ["1"],
                "Country [Economic Entity]": ["France"],
                "Raw Material": ["Gold"],
                "Year": [2022],
                "GeoPolRisk Score": [1.5],
                "GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]": [0.8],
                "HHI": [0.5],
                "Import Risk": [0.3],
                "Price": [1000],
            }
        )
        writetodb(mock_df)
        mock_execute_query.assert_called()

    @patch("geopolrisk.assessment.database.databases")
    def test_getbacidata(self, mock_databases):
        mock_databases.baci_trade = pd.DataFrame(
            {
                "period": ["2022"],
                "reporterCode": ["FRA"],
                "cmdCode": ["1001"],
                "qty": [10],
                "cifvalue": [100],
            }
        )
        df = getbacidata("2022", "FRA", "1001", data=mock_databases.baci_trade)
        self.assertFalse(df.empty)


if __name__ == "__main__":
    unittest.main()
