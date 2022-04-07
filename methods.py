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
import pandas as pd, sqlite3, json
from urllib.request import Request, urlopen
from functools import wraps
from __init__ import (
    IncompleteProcessFlow,
    InputError,
    APIError,
    _commodity,
    _reporter,
    _outputfile,
    _libfile,
    outputDF,
    logging)

#Define Paths

variables = [_libfile+'/datarecords.db',
             ]
regionslist = {}


"""The program is equipped with a predefined database for production of a 
raw materia. Change the path of the respective databases to customize the 
calculation.
""" 

"""
SQL select method. This program is used
only to pull records (ONLY SELECT STATEMENT)
"""
#Defining select/execute functions
def SQL(sqlstatement, SQL = 'select' ):
    
    if SQL == 'select':
        try:
            connect = sqlite3.connect(variables[0])
            cursor = connect.cursor()
            cursor.execute(sqlstatement)
            row = cursor.fetchall()
            connect.commit()
            connect.close()
            return row
        except:
            logging.debug('Datarecords database not found')
            connect.commit()
            connect.close()
            return None
    elif SQL == 'execute':
        try:
            connect = sqlite3.connect(variables[0])
            cursor = connect.cursor()
            cursor.execute(sqlstatement)
            #logging.debug(sqlstatement)
            return True
        except:
            logging.debug('Datarecords database not found')
            return None
 
#Method define library path
def path(
     prod_path = _libfile+'/production.xlsx',
     trade_path = None,
     wgi_path = _libfile+'/wgidataset.xlsx',
     ):
    
    #Create table if not available. The database file should be present.
    try:
        sqlstatement = """CREATE TABLE IF NOT EXISTS "recordData" (
        	"id"	INTEGER,
        	"country"	TEXT,
        	"resource"	TEXT,
        	"year"	INTEGER,
        	"recycling_rate"	REAL,
        	"scenario"	REAL,
        	"geopolrisk"	REAL,
        	"hhi"	REAL,
        	"wta"	REAL,
        	"geopol_cf"	REAL,
        	"resource_hscode"	REAL,
        	"iso"	TEXT,
        	PRIMARY KEY("id")
        );""" 
        try:
            connect = sqlite3.connect(variables[0])
            cursor = connect.cursor()
        except:
            logging.debug('Database not found')
        cursor.execute(sqlstatement)
        connect.commit()
        connect.close()
    except Exception as e:
        logging.debug(e)
        return None
        
    #Pull WGI data
    try:
        WGI = pd.read_excel(wgi_path, sheet_name = 'INVNOR')
    except Exception as e:
        logging.debug(e)
        return None
    
    variables.extend([prod_path, trade_path, wgi_path, WGI])
    
    #Confirmation of loading this function
    

"""User can modify this section along with another section in the calculation
if more trade blocs, regions or group of countries is necessary for the study
"""
"""It is important to note that the region EU is existing in the countries
database which shall be used to call the COMTRADE API. Unfortunately, other 
trade blocs or regions are unavailable and has to be called separately tallied
and accounted. In version 1, such feature is not available in the code. If users
modify the regions, ensure the countries and # section is modified accordingly. 
"""
    
#Method 3
def regions(**kwargs):
    if len(variables) < 5:
        raise IncompleteProcessFlow("Path of the files must be defined before regions.")
    regionslist['EU'] = ['Austria', 'Belgium', 'Belgium-Luxembourg', 'Bulgaria',
           'Croatia', 'Czechia', 'Czechoslovakia', 'Denmark', 
           'Estonia','Finland', 'France', 'Fmr Dem. Rep. of Germany',
           'Fmr Fed. Rep. of Germany', 'Germany', 'Greece', 'Hungary',
           'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 
           'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 
           'Slovakia', 'Slovenia', 'Spain', 'Sweden'],
    

    for key, value in kwargs.items():
        if key != str and value != list:
            raise InputError("Inputs does not match the required format")
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
            raise InputError("Countries in the list does not match ISO naming standards: "
                             "Please refer to documentation.")
            return None
        else:
            regionslist[key] = value
    for i in _reporter.Country.to_list():
        if i in regionslist.keys():
            raise InputError("Country or region already exists cannot overwrite.")
            return None
        regionslist[i] = [i]



#Decorator for path and regions required
def definitonrequired(func):
    @wraps(func)
    def verify(*args, **kwargs):
        if len(variables) < 5 or len(regionslist) < 257:
            raise IncompleteProcessFlow("The path and regions must be defined before execution :"
                                )
            
        else: 
            return func(*args, **kwargs)
    return verify


   
"""
The following method connects to the COMTRADE API using request from urlopen module.
Several inputs required to connect are provided as optional arguments. The user must
modify the values of these optional arguments before calling the calculation function. 

"""
#Method 1
@definitonrequired
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
    
    
    _request = "https://comtrade.un.org/api/get?max=50000&type=C&freq=A&px="+classification+"&ps="+period+"&r="+reporter+"&p="+partner+"&cc="+HSCode+"&rg="+TradeFlow+"&fmt=json"
    
    """
    Section 1.1 connects to the COMTRADE API using the requests method of urlopen library.
    Variable counter and totcounter counts the number of requests made to the COMTRADE API,
    as the number of connection per hour is limited to 100 as a public user. The connections 
    are logged in the end of script. User must call Method 7 of GeoPolRisk module in order to be logged.
    ----> Remember Method 7 requires Method 6 to be called as a prerequisite.
    """
    #1.1 Section to connect to the COMTRADE API
    logging.debug(_request) #Uncomment to debug the error
    try:
        request = Request(_request)
        response = urlopen(request)
    except Exception as e:
        logging.debug(e)
        raise APIError("Unable to access COMTRADE api. Refer to geopolrisk.logs")
        return None
    
    try:
        elevations = response.read()
    except Exception as e:
        logging.debug(e)
        raise APIError("Unable to read API data. Refer to geopolrisk.logs")
    
    data = json.loads(elevations)
    data = pd.json_normalize(data['dataset'])
    
    if data.shape[0] !=0:
        Worldindex = data.ptCode.to_list().index(0)
        data = data.drop(data.index[[Worldindex]])
        code = data.ptCode.to_list()
        countries = data.ptTitle.to_list()
        quantity = data.TradeQuantity.to_list()
        
        TradeData = [code, countries, quantity]
    else:
        TradeData = [None, None, None]
    
    COMTRADE_API.called = True
    return TradeData
     
@definitonrequired
def InputTrade( sheetname = None):
    trade_path = variables[2]
    if trade_path == None:
        raise InputError("Did not define path for individual trade.")
        return None
    try:
        data = pd.read_excel(trade_path, sheet_name=sheetname)
        data = data[list(data.keys())[0]]
        if data.shape[0] !=0:
            try:
                Worldindex = data.ptCode.to_list().index(0)
                data = data.drop(data.index[[Worldindex]])
            except Exception as e:
                logging.debug(e)
            code = data.ptCode.to_list()
            countries = data.ptTitle.to_list()
            quantity = data.TradeQuantity.to_list()
            
            TradeData = [code, countries, quantity]
        else:
            TradeData = [None, None, None]
        InputTrade.called = True
        return TradeData
    
    except Exception as e:
        logging.debug(e)
        raise APIError
        return None
   
@definitonrequired   
def WTA_calculation(period, TradeData = None, PIData = None,
                    scenario = 0, recyclingrate = 0.00):
    PIData = variables[4]
    if TradeData == None:
        return None
    else:
        """
        Section 1.2 is dedicated to calculation of a part of second factor of GeoPolRisk method also
        known as Weighted Trade Average (WTA). The trade information is weighted with the WGI values
        pulled from the csv file in the library. 
        """
        code, countries, quantity = TradeData[0], TradeData[1], TradeData[2]

        reducedmass, totalreduce = 0, 0

        #1.2 Section to calculate the numerator and trade total
        try:
            PIData.columns = PIData.columns.astype(str)
            PI_year = [str(i) for i in PIData.Year.to_list()]
        except Exception as e:
            logging.debug(e)
            return None
        try:    
            index = PI_year.index(period)
            PI_score = []
            for i in code:
                if str(i) in PIData.columns.to_list():
                    PI_score.append(PIData[str(i)].tolist()[index])
        except Exception as e:
            logging.debug(e)
            raise APIError
            return None
                
        """
        Version 0.2: Domestic recycling mitigates the supply risk of a raw material. However domestic recycling
        can be attributed to decrease of imports from a country with low WGI score or high WGI score.
        In other words, there can be two scenarios where imports are reduced from 
        a riskier country (best case scenario) or imports are reduced from 
        much stable country (worst case scenario). Both the cases are determined by the 
        WGI score, a higher WGI score is for a riskier country while lower for a stable
        country. The following code intends to manipulate the trade data to incorporate
        the domestic recycling.
        """
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
            raise APIError
            return None
        try:
            for i in _reduce:
                reducedmass = (quantity[i])*recyclingrate
                quantity[i] = (quantity[i])-reducedmass
                totalreduce += reducedmass
        except Exception as e:
            logging.debug(e)
            raise APIError
            return None
        
        """
        After manipulation of the trade data it is multiplied with the WGI
        score forming the numerator of the second factor of GeoPolRisk (WTA)
        """
        
        try:
            zipped_list = zip(quantity, PI_score)
            wgiavg = [x * y for (x,y) in zipped_list]
        except TypeError as e:
            logging.debug(e)
            logging.debug("The Comtrade API is broken")
            raise APIError
        try:
            numerator = sum(wgiavg)
            tradetotal = sum(quantity)
        except Exception as e:
            logging.debug(e)
            raise APIError
        WTA_calculation.called = True
        return numerator, tradetotal
        
"""
The first factor of the GeoPolRisk method involved calculating the herfindahl-hirschmann
index (hhi) and total domestic production required for calculating the second factor (WTA).
Regions, economic units or trade blocs such as the EU can also be a part of the calculation.
However, COMTRADE by default has the aggregated data for the EU, for others such as OECD etc 
the code has to be manipulated inorder to aggregate the trade data. The regions has to be first
defind in the 'regions' method in GeoPolRisk module. The production information is available in 
excel file in library.
"""

@definitonrequired
def productionQTY(Resource, EconomicUnit):
    EconomicUnit = regionslist[EconomicUnit]
    
    try:
        if Resource in ['Cerium', 'Lanthanum']:
            Resource = 'Rare Earth'
        x = pd.read_excel(variables[1], sheet_name = Resource)
        prod = pd.DataFrame(x)
        Col = prod.columns.tolist()
    except Exception as e:
        logging.debug(e)
        logging.warning("There was an error while acessing the file Metals_Raw.xlsx with an exception as ", exc_info = True)
        raise APIError
        return None

    #P2. Fetching the production quantity from 'prod' dataframe.
    Prod_Year = prod.Year.to_list()
    temp = [0]*len(Prod_Year)
    for i in EconomicUnit:
        if i in Col:
            Prod_Qty = prod[i].values.tolist()
            for k in range(len(Prod_Qty)):
                if str(Prod_Qty[k]) == 'nan':
                    Prod_Qty[k] = 0
            Prod_Qty = [sum(j) for j in zip(temp, Prod_Qty)]
            temp = Prod_Qty
        else:
            Prod_Qty = temp
    #logging.debug("The following will be the list of data", "This is the country "+str(i), "Next should be the list ",str(self.Prod_Qty))
   
    #P3. Calculating the HHI.
    Nom = pd.Series()
    for i in range(1,prod.shape[1]):
        temp = prod.iloc[:,i]*prod.iloc[:,i]
        Nom = Nom.add(temp, fill_value=0)
    DeNom = prod.sum(axis = 1)
    hhi = (Nom /(DeNom*DeNom)).tolist() 
    HHI = [round(i,3) for i in hhi]
    
    
    productionQTY.called = True
    return [HHI, Prod_Qty, Prod_Year]

def GeoPolRisk(ProductionData, WTAData, Year, AVGPrice):
    Index = ProductionData[2].index(Year)
    HHI = ProductionData[0][Index]
    PQT = ProductionData[0][0]
    WTA = (WTAData[0]/ (WTAData[1]+PQT))
    
    GeoPolRisk = HHI * WTA
    GeoPolCF = GeoPolRisk * AVGPrice
    
    return [HHI, WTA, GeoPolRisk, GeoPolCF]
    
"""
End of script logging and exporting database to specified format. End log 
method requires extractdata method to be precalled to work. 
"""

@definitonrequired
def endlog( counter=0, totcounter=0, emptycounter=0, outputDFType='csv'):
    logging.debug("Number of successfull COMTRADE API attempts {}".format(counter))
    logging.debug("Number of total attempts {}".format(totcounter))
    logging.debug("Number of empty dataframes {}".format(emptycounter))
    if outputDFType == 'json':
        outputDF.to_json(_outputfile+'/export.json', orient='columns')
    elif outputDFType =='excel':
        outputDF.to_excel(_outputfile+'/export.xlsx')
    else:
        outputDF.to_csv(_outputfile+'/export.csv')

    
"""Convert entire database to required format
**CHARACTERIZATION FACTORS
Refer to python json documentation for more information on types of
orientation required for the output.
"""

@definitonrequired
def generateCF(exportType='csv', orient=""):
    exportF = ['csv', 'excel', 'json']
    if exportType in exportF:
        logging.debug("Exporting database in the format {}".format(exportType))
        CFType=exportType
    else:
        logging.debug("Exporting format not supported {}. "
                      "Using default format [csv]".format(exportType))
        CFType="csv"
    try:
        conn = sqlite3.connect(variables[0], isolation_level=None,
                   detect_types=sqlite3.PARSE_COLNAMES)
        db_df = pd.read_sql_query("SELECT * FROM recorddata", conn)
        if CFType == "csv":
            db_df.to_csv(_outputfile+'/database.csv', index=False)
        elif CFType == "excel":
            db_df.to_excel(_outputfile+'/database.xlsx', index=False)
        elif CFType == "json":
             db_df.to_json(_outputfile+'/database.json', orient = orient, index=False)
    except Exception as e:
        logging.debug(e)
    

