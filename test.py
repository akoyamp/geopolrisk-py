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
from geopolrisk.tests.test_case_1 import Testutilsfunctions

# from geopolrisk.tests.test_case_2 import TestCoreFunctions
# from geopolrisk.tests.test_case_3 import Testmainfunctions


def main():

    # Test Suite
    suite = unittest.TestSuite()

    # Add all test cases to the test suite
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Testutilsfunctions))
    # testsuite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCoreFunctions))
    # suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Testmainfunctions))

    # Run the test suite
    unittest.TextTestRunner(verbosity=3).run(suite)


if __name__ == "__main__":
    main()
