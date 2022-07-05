# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 19:51:17 2022

@author: anish
"""

import pandas as pd
from sqlalchemy import create_engine
import numpy as np


"""
Using sqlalchemy we can pull the database data into a dataframe.
sql is a dataframe of the inputs.db database stored in lib folder.
It contains the country name and 3 digit ISO codes.
countries is a list of all the country names stored in sql dataframe.
"""
#Pull ISO data from sql file
con = create_engine('sqlite:///lib/inputs.db').connect()
sql = pd.read_sql_table('reporter_iso', con)
countries = sql.Country.to_list()



"""
Pull the production data into a dataframe for a particular sheet name (resource).
Convert the column header to list and remove the first value i.e "Year".
Using the dataframe SQL and countries list created before correlate the 3 digit
ISO codes and store it into columns_ISO.
"""
#dataframe of production data
df = pd.read_excel("lib/Production.xlsx", sheet_name="Aluminium")
columns = df.columns.tolist()
columns = columns[1:]
columns_ISO = []
for i in columns:
    columns_ISO.append(sql.ISO[countries.index(i)])


"""
Using the user input for the year, pull the row from the production data dataframe.
Convert all none to 0.
Convert the values to array and then to a list removing the first value i.e 'Year'.
"""
#Pull production data for a particular year
Production_Data = df.loc[df['Year'] == 2014].fillna(0).values.tolist()[0][1:]

"""
Now display the data using countries from countries_ISO and data from Production_Data.
"""

"""
Data to display below the map.
Three columns
HHI = HHI,
Max producing country = ProdCtry
Max producting quantity = ProdQty
"""

#HHI Calculation
temp = []
for i in range(len(Production_Data)):
    temp.append(Production_Data[i]*Production_Data[i])
Nom = sum(temp)
DeNom = sum(Production_Data)

HHI = round((Nom /(DeNom*DeNom)),3)
ProdQty = max(Production_Data)
ProdCtry = columns[Production_Data.index(ProdQty)]
