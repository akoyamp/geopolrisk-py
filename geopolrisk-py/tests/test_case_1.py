
import __init__
from assessment.operations import gprs_comtrade
import time
from .defaults import *

#testcase to test the gprs_comtrade function
"""
The following test case will test the gprs_comtrade function using
random sampled data from the list provided in the defaults module.
The following tests will test the robustness of the gprs_comtrade function
and determine the correctness of the results.
"""

#test for input validation and correctness
def test_1():
    Resources = random_sampler(ListofMetals, 5)
    Countries = random_sampler(ListofCountries, 5)
    Year = random_sampler(ListofYears, 5)

    #Setting the recycling value 0
    Recycling = 0
    RecyclingScenario = 0

    try:
        gprs_comtrade(Resources, Countries, Year, Recycling, RecyclingScenario)
    except Exception as e:
        print(e)
        assert False


