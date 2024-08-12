# Copyright (C) 2024 University of Bordeaux, CyVi Group & University of Bayreuth,
# Ecological Resource Technology & Anish Koyamparambath, Christoph Helbig, Thomas Schraml
# This file is part of geopolrisk-py library.
# geopolrisk-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# geopolrisk-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with geopolrisk-py.  If not, see <https://www.gnu.org/licenses/>.


import sqlite3, pandas as pd, logging, os
from tqdm import tqdm
from datetime import datetime
from pathlib import Path

logging = logging
__all__ = ["core", "console", "utils", "main"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "alpha"
__version__ = "2"
__data__ = "10 July 2024"

databases = None

# Generic SQL function (multi use)
def execute_query(query, db_path=""):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    is_select_query = query.strip().lower().startswith("select")
    if is_select_query:
        cursor.execute(query)
        results = cursor.fetchall()
    else:
        cursor.execute(query)
        results = None
    conn.commit()
    conn.close()
    if is_select_query:
        return results


class database:
    Output = "Datarecords.db"  # Database file to store the GeoPolRisk values
    _dwmd = "world_mining_data.db"  # World Mining Data Database
    _dwgi = "wgi.db"  # World Governance Indicator Database
    _dbaci = "baci.db"  # Trade data from BACI HS92
    def __init__(self):
        pass
    """
    The first iteration runs the init files that creates a folder 
    "geopolrisk" in the documents folder of the operating system 
    and all the required subfolders. The user must then copy all 
    the required database files into the "databases" folder in 
    the newly created "geopolrisk".
    """
    try:
        directory = os.path.join(Path.home(), "Documents/geopolrisk")
        if not os.path.exists(os.path.join(Path.home(), "Documents/geopolrisk")):
            os.makedirs(os.path.join(Path.home(), "Documents/geopolrisk"))

        if not os.path.exists(os.path.join(Path.home(), "Documents/geopolrisk/logs")):
            os.makedirs(os.path.join(Path.home(), "Documents/geopolrisk/logs"))

        if not os.path.exists(
            os.path.join(Path.home(), "Documents/geopolrisk/databases")
        ):
            os.makedirs(os.path.join(Path.home(), "Documents/geopolrisk/databases"))

        if not os.path.exists(os.path.join(Path.home(), "Documents/geopolrisk/output")):
            os.makedirs(os.path.join(Path.home(), "Documents/geopolrisk/output"))
    except Exception as e:
        print(f"Unable to create directories {e}")
        raise FileNotFoundError

    if not os.path.isfile(os.path.join(directory + "/databases/", _dwmd)):
        print(
            "Database files not found! Copy the required database files into the folder."
        )

    ##############################################
    ##   READING TABLES FROM THE DATABASE FILES ##
    ##############################################

    Tables_world_mining_data = [
        "Aluminium",
        "Antimony",
        "Arsenic",
        "Asbestos",
        "Baryte",
        "Bauxite",
        "Bentonite",
        "Beryllium (conc.)",
        "Bismuth",
        "Boron Minerals",
        "Cadmium",
        "Chromium (Cr2O3)",
        "Cobalt",
        "Coking Coal",
        "Copper",
        "Diamonds (Gem)",
        "Diamonds (Ind)",
        "Diatomite",
        "Feldspar",
        "Fluorspar",
        "Gallium",
        "Germanium",
        "Gold",
        "Graphite",
        "Gypsum and Anhydrite",
        "Indium",
        "Iron (Fe)",
        "Kaolin (China-Clay)",
        "Lead",
        "Lignite",
        "Lithium (Li2O)",
        "logging",
        "Magnesite",
        "Manganese",
        "Mercury",
        "Molybdenum",
        "Natural Gas",
        "Nickel",
        "Niobium (Nb2O5)",
        "Oil Sands (part of Petroleum)",
        "Oil Shales",
        "Palladium",
        "Perlite",
        "Petroleum",
        "Phosphate Rock (P2O5)",
        "Platinum",
        "Potash (K2O)",
        "Rare Earths (REO)",
        "Rhenium",
        "Rhodium",
        "Salt (rock, brines, marine)",
        "Selenium",
        "Silver",
        "Steam Coal ",
        "Sulfur (elementar & industrial)",
        "Talc, Steatite & Pyrophyllite",
        "Tantalum (Ta2O5)",
        "Tellurium",
        "Tin",
        "Titanium (TiO2)",
        "Tungsten (W)",
        "Uranium (U3O8)",
        "Vanadium (V)",
        "Vermiculite",
        "Zinc",
        "Zircon",
        "Country_ISO",
        "HS Code Map",
    ]
    Tables_wgi = [
        "Normalized",
    ]
    Tables_baci = [
        "baci_trade",
    ]

    # Function to check if database exists and fetch the required tables
    def check_db_tables(db, table_names):
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            cursor.execute(query)
            result = cursor.fetchall()
            table_names = [row[0] for row in result]
        except Exception as e:
            print(f"Unable to verify if the database contains the required tables {e}")
            raise FileNotFoundError

        # check if all the tables in the list are present in the database
        missingTables = []
        for table_name in table_names:
            if table_name not in table_names:
                missingTables.append(table_name)
            else:
                pass

        # If there are missing tables, raise an error
        if len(missingTables) > 0:
            print(
                f"The following tables are missing from the database: {missingTables}"
            )
            return False
        else:
            return True

    ###############################################
    ## Extracting TABLES FROM THE DATABASE FILES ##
    ###############################################

    def extract_tables_to_df(db_path, table_names):
        try:
            tables = {}
            conn = sqlite3.connect(db_path)
            for table_name in tqdm(
                table_names,
                desc="Reading tables from the library database.",
            ):
                if table_name == "baci_trade":
                    query = f"""
                            select 
                                bacitab.t as period,
                                bacitab.j as reporterCode,
                                (SELECT cc.country_name FROM country_codes_V202401b cc WHERE bacitab.j = cc.country_code) AS reporterDesc,
                                (SELECT cc.country_iso3 FROM country_codes_V202401b cc WHERE bacitab.j = cc.country_code) AS reporterISO,
                                bacitab.i as partnerCode,
                                (SELECT cc.country_name FROM country_codes_V202401b cc WHERE bacitab.i = cc.country_code) AS partnerDesc,
                                (SELECT cc.country_iso3 FROM country_codes_V202401b cc WHERE bacitab.i = cc.country_code) AS partnerISO,
                                bacitab.k as cmdCode,
                                REPLACE(TRIM(bacitab.q), 'NA', 0) as qty,
	                            REPLACE(TRIM(bacitab.v),'NA', 0) as cifvalue,
                                (SELECT vwyc.wgi FROM v_wgi_year_country vwyc WHERE bacitab.t = vwyc.Year and bacitab.i = vwyc.country_code) AS partnerWGI
                            from baci_trade bacitab
                            """
                else:
                    query = f"SELECT * FROM '{table_name}'"
                table_df = pd.read_sql_query(query, conn)
                tables[table_name] = table_df
            conn.close()
        except Exception as e:
            print(f"Error to read tables {table_names} from database {db_path} - {e}")
            conn.close()
        return tables

    # Check if the world_mining_data.db database exists and fetch the required tables
    Database_wmd_path = directory + "/databases/" + _dwmd
    if check_db_tables(Database_wmd_path, Tables_world_mining_data):
        tables_world_mining_data = extract_tables_to_df(
            Database_wmd_path, Tables_world_mining_data
        )
    else:
        print("Error while reading the World Mining Data db")
        raise (FileNotFoundError)

    # Check if the wgi.db database exists and fetch the required tables
    Database_wgi_path = directory + "/databases/" + _dwgi
    if check_db_tables(Database_wgi_path, Tables_wgi):
        tables_wgi = extract_tables_to_df(Database_wgi_path, Tables_wgi)
    else:
        print("Error while reading the WGI db")
        raise (FileNotFoundError)

    # Check if the baci.db exists and fetch the required tables
    Database_baci_path = directory + "/databases/" + _dbaci
    if check_db_tables(Database_baci_path, Tables_baci):
        tables_baci = extract_tables_to_df(Database_baci_path, Tables_baci)
    else:
        print("Error while reading the BACI db")
        raise (FileNotFoundError)

    #############################################################
    ## Extracting the dataframes into the individual variables ##
    #############################################################

    production = tables_world_mining_data
    baci_trade = tables_baci["baci_trade"]
    wgi = tables_wgi["Normalized"]

    regionslist = {}
    regional = False
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

def get_databases():
    global databases
    if databases == None:
        databases = (
            database()
        )
    return databases

###########################################################
## Creating a log object and file for logging the errors ##
###########################################################

Filename = "Log_File_{:%Y-%m-%d(%H-%M-%S)}.log".format(datetime.now())
log_level = logging.DEBUG
try:
    logging.basicConfig(
        level=log_level,
        format="""%(asctime)s | %(levelname)s | %(threadName)-10s |
          %(filename)s:%(lineno)s - %(funcName)20s() |
            %(message)s""",
        filename=databases.directory + "/logs/" + Filename,
        filemode="w",
    )
except:
    print("Cannot create log file!")


#if __name__ == "__init__":
#     databases = (
#     database()
# )  # Important object that saves all the variables in the class database to be used in the library