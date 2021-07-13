# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 11:33:56 2021

@author: akoyamparamb
"""
import sqlite3
import pandas as pd
_columns = ["Year", "Resource", "Country", "GeoPolRisk", "HHI", "WA"]
outputDF = pd.DataFrame(columns = _columns)

def extractdata( Year, Country, Metal):
    def select(sqlstatement):
        try:
            connect = sqlite3.connect('./lib/datarecords.db')
            cursor = connect.cursor()
        except Exception as e:
            print(e)
        cursor.execute(sqlstatement)
        row = cursor.fetchall()
        connect.commit()
        connect.close()
        return row
    try:
        data = select("SELECT GeoPolRisk, WeightAvg FROM recordData WHERE Country = '"+Country+"' AND Resource= '"+Metal+"' AND Year='"+Year+"'")
    except Exception as e:
        print(e)
        
    if len(data) !=0:
        toappend = [Year,Metal,Country,data[0][0],0,data[0][1]]
        outputDF.loc[len(outputDF)] = toappend
       
    
    
extractdata('2010', 'Japan', 'Copper')