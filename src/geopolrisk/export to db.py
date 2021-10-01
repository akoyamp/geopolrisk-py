# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 13:42:27 2021

@author: akoyamparamb
"""
import pandas as pd, sys, getpass, json, sqlite3, logging

json_file = open('./lib/hs.json', 'r')
data = pd.json_normalize(json.loads(json_file.read())['results'])
data.to_excel("hs.xlsx")