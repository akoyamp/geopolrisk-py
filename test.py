# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:40:59 2022

@author: akoyamparamb
"""

import pandas as pd
import json, os

dir_path = os.path.dirname(os.path.realpath(__file__))
FILES = {"commodity":"lib/commodityHS.json","production":dir_path+"/lib/Production.xlsx",
          "reporter":dir_path+"/lib/reporterISO.json","wgi":dir_path+"/lib/wgi.json", "yearly":dir_path+"/lib/yearlyAVGprice.json"}
with open(FILES["reporter"]) as dingi:
    data = json.load(dingi)

train = pd.DataFrame.from_dict(data, orient="index")
