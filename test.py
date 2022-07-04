# -*- coding: utf-8 -*-
"""
Created on Sat May 28 03:00:24 2022

@author: anish
"""

from geopolrisk.operations import update_cf, gprs_comtrade
import time

ListofMetals = [2602, 2601, 2603, 2511, 8106, 7108, 2613, 2604, 2608, 8107,
                  261610, 251910, 261510, 261710, 2524, 2610, 2504, 271111, 2709,
                2701, 2609, 2611, 261210, 251910, 810520, 280540, 2606, 2607]#  
ShortListofMetals = [2602, 2601, 2603, 2846, 2614, 2709, 283691,]
ListofCountries = [36, 124, 97, 251, 276, 392, 826, 842,] 
ShortListofCountries = [36, 124, 97, 251]#
Year = [2002, 2003,  2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]#,
ShortListofYear = [2017, 2018, 2019, 2020]

for i in range(100):
    try:
        gprs_comtrade(ListofMetals, ListofCountries, ShortListofYear, 0, 0)
    except Exception as e:
        print(e)
        continue
    time.sleep(3600)


# update_cf()

# from geopolrisk.gprsplots import compareplot

# dip = compareplot(["Australia", "France", "Canada", "European Union"],[2014], ["Manganese","Iron", "Copper", "Petroleum"], 0)
# dip.show()

# from geopolrisk.operations import updateprice 
# updateprice()
