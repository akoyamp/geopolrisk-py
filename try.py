# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 17:07:11 2022

@author: akoyamparamb
"""



from methods import *
path(trade_path="comtrade.xlsx")
regions()
TD = InputTrade()
X = productionQTY("Aluminium", "Germany")
Y = WTA_calculation("2015", TradeData = TD)

x = X[2].index(2015)
HHI = X[0][x]
PQT = X[0][0]
Nom = Y[0]
Denom = Y[1]

GeoPolRisk = HHI * (Nom/ (Denom+PQT))