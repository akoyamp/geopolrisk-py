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


import sqlite3, pandas as pd, logging, os, time
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
import shutil

logging = logging

databases = None


def execute_query(query, db_path="", params=None, retries=5, delay=0.1):
    """
    Execute an SQL query on a SQLite database with retry mechanism for locked database.

    Args:
        query (str): SQL query to execute.
        db_path (str): Path to the SQLite database file.
        params (tuple or list, optional): Parameters for the SQL query.
        retries (int, optional): Number of retries if the database is locked. Default is 5.
        delay (float, optional): Delay between retries in seconds. Default is 0.1 seconds.

    Returns:
        list or None: Query results for SELECT queries, None for others.
    """
    attempts = 0
    while attempts <= retries:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            is_select_query = query.strip().lower().startswith("select")

            if is_select_query:
                cursor.execute(query, params or [])
                results = cursor.fetchall()
            else:
                cursor.execute(query, params or [])
                results = None

            conn.commit()
            conn.close()
            if is_select_query:
                return results

            break  # Exit loop if query succeeds

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                attempts += 1
                if attempts > retries:
                    raise Exception(
                        f"Database is locked after {retries} retries."
                    ) from e
                time.sleep(delay)  # Wait before retrying
            else:
                raise  # Raise other operational errors immediately


class database:
    Output = "Datarecords.db"  # Database file to store the GeoPolRisk values
    _dwmd = "world_mining_data.db"  # World Mining Data Database
    _dwgi = "wgi.db"  # World Governance Indicator Database
    _dbaci = "baci.db"  # Trade data from BACI HS92
    _company_data_excel = "Company data.xlsx"  # Company data Excel file

    def __init__(self):
        pass

    """
    Creating a log object and file for logging the errors
    """

    def init_logging(log_directory):
        Filename = "Log_File_{:%Y-%m-%d(%H-%M-%S)}.log".format(datetime.now())
        log_level = logging.DEBUG
        try:
            logging.basicConfig(
                level=log_level,
                format="""%(asctime)s | %(levelname)s | %(threadName)-10s |
                %(filename)s:%(lineno)s - %(funcName)20s() |
                    %(message)s""",
                filename=log_directory + "/" + Filename,
                filemode="w",
            )
        except:
            print("Cannot create log file!")

    """
    Creates the necessary directories in the user's Documents folder if they do not already exist.
    """
    try:
        # Define the main directory path
        directory = os.path.join(Path.home(), "Documents/geopolrisk")
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

        # Define the logs directory path
        logs_directory = os.path.join(directory, "logs")
        if not os.path.exists(logs_directory):
            os.makedirs(logs_directory)
            print(f"Created directory: {logs_directory}")

        # init logging
        init_logging(logs_directory)

        # Define the databases directory path
        databases_directory = os.path.join(directory, "databases")
        if not os.path.exists(databases_directory):
            os.makedirs(databases_directory)
            logging.info(f"Created directory: {databases_directory}")

        # Define the output directory path
        output_directory = os.path.join(directory, "output")
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            logging.info(f"Created directory: {output_directory}")

    except Exception as e:
        print(f"Unable to create directories: {e}")
        logging.error(f"Unable to create directories: {e}")
        raise FileNotFoundError

    # path to the database files - "lib" directory in the parent directory of the current file
    directory_databases = os.path.join(Path(__file__).parent.resolve().parent, "lib")

    """
    Copies the 'Company data.xlsx' file from the lib directory to the databases directory
    if it does not already exist in the databases directory.
    """
    try:
        # Define the source and destination paths
        source_path = os.path.join(
            Path(__file__).parent.resolve().parent, "lib", _company_data_excel
        )
        destination_path = os.path.join(databases_directory, _company_data_excel)

        # Check if the source file exists
        if not os.path.isfile(source_path):
            logging.warning(f"Source file not found: {source_path}")
        # Check if the destination file already exists
        elif os.path.isfile(destination_path):
            logging.info(f"Destination file already exists: {destination_path}")
        # Copy the file
        else:
            shutil.copy2(source_path, destination_path)
            logging.info(
                f"Copied file {_company_data_excel} from {source_path} to {destination_path}"
            )

    except Exception as e:
        logging.error(f"Unable to copy {_company_data_excel}: {e}")

    """
    Checks if the required database files are present in the databases directory "lib".
    """
    directory_databases = os.path.join(Path(__file__).parent.resolve().parent, "lib")

    if not os.path.isfile(os.path.join(directory_databases, _dwmd)):
        logging.warning(
            f"Database file {_dwmd} not found! Copy the required database files into the folder {directory_databases}."
        )
    if not os.path.isfile(os.path.join(directory_databases, _dwgi)):
        logging.warning(
            f"Database file {_dwgi} not found! Copy the required database files into the folder {directory_databases}."
        )
    if not os.path.isfile(os.path.join(directory_databases, _dbaci)):
        logging.warning(
            f"Database file {_dbaci} not found! Copy the required database files into the folder {directory_databases}."
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
        "Steam Coal",
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
                desc=f"Reading table/s {table_names} from the library database {db_path}.",
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
                                -- where bacitab.k IN ('760110', '260400') -- only for a better test performance - filter by hscode's
                                -- where 1=2 -- only for a better test performance - no results
                            """
                    # Test-Query - read the vieww
                    # query = f"""
                    #         select
                    #         *
                    #         from v_baci_trade_with_wgi bacitab
                    #         --where cmdCode = '260400'
                    #         """
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
    Database_wmd_path = os.path.join(directory_databases, _dwmd)
    if check_db_tables(Database_wmd_path, Tables_world_mining_data):
        tables_world_mining_data = extract_tables_to_df(
            Database_wmd_path, Tables_world_mining_data
        )
    else:
        print("Error while reading the World Mining Data db")
        raise (FileNotFoundError)

    # Check if the wgi.db database exists and fetch the required tables
    Database_wgi_path = os.path.join(directory_databases, _dwgi)
    if check_db_tables(Database_wgi_path, Tables_wgi):
        tables_wgi = extract_tables_to_df(Database_wgi_path, Tables_wgi)
    else:
        print("Error while reading the WGI db")
        raise (FileNotFoundError)

    # Check if the baci.db exists and fetch the required tables
    Database_baci_path = os.path.join(directory_databases, _dbaci)
    if check_db_tables(Database_baci_path, Tables_baci):
        tables_baci = extract_tables_to_df(Database_baci_path, Tables_baci)
    else:
        print("Error while reading the BACI db")
        raise (FileNotFoundError)

    #############################################################
    ## Extracting the dataframes into the individual variables ##
    #############################################################

    production = tables_world_mining_data
    # production["HS Code Map"] = (
    #     production["HS Code Map"]
    #     .loc[production["HS Code Map"]["HS Code"] != "Not Available"]
    #     .dropna(subset=["Symbol"])
    # )
    filtered_production = production["HS Code Map"].loc[
        production["HS Code Map"]["HS Code"] != "Not Available"
    ]
    filtered_production = filtered_production.dropna(subset=["Symbol"])
    production["HS Code Map"] = filtered_production

    baci_trade = tables_baci["baci_trade"]
    wgi = tables_wgi["Normalized"]

    regionslist = {}
    regional = False
    regionslist["EU"] = [
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
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


if databases == None:
    databases = database()
