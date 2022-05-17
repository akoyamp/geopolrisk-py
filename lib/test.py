# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:40:59 2022

@author: akoyamparamb
"""


import pandas as pd
import json
file = "pricedata.json"
with open(file) as dingi:
    data = json.load(dingi)

train = pd.DataFrame.from_dict(data, orient="index").reset_index(level=0, inplace=True)
