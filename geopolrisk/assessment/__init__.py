# Copyright (C) 2023 University of Bordeaux, CyVi Group & Anish Koyamparambath
# This file is part of geopolrisk-py library.
#
# geopolrisk-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# geopolrisk-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with geopolrisk-py.  If not, see <https://www.gnu.org/licenses/>.

import sqlite3, pandas as pd, getpass, logging, os
from datetime import datetime
from pathlib import Path

# from .Exceptions.warningsgprs import *

logging = logging
__all__ = ["core", "operations", "console", "gprsplots", "utils", "tests", "main"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "release"
__version__ = "1"
__data__ = "10 March 2023"

hard_dependencies = ("pandas", "scipy", "matplotlib")
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


# Function to use sqlite3
def execute_query(query, db_path=""):
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


class database:
    # Global Variables
    Output = "Datarecords.db"
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
        print(f"Unable to create directories {e}")
        raise FileNotFoundError

    # Verify that the file exists else input the correct file path
    if not os.path.isfile(os.path.join(dbFolder, Database)):
        folder_path = input("The file doesn't exist. Please enter a folder path: ")

    # Verify if the database contains the required tables
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
        "Crude_Oil",
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

    db = dbFolder + "/" + Database
    # Check if the database exists and fetch the required tables
    try:
        result = execute_query(
            "SELECT name FROM sqlite_master WHERE type='table';", db_path=db
        )
        table_names = [row[0] for row in result]
    except Exception as e:
        print(f"Unable to verify if the database contains the required tables {e}")
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
        pass

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
        	"index"	INTEGER,
            "id" TEXT NOT NULL,
        	"country"	TEXT,
        	"resource"	TEXT,
        	"year"	INTEGER,
        	"recycling_rate"	REAL,
        	"scenario"	REAL,
        	"geopolrisk"	REAL,
        	"hhi"	REAL,
        	"wta"	REAL,
        	"geopol_cf"	REAL,
        	"resource_hscode"	INTEGER,
        	"iso"	INTEGER,
            "log_ref" TEXT,
        	PRIMARY KEY("index")
        );"""
        execute_query(sqlstatement, db_path=exportfile + "/" + Output)
    except Exception as e:
        print(f"Could not create the output database {e}")

    # Extract the tables into a dictionary
    try:
        tables = extract_tables_to_df(db, Tables)
    except Exception as e:
        print(f"Could not extract the tables {e}")

    production = tables
    reporter = tables["Country_ISO"]
    price = tables["Price"]
    commodity = tables["commodityHS"]
    wgi = tables["WGI"]
    regionslist = {}
    regionslist["EU"] = [
        "Austria",
        "Belgium",
        "Belgium-Luxembourg",
        "Bulgaria",
        "Croatia",
        "Czechia",
        "Czechoslovakia",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
        "Fmr Dem. Rep. of Germany",
        "Fmr Fed. Rep. of Germany",
        "Germany",
        "Greece",
        "Hungary",
        "Ireland",
        "Italy",
        "Latvia",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Netherlands",
        "Poland",
        "Portugal",
        "Romania",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
    ]


instance = database()


class outputDF:
    columns = [
        "Year",
        "Resource",
        "Country",
        "Recycling Rate",
        "Recycling Scenario",
        "Risk",
        "GeoPolRisk Characterization Factor",
        "HHI",
        "Weighted Trade AVerage",
    ]
    outputList = []


outputdf = outputDF()
# Test fail variables
LOGFAIL, DBIMPORTFAIL = False, False

# Create a log file for init function

Filename = "Log_File_{:%Y-%m-%d(%H-%M-%S)}.log".format(datetime.now())

log_level = logging.DEBUG
try:
    logging.basicConfig(
        level=log_level,
        format="""%(asctime)s | %(levelname)s | %(threadName)-10s |
          %(filename)s:%(lineno)s - %(funcName)20s() |
            %(message)s""",
        filename=instance.logfile + "/" + Filename,
        filemode="w",
    )
except:
    # it is imperative that the log file work before running the main code.
    LOGFAIL = True
    print("Cannot create log file!")
