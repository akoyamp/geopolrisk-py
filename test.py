import unittest, os
from geopolrisk.tests.test_case_utils import TestGeoPolRisk


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestGeoPolRisk))
    unittest.TextTestRunner(verbosity=3).run(suite)


if __name__ == "__main__":
    main()
