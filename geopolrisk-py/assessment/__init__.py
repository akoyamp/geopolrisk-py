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


import sqlite3, pandas as pd, getpass, logging, os, json  # ,shutil
from datetime import datetime
from pathlib import Path
from .Exceptions.warningsgprs import *

logging = logging
__all__ = ["core", "operations", "gcalc", "gprsplots"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "beta"
__version__ = "2.5"
__data__ = "10 June 2022"

hard_dependencies = ("pandas", "logging", "urllib", "functools")
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

# Global Variables
Output = "Eu Geo Bi.db"
Database = "library.db"
OutputFolder = "Documents/geopolrisk"
LogFolder = OutputFolder + "/logs"
CFDatabase = OutputFolder + "/output"
DBFolder = OutputFolder + "/databases"

# Create directories
try:
    directory = getpass.getuser()
    if not os.path.exists(os.path.join(Path.home(), OutputFolder)):
        os.makedirs(os.path.join(Path.home(), OutputFolder))

    logfile = os.path.join(Path.home(), LogFolder)
    if not os.path.exists(logfile):
        os.makedirs(logfile)

    dbFolder = os.path.join(Path.home(), DBFolder)
    if not os.path.exists(dbFolder):
        os.makedirs(dbFolder)

    exportfile = os.path.join(Path.home(), CFDatabase)
    if not os.path.exists(exportfile):
        os.makedirs(exportfile)
except Exception as e:
    print(e)
    print("Unable to create directories")
    raise FileNotFoundError

# Function to use sqlite3
def execute_query(query, db_path=exportfile+'/'+Output):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Determine if the query is a SELECT or INSERT query
    is_select_query = query.strip().lower().startswith("select")

    # Execute the query and fetch the results (if it is a SELECT query)
    if is_select_query:
        cursor.execute(query)
        results = cursor.fetchall()
    else:
        cursor.execute(query)
        results = None

    # Commit the query to the database
    conn.commit()

    # Close the database connection
    conn.close()

    # Return the results (if it is a SELECT query)
    if is_select_query:
        return results

# Verify that the file exists else input the correct file path
if not os.path.isfile(os.path.join(dbFolder, Database)):
    folder_path = input("The file doesn't exist. Please enter a folder path: ")

#Verify if the database contains the required tables
Tables = [
    "commodityHS",
    "Country_ISO",
    "Aluminium",
    "Antimony",
    "Asbestos",
    "Barytes",
    "Bismuth",
    "Cadmium",
    "Chromium",
    "Coal",
    "Cobalt",
    "Copper",
    "Gold",
    "Graphite",
    "Iron",
    "Lead",
    "Lithium",
    "Magnesite",
    "Magnesium",
    "Manganese",
    "Mercury",
    "Molybdenum",
    "Nickel",
    "Petroleum",
    "REE",
    "Silver",
    "Tin",
    "Titanium",
    "Tungsten",
    "Uranium",
    "Zinc",
    "Zirconium",
    "NG",
    "WGI",
    "Price",
]
    
db = dbFolder+'/'+Database
# Check if the database exists and fetch the required tables
try:
    result = execute_query("SELECT name FROM sqlite_master WHERE type='table';", db_path=db)
    table_names = [row[0] for row in result]
except Exception as e:
    print(e)
    print("Unable to verify if the database contains the required tables")
    raise FileNotFoundError

# check if all the tables in the list are present in the database
missingTables = []
for table_name in Tables:
    if table_name not in table_names:
        missingTables.append(table_name)
    else:
        pass

# If there are missing tables, raise an error
if len(missingTables) > 0:
    print(f"The following tables are missing from the database: {missingTables}")
else:
    print("Database found!")


# Test fail variables
LOGFAIL, DBIMPORTFAIL = False, False

# Create a log file for init function
"""
Creating a log file for the init not to mix with the log of the main function. 
Logging is a sophisticated module that allows to record values or strings into 
a defined format. The required format is altered with the function basicConfig
as declared below.
Do not modify the path for the logs folder unless you specifically need
it elsewhere. Modify the alert level depending on requirements for debugging. 
"""

Filename = "Log_File_{:%Y-%m-%d(%H-%M-%S)}.log".format(datetime.now())

log_level = logging.DEBUG
try:
    logging.basicConfig(
        level=log_level,
        format="""%(asctime)s | %(levelname)s | %(threadName)-10s |
          %(filename)s:%(lineno)s - %(funcName)20s() |
            %(message)s""",
        filename= logfile + "/" + Filename,
        filemode="w",
    )
except:
    # it is imperative that the log file work before running the main code.
    LOGFAIL = True
    print("Cannot create log file!")
    raise Exception
# Function to extract the tables into a dictionary
def extract_tables_to_df(db_path, table_names):
    # Create a dictionary to store the extracted tables
    tables = {}

    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Loop through the table names and extract each table as a DataFrame
    for table_name in table_names:
        query = f"SELECT * FROM {table_name}"
        table_df = pd.read_sql_query(query, conn)

        # Add the table DataFrame to the tables dictionary with the table name as the key
        tables[table_name] = table_df

    # Close the database connection
    conn.close()

    # Return the tables dictionary
    return tables

# verify if output database exists else create it
try:
    sqlstatement = """CREATE TABLE IF NOT EXISTS "recordData" (
    	"id"	INTEGER,
    	"country"	TEXT,
    	"resource"	TEXT,
    	"year"	INTEGER,
    	"recycling_rate"	REAL,
    	"scenario"	REAL,
    	"geopolrisk"	REAL,
    	"hhi"	REAL,
    	"wta"	REAL,
    	"geopol_cf"	REAL,
    	"resource_hscode"	REAL,
    	"iso"	TEXT,
        "log_ref" TEXT,
    	PRIMARY KEY("id")
    );"""
    execute_query(sqlstatement)
except Exception as e:
    logging.debug(e)

# Extract the tables into a dictionary
try:
    tables = extract_tables_to_df(db, Tables)
except Exception as e:
    logging.debug(e)
    raise Exception

_production = tables
_reporter = tables["Country_ISO"]
_price = tables["Price"]
_commodity = tables["commodityHS"]
_wgi = tables["WGI"]
regionslist = {}
