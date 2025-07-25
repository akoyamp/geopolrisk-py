import unittest
import pandas as pd
import copy

# from geopolrisk.assessment.utils import replace_func, cvtresource, cvtcountry, sumproduct, createresultsdf, create_id
from geopolrisk.assessment.utils import *

# from geopolrisk.assessment.utils import databases
from defaults import *

# execute this test from the root-folder by "python -m unittest geopolrisk/tests/test_util.py"

# Extracting samples data from a list of resources, countries and years
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(ListofMetalName[ListofMetals.index(n)])


class TestUtilModul(unittest.TestCase):

    def setUp(self):
        # Deep copy to preserve all original nested data (e.g., DataFrames)
        self._original_production = copy.deepcopy(databases.production)
        self._original_regionslist = copy.deepcopy(databases.regionslist)

    def tearDown(self):
        # Restore the original state
        databases.production = self._original_production
        databases.regionslist = self._original_regionslist

    def test_replace_func(self):
        """Test the replace_func utility function."""
        self.assertEqual(replace_func(1.0), 1.0)  # Float input returns unchanged
        self.assertEqual(replace_func("NA"), 0)  # "NA" string input returns 0
        self.assertEqual(replace_func(None), 0)  # None input returns 0
        self.assertEqual(replace_func(" "), 0)  # Whitespace string input returns 0

    def test_cvtcountry(self):
        """Test the cvtcountry utility function."""
        self.assertEqual(
            cvtcountry(276, type="Name"), "Germany"
        )  # Existing ISO code returns mapped value
        self.assertEqual(cvtcountry("Germany"), 276)  # Existing name returns mapped ISO
        with self.assertRaises(ValueError):
            cvtcountry("ABC")  # Non-existent ISO code raises ValueError
        with self.assertRaises(ValueError):
            cvtcountry("ABC", type="Name")  # Non-existent name raises ValueError

    def test_sumproduct(self):
        """Test the sumproduct utility function."""
        A = [1, 2, 3]
        B = [4, 5, 6]
        self.assertEqual(sumproduct(A, B), 32)  # Correct dot product calculation

    def test_create_id(self):
        """Test the create_id utility function."""
        HS = 260400
        ISO = 276
        Year = 2022
        self.assertEqual(create_id(HS, ISO, Year), "2604002762022")

    def test_createresultsdf(self):
        """Test the createresultsdf utility function."""

        databases.Output = "output.db"

        df = createresultsdf()

        self.assertIsInstance(df, pd.DataFrame)  # Returns a DataFrame
        expected_columns = [
            "DBID",
            "Country [Economic Entity]",
            "Raw Material",
            "Year",
            "GeoPolRisk Score",
            "GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]",
            "HHI",
            "Import Risk",
            "Price",
        ]
        self.assertListEqual(list(df.columns), expected_columns)

    def test_getbacidata(self):
        """Test the getbacidata utility function."""
        period = 2022
        country = 276
        commoditycode = "260400"

        # Mock the databases.baci_trade DataFrame
        mock_data = pd.DataFrame(
            {
                "period": [period],
                "reporterCode": [country],
                "cmdCode": [commoditycode],
                "qty": [1000],
                "cifvalue": [10000],
                "partnerWGI": [0.5],
                "rawMaterial": [commoditycode],
            }
        )

        baci_data = getbacidata(period, country, commoditycode, data=mock_data)

        self.assertIsInstance(baci_data, pd.DataFrame)
        self.assertEqual(baci_data["qty"].iloc[0], 1000)
        self.assertEqual(baci_data["cifvalue"].iloc[0], 10000)
        self.assertEqual(baci_data["partnerWGI"].iloc[0], 0.5)

    def test_aggregateTrade(self):
        """Test the aggregateTrade utility function."""
        period = 2022
        country = [276, 380]
        commoditycode = "Nickel"

        # Mock the databases.baci_trade DataFrame
        mock_data = pd.DataFrame(
            {
                "period": [period, period],
                "reporterCode": [country[0], country[1]],
                "cmdCode": [commoditycode, commoditycode],
                "qty": [1000, 2000],
                "cifvalue": [10000, 20000],
                "partnerWGI": [0.5, 0.6],
                "partnerCode": [4, 4],
                "rawMaterial": [commoditycode, commoditycode],
            }
        )

        sumnum, sumqty, price = aggregateTrade(
            period, country, commoditycode, data=mock_data
        )

        self.assertEqual(sumnum, 1700)
        self.assertEqual(sumqty, 3000)
        self.assertEqual(price, 10)

    def test_transformdata(self):
        """Test the transformdata utility function."""

        data = transformdata(mode="test")

        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 5)
        self.assertEqual(
            data["cmdCode"].tolist(), ["Nickel", "Nickel", "Nickel", "Nickel", "Nickel"]
        )
        self.assertEqual(data["partnerISO"].tolist(), [208, 528, 620, 818, 842])
        self.assertEqual(
            data["partnerWGI"].tolist(),
            [
                0.326998233795166,
                0.35653903484344485,
                0.32785606384277344,
                0.7056113243103027,
                0.5072010055184364,
            ],
        )

    def test_getProd(self):
        """Test the getProd utility function."""
        resource = "Nickel"

        # Mock the databases.production["HS Code Map"] DataFrame
        mock_map_df = pd.DataFrame(
            {
                "Sheet_name": ["Nickel"],
                "Reference ID": ["Nickel"],
                "HS Code": ["260400"],
            }
        )
        databases.production["HS Code Map"] = mock_map_df

        # Mock the databases.production[MappedTableName] DataFrame
        mock_prod_df = pd.DataFrame(
            {
                "Country": ["Germany"],
                "Country_Code": [276],
                "Country_ISO": ["DEU"],
                "2022": ["1000"],
            }
        )
        databases.production["Nickel"] = mock_prod_df

        prod_data = getProd(resource)

        self.assertIsInstance(prod_data, pd.DataFrame)
        self.assertEqual(prod_data["Country"].iloc[0], "Germany")
        self.assertEqual(prod_data["Country_Code"].iloc[0], 276)
        self.assertEqual(prod_data["Country_ISO"].iloc[0], "DEU")
        self.assertEqual(prod_data["2022"].iloc[0], "1000")

    def test_regions_creation(self):
        """Test to verify the region creation."""
        region_dict = {
            "RegionX": Countries,
            "RegionY": ["Bulgaria", "Croatia", "Czechia", "Czechoslovakia"],
        }
        regions(region_dict)
        self.assertIsInstance(
            databases.regionslist, dict, msg="Region creation failed!"
        )
        self.assertIn(
            "RegionX",
            databases.regionslist,
            msg="Region creation did not include RegionX",
        )
        self.assertIn(
            "RegionY",
            databases.regionslist,
            msg="Region creation did not include RegionY",
        )


if __name__ == "__main__":
    unittest.main()
