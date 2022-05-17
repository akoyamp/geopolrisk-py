# Copyright 2020-2021 by Anish Koyamparambath and University of Bordeaux. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Anish Koyamparambath (AK) or 
# University of Bordeaux (UBx) will not be used in advertising or publicity pertaining 
# to distribution of the software without specific, written prior permission.
# BOTH AK AND UBx DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# BOTH AK AND UBx BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import sqlite3, pandas as pd, getpass, logging, os, shutil
from datetime import datetime
from pathlib import Path
from warnings import InputError

logging = logging
__all__ = ["main", "gprs", "plots"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "testing"
__version__ = "0.95"
__data__ = "30 March 2022"

hard_dependencies = ("pandas", "logging", "urllib")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(f"{dependency}: {e}")

if missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies


dir_path = os.path.dirname(os.path.realpath(__file__))
FILES = {"/inputs.db":dir_path+"/lib/inputs.db","/Production.xlsx":dir_path+"/lib/Production.xlsx",
         "/datarecords.db":dir_path+"/lib/datarecords.db","/wgidataset.xlsx":dir_path+"/lib/wgidataset.xlsx"}


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
Do not modify the path for the logs folder unless you specifically need
it elsewhere. Modify the alert level depending on requirements for debugging. 
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
        connect = sqlite3.connect(_libfile+'/inputs.db')
        cursor = connect.cursor()
    except:
        logging.debug('Import database not found')
        DBIMPORTFAIL = True

_commodity = pd.DataFrame(row, columns = ["HSCODE", "Parent", "Text"])

_price = pd.read_csv(row, columns = ["id", "hs", "2000", "2001", 
                                         "2002", "2003", "2004",
                                         "2005", "2006", "2007",
                                         "2008", "2009", "2010",
                                         "2011", "2012", "2013",
                                         "2014", "2015", "2016",
                                         "2017", "2018", "2019",
                                         "2020", "2021", "2022",
                                         "2023", "2024"])

_reporter = pd.DataFrame(row, columns = ["ISO", "Country"])


_commodity, _price, _reporter = None, None, None 
        

_columns = ["Year", "Resource", "Country","Recycling Rate","Recycling Scenario", "Risk","GeoPolRisk Characterization Factor", "HHI", "Weighted Trade AVerage"]
outputDF = pd.DataFrame(columns = _columns)


"""
SQL select method. This program is used
only to pull records (ONLY SELECT STATEMENT)
"""
#Defining select/execute functions
def SQL(database, sqlstatement, SQL = 'select' ):
    
    try:
        connect = sqlite3.connect(database)
        cursor = connect.cursor()  
        if SQL == 'select':
            cursor.execute(sqlstatement)
            output = cursor.fetchall()
        elif SQL == 'execute': 
            cursor.execute(sqlstatement)
            output = None
        else:
            print("Unknown SQL operation requested")
            logging.debug(sqlstatement)
            raise InputError
    except:
        connect.commit()
        connect.close()
        logging.debug('Datarecords database not found')
        return output



