import unittest
from tests.test_case_1 import Testutilsfunctions
from tests.test_case_2 import TestCoreFunctions
from tests.test_case_3 import Testmainfunctions

if __name__ == '__main__':
    coretest = unittest.TestLoader().loadTestsFromTestCase(Testmainfunctions)
    unittest.TextTestRunner(verbosity=3).run(coretest)