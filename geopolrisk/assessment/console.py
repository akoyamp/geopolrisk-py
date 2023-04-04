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

import pandas as pd, json, sqlite3
import comtradeapicall as ctac
from urllib.request import Request, urlopen
from .__init__ import instance, logging, execute_query
from .main import main_complete as gprs_comtrade
from .utils import convertCodes


# Define Paths
tradepath = None
_production, _reporter = instance.production, instance.reporter
regionslist, _outputfile = instance.regionslist, instance.exportfile
_price = instance.price
db = _outputfile + "/" + instance.Output
# Extract list of all data
HS = _price.HS.to_list()
HS = [int(float(x)) for x in HS]
Resource = _price.Resource.to_list()
Country = _reporter.Country.to_list()
ISO = _reporter.ISO.to_list()
ISO = [int(x) for x in ISO]


# from .Exceptions.warningsgprs import *
import itertools, sqlite3, pandas as pd, sys
from difflib import get_close_matches


"""
A simple guided step by step method for new users. This method can be called 
to any console based application if needed.
"""


def matchwords(word, List):
    word = word.lower()
    List = [x.lower() for x in List]
    if word in List:
        index = List.index(word)
        return index
    else:
        return -1


def getthequestions(compareList, *args):
    A = args[0]
    B = args[1]
    print(A)
    _exit = True
    finalvalue = False
    while _exit:
        inputvalue = input("Enter the value: ")
        comparelist = list(map(lambda x: x.lower(), compareList))
        closevalues = get_close_matches(inputvalue.lower(), comparelist)
        cl_index = matchwords(inputvalue, comparelist)
        if cl_index > -1:
            finalvalue = compareList[cl_index]
            _exit = False
        elif inputvalue.lower() == "exit":
            sys.exit(1)
        elif len(closevalues) == 1:
            cl_index = matchwords(closevalues[0], comparelist)
            if cl_index > -1:
                finalvalue = compareList[cl_index]
                _exit = False
            else:
                print("Please try again.")
        elif len(closevalues) > 1:
            print("Input did not match exactly a value in our list.")
            print("Is the value you intented in the list below?")
            print(closevalues)
            print("If yes, input the position of the value as 1 ,2 ,3,...")
            print("If not, type 'no'.")
            ni_value = input("Inpute the position : ")
            try:
                ni_value = int(ni_value) - 1
                _exit = False
            except:
                _exit = True
                break

            cl_index = matchwords(closevalues[ni_value], comparelist)
            if cl_index > -1:
                finalvalue = compareList[cl_index]
                _exit = False
            else:
                print("")
                _exit = True
                break
        else:
            print(B)

    return finalvalue


def guided():
    start = True
    intro = """
    Welcome to the geopolrisk-py guided assessment. Using this function, a user can
    assess the supply risk of importing a resource to a country. Questions are asked
    at each step of the assessment to which the user must type the response. At any 
    given point, the user can exit the assessment by typing 'exit'. The results of 
    the assessment are downloaded to the output folder.
    """
    print(intro)
    logging.info("Assessment type: Guided")
    while start:
        A = "Enter the name of the resource : "
        B = "The entered resource is not found! Please try again."
        resource = [
            getthequestions(Resource, A, B),
        ]
        logging.debug("Guided Assessment| Input Resource: {}".format(resource))
        A = "Enter the name of the country of asssessment : "
        B = "The entered country is not found! Please try again."
        country = [
            getthequestions(Country, A, B),
        ]
        logging.debug("Guided Assessment| Input Country: {}".format(country))
        _exit = True
        while _exit:
            period = input("Enter the year of assessment :")
            try:
                if int(period) in range(2000, 2020):
                    period = int(period)
                    logging.debug("Guided Assessment| Input Year: {}".format(period))
                    _exit = False
                else:
                    print("Provide enter an year between 2000 and 2020")
                    _exit = True
            except Exception as e:
                logging.debug(e)
                if period.lower() == "exit":
                    sys.exit()
                break

        _exit = True
        while _exit:
            print(
                "Enter the rate of domestic recycling input of the raw material (in fractions) or type exit to exit"
            )
            recyclingrate = input("Enter the recycling input rate: ")
            try:
                if float(recyclingrate) in range(0, 101):
                    recyclingrate = float(recyclingrate) / 100
                    logging.debug(
                        "Guided Assessment| Input Recycling Rate: {}".format(
                            recyclingrate
                        )
                    )
                    _exit = False
                else:
                    print("Provide enter a value between 0 to 100.")
                    _exit = True
            except Exception as e:
                logging.debug(e)
                if recyclingrate.lower() == "exit":
                    sys.exit()
                break

        _exit = True
        while _exit:
            print("Select 0 for no recycling scenario (recyclingrate is set to zero)")
            print(
                "Select 0 for assuming a best case scenario where the imports from a riskier country is reduced"
            )
            print(
                "Select 1 for assuming a worst case scenario where the imports from a stable country is reduced"
            )
            scenario = input("Select 1 or 0: ")
            try:
                if int(scenario) in [0, 1]:
                    scenario = int(scenario)
                    logging.debug(
                        "Guided Assessment| Input Scenario: {}".format(scenario)
                    )
                    _exit = False
                else:
                    print("Provide enter either 0 or 1.")
                    _exit = True
            except Exception as e:
                logging.debug(e)
                if scenario.lower() == "exit":
                    sys.exit()
                break
        _ignore, _ignore2, resource, country = convertCodes(resource, country)
        regions()
        gprs_comtrade(resource, [period], country, recyclingrate, scenario)
        endmain()

        print("Assessment completed! The results are downloaded to the output folder")
        print("In case of error in the output file, refer to logs.")
