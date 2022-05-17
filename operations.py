# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 15:29:23 2022

@author: akoyamparamb
"""
from __init__ import (
    APIError,
    _commodity,
    _reporter,
    _price,
    _outputfile,
    outputDF,
    logging)

from core import (
    SQL,
    path,
    regions,
    COMTRADE_API,
    InputTrade,
    WTA_calculation,
    productionQTY,
    endlog,
    GeoPolRisk,
    variables,
    regionslist,
    definitionrequired,
    )

def convertCodes(resource, country, direction):
    if direction == 1:
        ISO, HS = [], []
        for i in resource:
            HS.append(_price.iloc[_price.id.to_list().index(resource),1])
        for i in country:
            ISO.append(_reporter.ISO.to_list()[_reporter.Country.to_list().index(i)])
            
        return HS,ISO
    if direction == 2:
        HS = _price.iloc[_price.hs.to_list().index(resource),0]
        ISO = _reporter.Country.to_list()[_reporter.ISO.to_list().index(country)]
        return HS,ISO

def sqlverify(*args):
    resource, country, year, recyclingrate, scenario = args[0], args[1], args[2], args[3], args[4] 
    sqlstatement = "SELECT geopolrisk, hhi, wta, geopol_cf FROM recordData WHERE country = '"+country+"' AND resource= '"+resource+"' AND year = '"+str(year)+"' AND recycling_rate = '"+str(recyclingrate)+"' AND scenario = '"+str(scenario)+"';"
    row = SQL(sqlstatement, SQL = 'select')
    if not row:
        return None
    else: 
        outputDF.append([str(year), resource , country ,recyclingrate, scenario, row[0][0],row[0][3],row[0][1],row[0][2]])
        return True


def Nonregion_totcal(resourcelist, countrylist, yearlist, recyclingrate, scenario):
    #Call Path and Regions
    path()
    regions()
    for i in resourcelist:
        for j in countrylist:
            for k in yearlist:
                resource, country = convertCodes(i, j, 2)
                verify = sqlverify(resource, country, k, recyclingrate, scenario)
                if verify is not None:
                    TradeData = COMTRADE_API(classification = "HS",
                    period = k,
                    partner = "all",
                    reporter = j,
                    HSCode = i,
                    TradeFlow = "1",
                    recyclingrate = recyclingrate,
                    scenario = scenario)
                    AVGPrice = _price[str(k)].tolist()[_price.hs.to_list().index(i)]
                    X = productionQTY(resource, country)
                    Y = WTA_calculation(str(k), TradeData = TradeData)
                    
                    HHI, WTA, Risk, CF = GeoPolRisk(X, Y, str(k), AVGPrice)
                    outputDF.loc[len(outputDF)] = [str(k), resource, country ,recyclingrate, scenario, Risk, CF, HHI, WTA]
                else:
                    logging.debug("No transaction has been made. "
                                  "Preexisting data has been inserted in output file.")


@definitionrequired
def regional_totcal(resourcelist, countrylist, yearlist, recyclingrate, scenario):
    newregionlist = []
    if variables[2] is None:
        newregion = [i for i , x  in enumerate(countrylist) if str(x) not
                       in _reporter.Country.to_list() and str(x) not 
                       in _reporter["ISO"].astype(str).tolist()]
        for i in newregion:
            newregionlist.append(countrylist[i])
            del countrylist[i]
        if len(countrylist) != 0:
            for i in resourcelist:
                _ignore, countrylist = convertCodes([], countrylist, 1) #Comment if country list are in iso codes
                for j in countrylist:
                    for k in yearlist:
                        resource, country = convertCodes(i, j, 2)
                        verify = sqlverify(resource, country, k, recyclingrate, scenario)
                        if verify is not None:
                            TradeData = COMTRADE_API(classification = "HS",
                            period = k,
                            partner = "all",
                            reporter = j,
                            HSCode = i,
                            TradeFlow = "1",
                            recyclingrate = recyclingrate,
                            scenario = scenario)
                            AVGPrice = _price[str(k)].tolist()[_price.hs.to_list().index(i)]
                            X = productionQTY(resource, country)
                            Y = WTA_calculation(str(k), TradeData = TradeData)
                            
                            HHI, WTA, Risk, CF = GeoPolRisk(X, Y, str(k), AVGPrice)
                            
                            outputDF.loc[len(outputDF)] = [str(j), resource, country ,recyclingrate, scenario, Risk, CF, HHI, WTA]
                            logging.debug("No transaction has been made. "
                                          "Preexisting data has been inserted in output file.")
        else:
            for l in newregionlist:
                countrylist = regionslist[l]
                _ignore, countrylist = convertCodes([], countrylist, 1)
                for i in resourcelist:
                    for j in yearlist:
                        newcodelist, newcountrylist, newquantitylist = [], [], []
                        TotalDomesticProduction = 0
                        for k in countrylist:
                            resource, country = convertCodes(i, k, 2)
                            verify = sqlverify(resource, country, j, recyclingrate, scenario)
                            if verify is not None:
                                TradeData = COMTRADE_API(classification = "HS",
                                period = j,
                                partner = "all",
                                reporter = k,
                                HSCode = i,
                                TradeFlow = "1",
                                recyclingrate = recyclingrate,
                                scenario = scenario)
                                
                                for ind, n in enumerate(TradeData[0]):
                                    if n not in newcodelist:
                                        newcodelist.append(n)
                                        newquantitylist.append(TradeData[2][ind])
                                        newcountrylist.append(TradeData[1][ind])
                                    else:
                                        index = newcodelist.index(n)
                                        newquantitylist[index] = newquantitylist[index] + TradeData[2][ind]
                                        
                                    X = productionQTY(resource, country)
                                    index = X[2].index(j)
                                    TotalDomesticProduction += X[1][index]
                            else:
                                logging.debug("No transaction has been made. "
                                      "Preexisting data has been inserted in output file.")
                        AVGPrice = _price[str(j)].tolist()[_price.hs.to_list().index(i)]
                        Y = WTA_calculation(str(j), TradeData = TradeData)
                        HHI, WTA, Risk, CF = GeoPolRisk([X[0], TotalDomesticProduction, X[2]], Y, str(j), AVGPrice)
                        outputDF.loc[len(outputDF)] = [str(j), resource, l ,recyclingrate, scenario, Risk, CF, HHI, WTA]
                    



   