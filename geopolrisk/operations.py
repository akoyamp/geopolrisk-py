# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 15:29:23 2022

@author: akoyamparamb
"""
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

from .core import (
    regions,
    COMTRADE_API,
    InputTrade,
    WTA_calculation,
    productionQTY,
    GeoPolRisk,
    )
from .Exceptions.warningsgprs import *
import itertools, sqlite3, pandas as pd, time



def convertCodes(resource, country, direction):
    if direction == 1:
        ISO, HS = [], []
        try:
            for i in resource:
                HS.append(_price.iloc[_price.id.to_list().index(resource),26])
            for i in country:
                ISO.append(_reporter.ISO.to_list()[_reporter.Country.to_list().index(i)]) 
        except Exception as e:
            logging.debug(e)
            raise CalculationError
            return None
        return HS,ISO
    if direction == 2:
        try:
            HS = _price.iloc[_price.hs.to_list().index(resource),25]
            ISO = _reporter.Country.to_list()[_reporter.ISO.to_list().index(country)]
        except Exception as e:
            logging.debug(e)
            raise CalculationError
            return None
        return HS,ISO




def sqlverify(*args):
    resource, country, year, recyclingrate, scenario = args[0], args[1], args[2], args[3], args[4] 
    sqlstatement = "SELECT geopolrisk, hhi, wta, geopol_cf FROM recordData WHERE country = '"+country+"' AND resource= '"+resource+"' AND year = '"+str(year)+"' AND recycling_rate = '"+str(recyclingrate)+"' AND scenario = '"+str(scenario)+"';"
    try:
        row = SQL(sqlstatement, SQL = 'select')
    except InputError:
        logging.debug(sqlstatement)
    if not row:
        return None
    else: 
        outputDF.append([str(year), resource , country ,recyclingrate, scenario, row[0][0],row[0][3],row[0][1],row[0][2]])
        return True


def recorddata(*args):
    resource, country, year, recyclingrate, scenario, GPRS, CF, HHI, WTA, HSCODE, ISO, Log= args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7],args[8], args[9], args[10], args[11] 
    sqlstatement = "INSERT INTO recordData (country, resource, year, recycling_rate, scenario, geopolrisk, hhi, wta, geopol_cf, resource_hscode, iso, log_ref) VALUES ('"\
                 ""+country+"','"+resource+"','"+str(year)+""\
                 "','"+str(recyclingrate)+"','"+str(scenario)+"','"\
                 ""+str(GPRS)+"','"+str(HHI)+"','"+str(WTA)+""\
                 "','"+str(CF)+"','"+str(HSCODE)+"','"+str(ISO)+"',"\
                 "'"+str(Log)+"');"
    try:
        row = SQL(sqlstatement, SQL = 'execute')
        return True
    except Exception as e:
        logging.debug(e)



def gprs_comtrade(resourcelist, countrylist, yearlist, recyclingrate, scenario):
    regions()
    
    #Counter to calculate the number of requests sent to API. 
    #Easier to debug the problem
    counter, totalcounter, emptycounter = 0, 0, 0
    
    #Iterate for each value in each list
    for I in itertools.product(resourcelist, countrylist, yearlist):
        totalcounter += 1
        #Need to verify if the data preexists to avoid limited API calls
        try:
            resource, country = convertCodes(I[0], I[1], 2)
            verify = sqlverify(resource, country, I[2], recyclingrate, scenario)
        except Exception as e:
            logging.debug(e)    
            logging.debug(verify)
            
            
        if verify is None:
            #The program has to sleep inorder to avoid conflict in multiple API requests
            time.sleep(5)
            try:
                counter  += 1
                TradeData = COMTRADE_API(classification = "HS",
                period = I[2],
                partner = "all",
                reporter = I[1],
                HSCode = I[0],
                TradeFlow = "1",
                recyclingrate = recyclingrate,
                scenario = scenario)
            except APIError as e:
                logging.debug(e)
                counter -= 1
                break
            
            #From the core methods, TradeData is None only when the dataframe is empty
            emptycounter += 1 if TradeData[0] is None else emptycounter
            
            try:
                AVGPrice = _price[str(I[2])].tolist()[_price.hs.to_list().index(I[0])]
                X = productionQTY(resource, country)
                Y = WTA_calculation(str(I[2]), TradeData = TradeData, PIData = _wgi, scenario = scenario, recyclingrate = recyclingrate)
                HHI, WTA, Risk, CF = GeoPolRisk(X, Y, str(I[2]), AVGPrice)
            
            except Exception as e:
                logging.debug(e)
                logging.debug("The resource is {}".format(resource))
                logging.debug("The country and year are {} {}".format(country, I[2]))
                continue
                
            outputDF.loc[len(outputDF)] = [str(I[2]), resource, country ,recyclingrate, scenario, Risk, CF, HHI, WTA]
            recorddata(resource, country, I[2], recyclingrate, scenario, Risk, CF, WTA, HHI, I[0], I[1], Filename)
        else:
            logging.debug("No transaction has been made. "
                          "Preexisting data has been inserted in output file.")
            
            
    endlog(counter, totalcounter, emptycounter)




def gprs_regional(resourcelist, countrylist, yearlist, recyclingrate, scenario):
    newregionlist = []
    counter, totalcounter, emptycounter = 0, 0, 0
    newregion = [i for i , x  in enumerate(countrylist) if str(x) not
                   in _reporter.Country.to_list() and str(x) not 
                   in _reporter["ISO"].astype(str).tolist()]
    for i in newregion:
        newregionlist.append(countrylist[i])
        del countrylist[i]
    for l in newregionlist:
        countrylist = regionslist[l]
        _ignore, countrylist = convertCodes([], countrylist, 1)
        for I in itertools.product(resourcelist, yearlist):
            
            counter  += 1
            totalcounter += 1
            
            newcodelist, newcountrylist, newquantitylist = [], [], []
            newtradelist = [newcodelist, newcountrylist, newquantitylist]
            TotalDomesticProduction = 0
            for k in countrylist:
                resource, country = convertCodes(I[0], k, 2)
                verify = sqlverify(resource, country, I[1], recyclingrate, scenario)
                if verify is None:
                    TradeData = COMTRADE_API(classification = "HS",
                    period = I[1],
                    partner = "all",
                    reporter = k,
                    HSCode = I[0],
                    TradeFlow = "1",
                    recyclingrate = recyclingrate,
                    scenario = scenario)
                    
                    if TradeData [0] is None:
                        emptycounter += 1
                    for ind, n in enumerate(TradeData[0]):
                        if n not in newcodelist:
                            newcodelist.append(n)
                            newquantitylist.append(TradeData[2][ind])
                            newcountrylist.append(TradeData[1][ind])
                        else:
                            index = newcodelist.index(n)
                            newquantitylist[index] = newquantitylist[index] + TradeData[2][ind]
                            
                    X = productionQTY(resource, country)
                    index = X[2].index(I[1])
                    TotalDomesticProduction += X[1][index]
                else:
                    logging.debug("No transaction has been made. "
                          "Preexisting data has been inserted in output file.")
                    counter -= 1
            AVGPrice = _price[str(I[1])].tolist()[_price.hs.to_list().index(i)]
            Y = WTA_calculation(str(I[1]), TradeData = newtradelist)
            HHI, WTA, Risk, CF = GeoPolRisk([X[0], TotalDomesticProduction, X[2]], Y, str(I[1]), AVGPrice)
            outputDF.loc[len(outputDF)] = [str(I[1]), resource, l ,recyclingrate, scenario, Risk, CF, HHI, WTA]
    
    endlog(counter, totalcounter, emptycounter)
    



def gprs_organization(resourcelist, countrylist, yearlist, recyclingrate, scenario, sheetname):
    newregionlist = []
    newregion = [i for i , x  in enumerate(countrylist) if str(x) not
                   in _reporter.Country.to_list() and str(x) not 
                   in _reporter["ISO"].astype(str).tolist()]
    for i in newregion:
        newregionlist.append(countrylist[i])
        del countrylist[i]
    for l in newregionlist:
        countrylist = regionslist[l]
        _ignore, countrylist = convertCodes([], countrylist, 1)
        for I in itertools.product(resourcelist, yearlist):
            TotalDomesticProduction = 0
            TradeData = InputTrade(sheetname)
            for k in countrylist:
                resource, country = convertCodes(I[0], k, 2)
                try:                            
                    X = productionQTY(resource, country)
                    index = X[2].index(I[1])
                    TotalDomesticProduction += X[1][index]
                except Exception as e:
                    logging.debug(e)
            AVGPrice = _price[str(I[1])].tolist()[_price.hs.to_list().index(i)]
            
            Y = WTA_calculation(str(I[1]), TradeData = TradeData)
            HHI, WTA, Risk, CF = GeoPolRisk([X[0], TotalDomesticProduction, X[2]], Y, str(I[1]), AVGPrice)
            outputDF.loc[len(outputDF)] = [str(I[1]), resource, l ,recyclingrate, scenario, Risk, CF, HHI, WTA]

"""
End of script logging and exporting database to specified format. End log 
method requires extractdata method to be precalled to work. 
"""


def endlog( counter=0, totalcounter=0, emptycounter=0):
    logging.debug("Number of successfull COMTRADE API attempts {}".format(counter))
    logging.debug("Number of total attempts {}".format(totalcounter))
    logging.debug("Number of empty dataframes {}".format(emptycounter))
    outputDF.to_csv(_outputfile+'/export.csv')

    
"""Convert entire database to required format
**CHARACTERIZATION FACTORS
Refer to python json documentation for more information on types of
orientation required for the output.
"""


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
        conn = sqlite3.connect(_outputfile+"/datarecords.db", isolation_level=None,
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
    

