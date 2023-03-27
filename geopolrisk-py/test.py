import unittest
from tests.test_case_1 import Testutilsfunctions
from tests.test_case_2 import TestCoreFunctions

if __name__ == '__main__':
    

    coretest = unittest.TestLoader().loadTestsFromTestCase(TestCoreFunctions)
    unittest.TextTestRunner(verbosity=3).run(coretest)

