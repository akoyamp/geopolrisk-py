import unittest

# from tests.test_prod import Testprodfunctions
# from tests.test_trade import Testtradefunctions
from tests.test_inputs import TestDataClass

if __name__ == "__main__":
    # ProdTest = unittest.TestLoader().loadTestsFromTestCase(Testprodfunctions)
    # unittest.TextTestRunner(verbosity=3).run(ProdTest)
    # Tradetest = unittest.TestLoader().loadTestsFromTestCase(Testtradefunctions)
    # unittest.TextTestRunner(verbosity=3).run(Tradetest)
    Datatest = unittest.TestLoader().loadTestsFromTestCase(TestDataClass)
    unittest.TextTestRunner(verbosity=3).run(Datatest)
