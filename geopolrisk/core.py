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


#Imports
import pandas as pd, json
from urllib.request import Request, urlopen
from pathlib import Path
from .__init__ import (
    _production,
    _reporter,
    regionslist,
    logging)
from .Exceptions.warningsgprs import *
#Define Paths
tradepath = None

# This module contains methods (python functions) that provides access to different components and
# variables of the GeoPolRisk method. This is a functional module where methods 
# are designed for micromanaging the GeoPolRisk method. Refer to the scientific publication 
# available online for technical details.


# The GeoPolRisk method is designed to assess the geopolitical related supply risk
# of importing a resource from a macro economic perspective (country, regions, 
# trade blocs or group of countries) during a period. However, the method could be 
# adapted to analyse the supply risk at an organizational level. This requires 
# specific trade information in contrast to the macro economic perspective that uses 
# country trade data available that is accessed using the COMTRADE api.

# The specific trade data of the organization can be provided using a predefined
# excel or csv format. The location of the file is provided as an agrument to the
# 'settradepath' method below.


#Method 1
def settradepath(path):
    tradepath = path
    try:
        with open(tradepath) as openfile:
            pd.read_excel(openfile)
    except FileNotFoundError:
        tradepath = None
        raise FileNotFoundError
    except Exception as e:
        logging.debug(e)
        tradepath = None
        raise InputError
  

# In line with the earlier explanation of the scope of GeoPolRisk method, the 
# following methods creates a user defined scope (regions). By default, European
# Union (27 countries) is provided in the dictionary. A dictionary is provided
# as an argument with the name of the region/bloc is the key and the ISO names 
# of the countries as the values. The ISO names of the countries are available in
# the the reporters json file.


#Method 2
def regions(*args):
    regionslist['EU'] = ['Austria', 'Belgium', 'Belgium-Luxembourg', 'Bulgaria',
           'Croatia', 'Czechia', 'Czechoslovakia', 'Denmark', 
           'Estonia','Finland', 'France', 'Fmr Dem. Rep. of Germany',
           'Fmr Fed. Rep. of Germany', 'Germany', 'Greece', 'Hungary',
           'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 
           'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 
           'Slovakia', 'Slovenia', 'Spain', 'Sweden']
    
    if len(args) != 0:
        for key, value in args[0].items():
            if type(key) is not str and type(value) is not list:
                logging.debug("Dictionary input to regions does not match required type.")
                raise InputError
                return None
            Print_Error = [x for x in value if str(x) not
                           in _reporter.Country.to_list() and str(x) not 
                           in _reporter["ISO"].astype(str).tolist()]
            if len(Print_Error) != 0:
                logging.debug("Error in creating a region! "
                              "Following list of countries not"
                              " found in the ISO list {}. "
                              "Please conform with the ISO list or use"
                              " 3 digit ISO country codes.".format(Print_Error))
                raise InputError
                return None
            else:
                regionslist[key] = value
    for i in _reporter.Country.to_list():
        if i in regionslist.keys():
            logging.debug("Country or region already exists cannot overwrite.")
            raise InputError
            return None
        regionslist[i] = [i]


# The following method connects to the COMTRADE API using request from urlopen module.
# Several inputs required to connect are provided as optional arguments. The user must
# modify the values of these optional arguments before calling the calculation function. 

#Method 3
def COMTRADE_API(
    classification = "HS",
    period = "2010",
    partner = "all",
    reporter = "276",
    HSCode = "2602",
    TradeFlow = "1",
    recyclingrate = 0,
    scenario = 0
    ):
    
    try:
        _request = "https://comtrade.un.org/api/get?max=50000&type=C&freq=A&px="\
        ""+classification+"&ps="+str(period)+"&r="+str(reporter)+"&p="\
        ""+str(partner)+"&cc="+str(HSCode)+"&rg="+TradeFlow+"&fmt=json"
    except Exception as e:
        logging.debug(e)
        raise InputError
    
    # # Section 3.1 connects to the COMTRADE API using the requests method of urlopen library.
    # The user must provide inputs to all of the non-default arguments for most
    # accurate and intended results. A request statement is prepared using the 
    # inputs that is opened in the following line. Any error in the provided 
    # arguments leads to broken request and finally raising an APIError.
    
    # APIError is a defined Exception class available in the warningsgprs.
    
    
    #3.1 Section to connect to the COMTRADE API
    
    #logging.debug(_request) #Uncomment to debug the error
    try:
        request = Request(_request)
        response = urlopen(request)
    except Exception as e:
        logging.debug(_request)
        logging.debug(e)
        raise APIError
        return None
    
    #3.2 Section to read the request result
    try:
        elevations = response.read()
    except Exception as e:
        logging.debug(e)
        raise APIError
        return None
    
    try:
        data = json.loads(elevations)
        data = pd.json_normalize(data['dataset'])
    except Exception as e:
        logging.debug(e)
        raise APIError
        return None
    
    #3.3 Section to extract the results to variables 
    
    if data.shape[0] !=0:
        Worldindex = data.ptCode.to_list().index(0)
        data = data.drop(data.index[[Worldindex]])
        code = data.ptCode.to_list()
        countries = data.ptTitle.to_list()
        quantity = data.TradeQuantity.to_list()
        
        TradeData = [code, countries, quantity]
    else:
        logging.debug(_request)
        logging.debug("API returned empty dataframe")
        
        TradeData = [None, None, None]
    
    return TradeData


"""
The defined trade path in the first method 
"""

#Method 4
def InputTrade(sheetname = None):
    trade_path = tradepath
    
    
    # This function reads the trade file specific to an organization/company.
    # It is possible to read excel or csv file. Section 1 validates if the 
    # path to the file is set using method 1 and reads the file into a dataframe.
    
    
    #4.1 Section to validate the path to trade file
    if trade_path == None:
        raise IncompleteProcessFlow
        return None
    else:
        
        # The file must be either in excel or csv file, failing which raises an 
        # InputError from the warningsgprs module
        
        if Path(trade_path).suffix == ".xlsx" or Path(trade_path).suffix == ".xls":
            try:
                data = pd.read_excel(trade_path, sheet_name=sheetname)
            except Exception as e:
                logging.debug(e)
                raise FileNotFoundError
                return None
        elif Path(trade_path).suffix == ".csv":
            try:
                data = pd.read_csv(trade_path)
            except Exception as e:
                logging.debug(e)
                raise FileNotFoundError
                return None
        else:
            logging.debug(Path(trade_path).suffix)
            raise FileNotFoundError
            return None
        
        
        # The comtrade API results are categorized by imports to a region/country 
        # per country and it includes the total imports to the region/country. The
        # code removes such imports to avoid erronous calculation.
        
        
        try:
            data = data[list(data.keys())[0]]
            if data.shape[0] !=0:
                try:
                    if 0 in data.ptCode.to_list():
                        Worldindex = data.ptCode.to_list().index(0)
                        data = data.drop(data.index[[Worldindex]])
                    else:
                        logging.debug("No worldindex found")
                except Exception as e:
                    logging.debug(e)
                code = data.ptCode.to_list()
                countries = data.ptTitle.to_list()
                quantity = data.TradeQuantity.to_list()
                TradeData = [code, countries, quantity]
            else:
                TradeData = [None, None, None]
            return TradeData
        
        except Exception as e:
            logging.debug(e)
            raise APIError
            return None
   

# The GeoPolRisk method is built with three components, HHI (production concentration),
# weighted trade average (WTA), yearly average price of the resource. With the 
# extracted trade information either using COMTRADE or individual trade is weighted
# using a governance indicator and then averaged using the total imports and domestic
# production of the resource.

# The method 'WTA_calculation' requires the year, trade data, governance indicator, 
# recycling rate and recycling scenario as inputs.

    
 
def WTA_calculation(period, TradeData = None, PIData = None,
                    scenario = 0, recyclingrate = 0.00):
    if TradeData is None or PIData is None:
        raise IncompleteProcessFlow
        return None
    elif TradeData[0] is not None:
        code, quantity = TradeData[0], TradeData[2]
        for i,n in enumerate(quantity):
            if n == None:
                quantity[i] = 0
        reducedmass, totalreduce = 0, 0

        #1.2 Section to calculate the numerator and trade total
        try:
            PIData.columns = PIData.columns.astype(str)
            PI_year = [str(i) for i in PIData.Year.to_list()]
        except Exception as e:
            logging.debug(e)
            raise Exception
            return None
        try:    
            index = PI_year.index(period)
            PI_score = []
            for i in code:
                if str(i) in PIData.columns.to_list():
                    PI_score.append(PIData[str(i)].tolist()[index])
        except Exception as e:
            logging.debug(e)
            raise CalculationError
            return None
                
        
        # Version 0.2: Domestic recycling mitigates the supply risk of a raw material. However domestic recycling
        # can be attributed to decrease of imports from a country with low WGI score or high WGI score.
        # In other words, there can be two scenarios where imports are reduced from 
        # a riskier country (best case scenario) or imports are reduced from 
        # much stable country (worst case scenario). Both the cases are determined by the 
        # WGI score, a higher WGI score is for a riskier country while lower for a stable
        # country. The following code intends to manipulate the trade data to incorporate
        # the domestic recycling.
        
        #Recyclability factor of GeoPolRisk
        _maxscore = max(PI_score)
        _minscore = min(PI_score)
        try:
            if scenario == 0:
                _reduce = [i for i, x in enumerate(PI_score) if x == _maxscore]
            else:
                _reduce = [i for i, x in enumerate(PI_score) if x == _minscore]
        except Exception as e:
            logging.debug(e)
            raise CalculationError
            return None
        try:
            for i in _reduce:
                reducedmass = (quantity[i])*recyclingrate
                quantity[i] = (quantity[i])-reducedmass
                totalreduce += reducedmass
        except Exception as e:
            logging.debug(e)
            raise CalculationError
            return None
        
    
        # After manipulation of the trade data it is multiplied with the WGI
        # score forming the numerator of the second factor of GeoPolRisk (WTA)
        
        
        try:
            zipped_list = zip(quantity, PI_score)
            wgiavg = [x * y for (x,y) in zipped_list]
        except TypeError as e:
            logging.debug(e)
            logging.debug("The Comtrade API is broken")
            raise CalculationError
        try:
            numerator = sum(wgiavg)
            tradetotal = sum(quantity)
        except Exception as e:
            logging.debug(e)
            raise CalculationError
        return numerator, tradetotal
    else:
        return 0, 0

# The first component of the GeoPolRisk method involved calculating the herfindahl-hirschmann
# index (HHI) and total domestic production required for calculating the second factor (WTA).



def productionQTY(Resource, EconomicUnit):
    EconomicUnit = regionslist[EconomicUnit]
    
    try:
        x = pd.read_excel(_production, sheet_name = Resource)
        prod = pd.DataFrame(x)
        Col = prod.columns.tolist()
    except Exception as e:
        logging.debug(e)
        logging.warning("There was an error while acessing the production data file with an exception as ", exc_info = True)
        raise FileNotFoundError
        return None

    #P2. Fetching the production quantity from 'prod' dataframe. 
    try:
        Prod_Year = prod.Year.to_list()
        temp = [0]*len(Prod_Year)
        for i in EconomicUnit:
            if i in Col:
                Prod_Qty = prod[i].values.tolist()
                for k in range(len(Prod_Qty)):
                    if str(Prod_Qty[k]) == 'nan' or Prod_Qty[k] is None:
                        Prod_Qty[k] = 0
                Prod_Qty = [sum(j) for j in zip(temp, Prod_Qty)]
                temp = Prod_Qty
            else:
                Prod_Qty = temp
    except Exception as e:
        logging.debug(e)
        raise CalculationError
        return None
    #logging.debug("The following will be the list of data", "This is the country "+str(i), "Next should be the list ",str(self.Prod_Qty))
   
    #P3. Calculating the HHI.
    Nom = pd.Series()
    try:
        for i in range(1,prod.shape[1]):
            temp = prod.iloc[:,i]*prod.iloc[:,i]
            Nom = Nom.add(temp, fill_value=0)
        DeNom = prod.sum(axis = 1)
        hhi = (Nom /(DeNom*DeNom)).tolist() 
        HHI = [round(i,3) for i in hhi]
    except Exception as e:
        logging.debug(e)
        raise CalculationError
        return None
    return [HHI, Prod_Qty, Prod_Year]

def GeoPolRisk(ProductionData, WTAData, Year, AVGPrice):
    Index = ProductionData[2].index(int(Year))
    HHI = ProductionData[0][Index]
    PQT = ProductionData[0][0]
    try:
        if isinstance(AVGPrice, (int, float)) and WTAData[1] != 0:
            WTA = (WTAData[0]/ (WTAData[1]+PQT))
            GeoPolRisk = HHI * WTA
            GeoPolCF = GeoPolRisk * AVGPrice
        elif WTAData[1] != 0:
            WTA = (WTAData[0]/ (WTAData[1]+PQT))
            GeoPolRisk = HHI * WTA
            GeoPolCF = "NA"
        else:
            WTA = 0
            GeoPolRisk = 0
            GeoPolCF = 0
            logging.debug("WTA has returned 0")
    except Exception as e:
        logging.debug(e)
        logging.debug("The Weighted Trade average value is {}".format(WTA))
        logging.debug("The HHI value is {}".format(HHI))
        logging.debug("The GeoPolRisk is {}".format(GeoPolRisk))
        logging.debug("The AVGPrice is {}".format(AVGPrice))
        raise CalculationError
        return None
    return [HHI, WTA, GeoPolRisk, GeoPolCF]
    
