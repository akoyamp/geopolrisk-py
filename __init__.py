# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 14:33:21 2021

@author: akoyamparamb
"""


import sqlite3, pandas as pd, getpass, logging, os, shutil
from datetime import datetime
from pathlib import Path

__all__ = ["main", "gprs", "plots"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "testing"
__version__ = "0.7"
__data__ = "30 September 2021"
FILES = {"/inputs.db":"geopolrisk/lib/inputs.db","/Production.xlsx":"geopolrisk/lib/Production.xlsx",
         "/datarecords.db":"geopolrisk/lib/datarecords.db","/wgidataset.xlsx":"geopolrisk/lib/wgidataset.xlsx"}


#Test fail variables
LOGFAIL, DBIMPORTFAIL = False, False


#Create directories
directory =  getpass.getuser()
if not os.path.exists(os.path.join(Path.home(), 'Documents/geopolrisk')):
    os.makedirs(os.path.join(Path.home(), 'Documents/geopolrisk'))

_logfile = os.path.join(Path.home(), 'Documents/geopolrisk/logs')
if not os.path.exists(_logfile):
    os.makedirs(_logfile)
    
_outputfile = os.path.join(Path.home(), 'Documents/geopolrisk/output')    
if not os.path.exists(_outputfile):
    os.makedirs(_outputfile)

_libfile = os.path.join(Path.home(), 'Documents/geopolrisk/lib')    
if not os.path.exists(_libfile):
    os.makedirs(_libfile)

#Copy library files
try:    
    for i in FILES.keys():
        shutil.copyfile(FILES[i],_libfile+i)
except:
    print("CRITICAL ERROR: Copy failed!")

#Create a log file for init function
"""
Creating a log file for the init not to mix with the log of the main function. 
Logging is a sophisticated module that allows to record values or strings into 
a defined format. The required format is altered with the function basicConfig
as declared below.
"""
Filename = _logfile+'//import({:%Y-%m-%d(%H-%M-%S)}).log'.format(datetime.now())
try:
    logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s | %(levelname)s | %(threadName)-10s | %(filename)s:%(lineno)s - %(funcName)20s() | %(message)s',
    filename = Filename,
    filemode = 'w'
    )
except:
    #it is imperative that the log file work before running the main code.
    LOGFAIL = True
    print("Cannot create log file!")



"""
Import db contains all raw information of the raw material, country that is 
used in several parts of the code in most of the classess. To avoid redundancy
, the databases are loaded once (when the module is called) as a dataframe,
which is then used throught this module. The database contains three tables
which is imported as three dataframes

"""
#Shall not execute if cannot create log files
if LOGFAIL != True:
    logging.debug('Username: {}'.format(getpass.getuser()))
    try:
        connect = sqlite3.connect('geopolrisk/lib/inputs.db')
        cursor = connect.cursor()
    except:
        logging.debug('Import database not found')
        DBIMPORTFAIL = True
    
    
    #Call all the data from import db
    if DBIMPORTFAIL != True:
        logging.debug("Import database accessed")
        #Get commodity data
        sqlstatement = "SELECT * FROM commodity_hs"
        cursor.execute(sqlstatement)
        row = cursor.fetchall()
        _commodity = pd.DataFrame(row, columns = ["HSCODE", "Parent", "Text"])
        
        #Get resource data
        sqlstatement = "SELECT * FROM pricedata"
        cursor.execute(sqlstatement)
        row = cursor.fetchall()
        _resource = pd.DataFrame(row, columns = ["id", "hs", "2000", "2001", 
                                                 "2002", "2003", "2004",
                                                 "2005", "2006", "2007",
                                                 "2008", "2009", "2010",
                                                 "2011", "2012", "2013",
                                                 "2014", "2015", "2016",
                                                 "2017", "2018", "2019",
                                                 "2020", "2021", "2022",
                                                 "2023", "2024"])
        
        
        #Get resource data
        sqlstatement = "SELECT * FROM reporter_iso"
        cursor.execute(sqlstatement)
        row = cursor.fetchall()
        _reporter = pd.DataFrame(row, columns = ["ISO", "Country"])
        
        #close db
        connect.commit()
        connect.close()
    else:
        _commodity, _resource, _reporter = None, None, None 
        



"""
The class is an error class that shall be raised in order to break
an operation or close an operation. The users are free to modify this class.
BREAK THE CODE IF EXCEPT AN APIERROR
""" 
class APIError(Exception): 
    def __init__(self, ):
        pass