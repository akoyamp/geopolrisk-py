
import __init__
from assessment.main import main
import time
from .defaults import *
from assessment.utils import convertCodes, create_id
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
        main(Resources, Year, Countries, recyclingrate=Recycling, scenario=RecyclingScenario)
    except Exception as e:
        print(e)
        assert False


def test_2():
    X, Y = 'Magnesite', ['Norway', 'Greece', 'Slovakia', 'Bangladesh', 'European Union']
    Resources = random_sampler(ListofMetals, 5)
    Countries = random_sampler(ListofCountries, 5)
    A, B, C, D = convertCodes(X, Y)
    print(A, B, C, D)

def test_3():
    Resources = random_sampler(ListofMetals, 5)
    Countries = random_sampler(ListofCountries, 5)
    Year = random_sampler(ListofYears, 5)
    for i,n in enumerate(Resources):
        print(create_id(Resources[i],Countries[i], Year[i]))