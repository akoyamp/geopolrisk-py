# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 14:23:19 2021

@author: akoyamparamb
"""


from __init__ import _commodity, _resource, _reporter
cc = _commodity
import sqlite3, pandas as pd

connect = sqlite3.connect('./lib/datarecords.db')
cursor = connect.cursor()
sqlstatement = "SELECT * FROM recordData"
cursor.execute(sqlstatement)
row = cursor.fetchall()
records = pd.DataFrame(row, columns = ["id", "country", "resource",
                                        "year", "recycling_rate", "scenario",
                                        "geopolrisk", "hhi", "wta", "geopol_cf",
                                        "resource_hscode", "iso"])


resources = records.resource.to_list()
for i, j in enumerate(resources):
    records.at[i,"resource_hscode"] = _resource.loc[_resource["id"] == j].hs.to_list()[0]
    records.at[i, "iso"] = _reporter.loc[_reporter["Country"] == records.iloc[i,1]].ISO.to_list()[0]
    records.at[i, "geopol_cf"] = float(_resource.loc[_resource["id"] == j][str(records.iloc[i,3])].tolist()[0])*records.iloc[i,6] 

#records.to_excel("outputdata.xlsx")