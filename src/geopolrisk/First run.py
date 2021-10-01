# -*- coding: utf-8 -*-
"""
Created on Thu May 27 14:00:11 2021
@author: anish


Testing the functionality of the module.

"""
#%autoreload

from geopolrisk.api import APIError
from geopolrisk.GeoPolRisk import main as main
#from plots import graphics
from tqdm import tqdm
main = main()

ListofMetals = [2602, 2601, 2603, 2511, 8106, 7108, 2613, 2604, 2608, 8107,
                2846, 261610, 251910, 261510, 261710, 2524, 2610, 2504, 271111, 2709,
                2701, 2609, 2614, 2611, 261210, 251910, 280540]
ShortListofMetals = [2602, 2601, 2603, 2709]
ListofCountries = [36, 124, 97, 251, 276, 392, 826, 842] #810520, 283691, 2606,2607,
Year = [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 
        2011, 2012, 2013, 2014, 2015, 2016, 2017]

# for i in tqdm(ListofCountries):
#     for j in (ListofMetals):
#         for K in Year:
#             try:
#                 main.TotalCalculation(period = K, reporter = i, HSCode = j)
#             except APIError:
#                 break
# main.endlog()
# #main.generateCF("json", "split")
main.simplerun()
main.endlog()

