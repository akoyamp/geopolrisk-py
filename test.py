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
    sqlstatement = "SELECT Year FROM recordData WHERE Country = '"+Country+"' AND Resource= '"+Metal+"';"
    row = [str(item[0]) for item in self.select(sqlstatement)]   
    if len(row) == 0 or Year not in row:
        sqlstatement = "INSERT INTO recordData (Country, Resource, Year, GeoPolRisk, Weightavg) VALUES ('"+Country+"','"+Metal+"','"+Year+"','"+GPRS+"','"+WA+"');"
        execute(sqlstatement)
    else:
        self.logging.debug("Redundancy detected!")
except Exception as e:
    self.logging.debug(e)