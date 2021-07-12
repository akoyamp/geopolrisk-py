# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 17:08:47 2021

@author: akoyamparamb
"""
import sqlite3



def execute(sqlstatement):
    try:
        connect = sqlite3.connect('./lib/Test.db')
        cursor = connect.cursor()
    except:
        pass
    cursor.execute(sqlstatement)
    connect.commit()
    connect.close()

try:
    sqlstatement = """CREATE TABLE IF NOT EXISTS recordData 
    (id INTEGER PRIMARY KEY, Country TEXT NOT NULL, Resource 
    TEXT NOT NULL, Year INTEGER NOT NULL, GeoPolRisk TEXT, WeightAvg TEXT);""" 
    execute(sqlstatement)
except Exception as e:
    pass


try:
    sqlstatement = "INSERT INTO recordData (Country, Resource, Year, GeoPolRisk, Weightavg) VALUES ('Australia','Magnesium','2002','0','0') WHERE NOT EXISTS (SELECT * FROM recordData WHERE Country = 'Australia' AND Resource= 'Magnesium' AND Year = '2002')"
    execute(sqlstatement)
    # row = [str(item[0]) for item in self.select(sqlstatement)]   
    # if len(row) == 0 or Year not in row:
    #     sqlstatement = "INSERT INTO recordData (Country, Resource, Year, GeoPolRisk, Weightavg) VALUES ('"+Country+"','"+Metal+"','"+Year+"','"+GPRS+"','"+WA+"');"
    #     
    # else:
    #     self.logging.debug("Redundancy detected!")
except Exception as e:
    print(e)