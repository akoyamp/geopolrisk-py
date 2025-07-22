import unittest
from geopolrisk.assessment.core import HHI, importrisk, importrisk_company, GeoPolRisk
from geopolrisk.assessment.utils import mapped_baci

mapped_baci = mapped_baci()
# execute this test from the root-folder by "python -m unittest geopolrisk/tests/test_core.py"


class TestCoreModul(unittest.TestCase):

    def test_HHI_valid_input(self):
        """Test HHI function with valid inputs to ensure it returns correct values."""
        resource = "Iron"
        year = 2020
        country = "China"
        ProdQty, hhi = HHI(resource, year, country)

        # Check if production quantity and HHI are floats
        self.assertIsInstance(ProdQty, float)
        self.assertIsInstance(hhi, float)

        # Check if HHI is normalized between 0 and 1
        self.assertGreaterEqual(hhi, 0)
        self.assertLessEqual(hhi, 1)

    def test_HHI_invalid_country(self):
        """Test HHI function with an invalid country to ensure it raises ValueError."""
        resource = "Iron"
        year = 2020
        country = "No Production Country"
        with self.assertRaises(ValueError):
            HHI(resource, year, country)

    def test_importrisk_valid_input(self):
        """Test importrisk function with valid inputs to ensure it returns correct values."""
        resource = "Rare earth"
        year = 2020
        country = "China"
        numerator, total_trade, price = importrisk(
            resource, year, country, data=mapped_baci
        )

        # Check if numerator, total trade, and price are floats
        self.assertIsInstance(numerator, float)
        self.assertIsInstance(total_trade, float)
        self.assertIsInstance(price, float)

        # Check if total trade is greater than zero
        self.assertGreater(total_trade, 0.0)

    def test_importrisk_invalid_country(self):
        """Test importrisk function with an invalid country to ensure it raises ValueError."""
        resource = "260400"
        year = 2022
        country = ["Invalid Country"]
        with self.assertRaises(ValueError):
            importrisk(resource, year, country, data=mapped_baci)

    def test_GeoPolRisk_valid_input(self):
        """Test GeoPolRisk function with valid inputs to ensure it returns correct values."""
        numerator = 1000.0
        total_trade = 2000.0
        price = 50.0
        prod_qty = 500.0
        hhi = 0.3
        score, cf, wta = GeoPolRisk(numerator, total_trade, price, prod_qty, hhi)

        # Check if score, characterization factor, and WTA are floats
        self.assertIsInstance(score, float)
        self.assertIsInstance(cf, float)
        self.assertIsInstance(wta, float)

        # Check if score is calculated correctly
        self.assertAlmostEqual(score, hhi * (numerator / (total_trade + prod_qty)))

    def test_GeoPolRisk_negative_values(self):
        """Test GeoPolRisk function with negative values to ensure it handles them appropriately."""
        numerator = -1000.0
        total_trade = 2000.0
        price = 50.0
        prod_qty = 500.0
        hhi = 0.3
        score, cf, wta = GeoPolRisk(numerator, total_trade, price, prod_qty, hhi)

        # Check if score is negative
        self.assertLess(score, 0)


if __name__ == "__main__":
    unittest.main()
