# Copyright 2020-2021 by Anish Koyamparambath and University of Bordeaux. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Anish Koyamparambath (AK) or 
# University of Bordeaux (UBx) will not be used in advertising or publicity pertaining 
# to distribution of the software without specific, written prior permission.
# BOTH AK AND UBx DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# BOTH AK AND UBx BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from .__init__ import (
    _reporter,
    SQL,
    _price,
    _outputfile,
    _wgi,
    outputDF,
    regionslist,
    logging,
    Filename)



from .operations import convertCodes, gprs_comtrade 

#from .Exceptions.warningsgprs import *
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
                ni_value = int(ni_value)-1
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
        Resource = _price.id.to_list()
        A = "Enter the name of the resource : "
        B = "The entered resource is not found! Please try again."
        resource = [getthequestions(Resource, A, B),]
        logging.debug("Guided Assessment| Input Resource: {}".format(resource))
        Country = _reporter.Country.to_list()
        A = "Enter the name of the country of asssessment : "
        B = "The entered country is not found! Please try again."
        country = [getthequestions(Country, A, B),]
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
                if period.lower() == 'exit':
                    sys.exit()
                break
        
        _exit = True
        while _exit:
            print("Enter the rate of domestic recycling input of the raw material (in fractions) or type exit to exit")
            recyclingrate = input("Enter the recycling input rate: ")
            try:
                if float(recyclingrate) in range(0,101):
                    recyclingrate = float(recyclingrate)/100
                    logging.debug("Guided Assessment| Input Recycling Rate: {}".format(recyclingrate))
                    _exit = False
                else:
                    print("Provide enter a value between 0 to 100.")
                    _exit = True
            except Exception as e:
                logging.debug(e)
                if recyclingrate.lower() == 'exit':
                    sys.exit()
                break
                
        _exit=True
        while _exit:
            print("Select 0 for no recycling scenario (recyclingrate is set to zero)")
            print("Select 0 for assuming a best case scenario where the imports from a riskier country is reduced")
            print("Select 1 for assuming a worst case scenario where the imports from a stable country is reduced")
            scenario = input("Select 1 or 0: ")
            try:
                if int(scenario) in [0, 1]:
                    scenario = int(scenario)
                    logging.debug("Guided Assessment| Input Scenario: {}".format(scenario))
                    _exit = False
                else:
                    print("Provide enter either 0 or 1.")
                    _exit = True
            except Exception as e:
                logging.debug(e)
                if scenario.lower() == 'exit':
                    sys.exit()
                break
        resource, country = convertCodes(resource, country, 1)
        gprs_comtrade(resource, country, [period], recyclingrate, scenario)
        
        print("Assessment completed! The results are downloaded to the output folder")
        print("In case of error in the output file, refer to logs.")



