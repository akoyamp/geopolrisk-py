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

import unittest, sys
from pathlib import Path

# Ensure /src is in sys.path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Import test modules
from test_database import TestDatabaseModule
from test_util import TestUtilModul
from test_main import TestMainModul
from test_core import TestCoreModul
from test_geopolrisk_data_results_from_excelfile import (
    TestGeoPolRiskPy,
)


def main():

    # Test Suite
    suite = unittest.TestSuite()

    # Add all test cases to the test suite
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCoreModul))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseModule))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMainModul))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestUtilModul))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestGeoPolRiskPy))

    # Run the test suite
    unittest.TextTestRunner(verbosity=3).run(suite)


if __name__ == "__main__":
    main()
