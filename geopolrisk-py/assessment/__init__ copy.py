import sqlite3, pandas as pd, getpass, logging, os
from datetime import datetime
from pathlib import Path
import yaml

# from .Exceptions.warningsgprs import *

logging = logging
__all__ = ["core", "operations", "gcalc", "gprsplots", "utils", "tests", "main"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "Beta"
__version__ = "3.0.1"
__data__ = "30 September 2023"

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
    # Define a function named load_config that takes a file_path as an argument
    def load_config(file_path):
        try:
            # Try to open the specified file for reading
            with open(file_path, "r") as config_file:
                # Use yaml.safe_load to parse the YAML content from the file
                config_data = yaml.safe_load(config_file)
                # Check if config_data is not None (i.e., it contains valid data)
                if config_data is not None:
                    # If valid data is found, return it as a Python dictionary
                    return config_data
                else:
                    # If the data is empty or invalid, raise a ValueError
                    raise ValueError("Config file is empty or contains invalid data.")

        # Handle the case where the file is not found
        except FileNotFoundError:
            print("Config file not found.")
            return None

        # Handle any other exceptions that might occur during file handling or parsing
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    # Example usage of the load_config function
    config_file_path = "geopolrisk-py/assessment/meta.yaml"

    # Call the load_config function with the specified config file path
    config_data = load_config(config_file_path)

    # Check if config_data contains valid data
    if config_data:
        # Access the loaded data from the configuration dictionary
        Tables = config_data.get("Tables", [])
        regions_list = config_data.get("regionslist", {})
        Output = config_data.get("Output", "")
        Database = config_data.get("Database", "")
        BACI = config_data.get("BACI", "")
        OutputFolder = config_data.get("OutputFolder", "")
    else:
        # Handle the case where an error occurred during data loading
        print("Error loading the configuration data.")
        raise Exception("Error loading the configuration data.")
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
    regionslist = regions_list


instance = database()

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
