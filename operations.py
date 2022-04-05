# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 15:29:23 2022

@author: akoyamparamb
"""
from geopolrisk.__init__ import (
    APIError,
    _commodity,
    _reporter,
    _resource,
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
    )
PIData, prod_path,  trade_path, wgi_path = path()


def Nonregion_totcal(resourcelist, country, yearlist, recyclingrate, scenario):
    pass
    