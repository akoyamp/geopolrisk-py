import unittest, os
from tests.test_case_1 import Testutilsfunctions
from tests.test_case_2 import TestCoreFunctions
from tests.test_case_3 import Testmainfunctions


if __name__ == '__main__':

    #Test Suite
    suite = unittest.TestSuite()

    #Add all test cases to the test suite
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Testutilsfunctions))
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCoreFunctions))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Testmainfunctions))

    #Run the test suite
    unittest.TextTestRunner(verbosity=3).run(suite)
