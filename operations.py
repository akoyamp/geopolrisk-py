# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 15:29:23 2022

@author: akoyamparamb
"""
from geopolrisk.__init__ import (
    APIError,
    _commodity,
    _reporter,
    _price,
    _outputfile,
    outputDF,
    logging)

from geopolrisk.methods import (
    SQL,
    path,
    regions,
    COMTRADE_API,
    InputTrade,
    WTA_calculation,
    productionQTY,
    endlog,
    recordspath,
    GeoPolRisk,
    )

def convertCodes(resource, country, direction):
    if direction == 1:
        ISO, HS = []
        for i in resource:
            HS.append(_commodity.HSCODES.to_list()[_commodity.Parent.to_list().index(i)])
        for i in country:
            ISO.append(_reporter.ISO.to_list()[_reporter.Country.to_list().index(i)])
            
        return HS,ISO
    if direction == 2:
        HS = _commodity.Parent.to_list()[_commodity.HSCODES.to_list().index(resource)]
        ISO = _reporter.Country.to_list()[_reporter.ISO.to_list().index(country)]
        return HS,ISO


def Nonregion_totcal(resourcelist, countrylist, yearlist, recyclingrate, scenario):
    #Call Path and Regions
    path()
    regions()
    resourcelist, countrylist = convertCodes(resourcelist, countrylist, 1)
    for i in resourcelist:
        for j in countrylist:
            for k in yearlist:
                TradeData = COMTRADE_API(classification = "HS",
                period = k,
                partner = "all",
                reporter = j,
                HSCode = i,
                TradeFlow = "1",
                recyclingrate = recyclingrate,
                scenario = scenario)
                AVGPrice = _price[str(k)].tolist()[_price.hs.to_list().index(i)]
                i, j = convertCodes(i, j, 2)
                X = productionQTY(i, j)
                Y = WTA_calculation(str(k), TradeData = TradeData)
                
                HHI, WTA, Risk, CF = GeoPolRisk(X, Y, str(k), AVGPrice)
                
                outputDF.append([str(k), i , j ,recyclingrate, scenario, Risk, CF, HHI, WTA])
    endlog()
    
