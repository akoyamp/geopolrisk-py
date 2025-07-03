import unittest
from geopolrisk.assessment.main import gprs_calc
from geopolrisk.assessment.utils import databases

# execute this test from the root-folder by "python -m unittest geopolrisk/tests/test_main.py"


class TestMainModul(unittest.TestCase):

    def setUp(self):
        """Set up test variables for the test cases."""
        self.period = [2018, 2019, 2020]
        # self.country = ['Japan', 'Canada']
        self.country = [
            36,
            124,
            251,
            276,
            392,
            826,
            842,
        ]
        # self.resource = ['Cobalt', 'Lithium']
        self.resource = [
            "Nickel",
            "Chromite",
            "Copper",
            "Lithium",
            "Cobalt",
        ]

        self.region_dict = {
            "West Europe": [
                "France",
                "Germany",
                "Italy",
                "Spain",
                "Portugal",
                "Belgium",
                "Netherlands",
                "Luxembourg",
            ]
        }

    def test_gprs_calc_non_regional(self):
        """Test gprs_calc function for non-regional assessment."""
        # Assuming databases.regional is False
        databases.regional = False
        result = gprs_calc(self.period, self.country, self.resource)

        # Check if the result is a DataFrame and has the expected columns
        self.assertIsNotNone(result)
        self.assertIn("DBID", result.columns)
        self.assertIn("Country [Economic Entity]", result.columns)
        self.assertIn("Raw Material", result.columns)
        self.assertIn("Year", result.columns)
        self.assertIn("GeoPolRisk Score", result.columns)
        self.assertIn(
            "GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]", result.columns
        )
        self.assertIn("HHI", result.columns)
        self.assertIn("Import Risk", result.columns)
        self.assertIn("Price", result.columns)
        # TODO - add checks for right calculations

    def test_gprs_calc_regional(self):
        """Test gprs_calc function for regional assessment."""
        # Assuming databases.regional is True
        databases.regional = True
        result = gprs_calc(self.period, self.country, self.resource, self.region_dict)
        databases.regional = False

        # Check if the result is a DataFrame and has the expected columns
        self.assertIsNotNone(result)
        self.assertIn("DBID", result.columns)
        self.assertIn("Country [Economic Entity]", result.columns)
        self.assertIn("Raw Material", result.columns)
        self.assertIn("Year", result.columns)
        self.assertIn("GeoPolRisk Score", result.columns)
        self.assertIn(
            "GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]", result.columns
        )
        self.assertIn("HHI", result.columns)
        self.assertIn("Import Risk", result.columns)
        self.assertIn("Price", result.columns)
        # TODO - add checks for right calculations

    def test_empty_resource(self):
        """Test gprs_calc function with an empty resource list."""
        result = gprs_calc(self.period, self.country, [])
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)  # Expecting no results


if __name__ == "__main__":
    unittest.main()
