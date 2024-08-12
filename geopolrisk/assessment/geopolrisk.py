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

# __init__.py imports
from datetime import datetime
from pathlib import Path
import sqlite3, logging
# utils.py imports
import pandas as pd, os, glob
# core.py imports
from typing import Union

# from .__init__ import databases, logging

# main.py imports
import itertools
from tqdm import tqdm

###############
# __init__.py #
###############

logging = logging
__all__ = ["core", "console", "utils", "main"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "alpha"
__version__ = "2"
__data__ = "10 July 2024"

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

databases = (
    database()
)

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



############
# utils.py #
############

tradepath = None
db = databases.directory + "/output"

########################################
##   Utility functions --  GeoPolRisk ##
########################################


def replace_func(x):
    if isinstance(x, float):
        return x
    else:
        if x.strip() == "NA" or x is None or isinstance(x, type(None)):
            return 0
        else:
            return x

def cvtresource(resource, type="HS"):
    """
    Type can be either 'HS' or 'Name'
    """
    MapHSdf = databases.production["HS Code Map"]
    if type == "HS":
        if resource in MapHSdf["ID"].tolist():
            return MapHSdf.loc[MapHSdf["ID"] == resource, "HS Code"].iloc[0]
        else:
            try:
                resource = int(resource)
            except:
                print("Entered raw material does not exist in our database!")
                logging.debug(
                    f"Error while fetching raw material. Entered raw material = {resource}"
                )
                raise ValueError
            if str(resource) in MapHSdf["HS Code"].tolist():
                return int(resource)
    elif type == "Name":
        try:
            resource = int(resource)
        except:
            print("Entered raw material does not exist in our database!")
            logging.debug(
                f"Error while fetching raw material. Entered raw material = {resource}"
            )
            resource = str(resource)
        if str(resource) in MapHSdf["HS Code"].astype(str).tolist():
            return MapHSdf.loc[MapHSdf["HS Code"] == str(resource), "ID"].iloc[0]
        elif resource in MapHSdf["ID"].tolist():
            return resource
        else:
            print("Entered raw material does not exist in our database!")
            logging.debug(
                f"Error while fetching raw material. Entered raw material = {resource}"
            )
            raise ValueError
def cvtcountry(country, type="ISO"):
    """
    Type can be either 'ISO' or 'Name'
    """
    MapISOdf = databases.production["Country_ISO"]
    if type == "ISO":
        if country in MapISOdf["Country"].tolist():
            return MapISOdf.loc[MapISOdf["Country"] == country, "ISO"].iloc[0]
        else:
            try:
                country = int(country)
            except:
                print("Entered country does not exist in our database!")
                logging.debug(
                    f"Error while fetching country. Entered country = {country}"
                )
                raise ValueError
            if country in MapISOdf["ISO"].astype(int).tolist():
                return country
    elif type == "Name":
        try:
            country = int(country)
        except:
            print("Entered country does not exist in our database!")
            logging.debug(
                    f"Error while fetching country. Entered country = {country}"
                )
            country = str(country)
        if country in MapISOdf["ISO"].astype(int).tolist():
            return MapISOdf.loc[MapISOdf["ISO"] == country, "Country"].iloc[0]
        elif country in MapISOdf["Country"].tolist():
            return country
        else:
            print("Entered country does not exist in our database!")
            logging.debug(
                f"Error while fetching country. Entered country = {country}"
            )
            raise ValueError
        

def sumproduct(A: list, B: list):
    return sum(i * j for i, j in zip(A, B))


def create_id(HS, ISO, Year):
    return str(HS) + str(ISO) + str(Year)


# Verify if the calculation is already stored in the database to avoid recalculation
def sqlverify(DBID):
    try:
        sql = f"SELECT * FROM recordData WHERE id = '{DBID}';"
        row = execute_query(
            f"SELECT * FROM recordData WHERE id = '{DBID}';",
            db_path=db,
        )
    except Exception as e:
        logging.debug(f"Database error in sqlverify - {e}, {sql}")
        row = None
    if not row:
        return False
    else:
        return True


def createresultsdf():
    dbpath = databases.directory + "/output/" + databases.Output

    # Columns for the dataframe
    Columns = [
        "DBID",
        "Country [Economic Entity]",
        "Raw Material",
        "Year",
        "GeoPolRisk Score",
        "GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]",
        "HHI",
        "Import Risk",
        "Price",
    ]
    df = pd.DataFrame(columns=Columns)
    SQLQuery = """CREATE TABLE IF NOT EXISTS "recordData" (
            "DBID"	INTEGER,
        	"Country [Economic Entity]"	TEXT,
        	"Raw Material"	TEXT,
        	"Year"	INTEGER,
        	"GeoPolRisk Score"	REAL,
        	"GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"	REAL,
        	"HHI"	REAL,
        	"Import Risk" REAL,
        	"Price"	INTEGER,
        	PRIMARY KEY("DBID")
        );"""
    row = execute_query(
        SQLQuery,
        db_path=dbpath,
    )
    return df


###################################################
##   Extrade trade data functions --  GeoPolRisk ##
###################################################


def getbacidata(
    period: float, country: float, commoditycode: float, data=databases.baci_trade
):
    """
    get the baci-trade-data from the baci_trade dataframe
    """
    period = str(period)
    country = str(country)
    commoditycode = str(commoditycode)
    df_query = f"(period == '{period}') & (reporterCode == '{country}') & (cmdCode == '{commoditycode}')"
    baci_data = data.query(df_query)
    """
    The dataframe is structured as follows:
    'period' -> The year of the trade recorded
    'reporterCode' -> The ISO 3 digit code of the reporting country
    'reporterISO' -> The ISO code of the reporting country
    'reporterDesc' -> The name of the reporting country
    'partnerCode' -> The ISO 3 digit code of the partner country
    'partnerISO' -> The ISO code of the partner country
    'partnerDesc' -> The name of the partner country
    'cmdCode' -> The 6 digit commodity code (HS92)
    'qty' -> The trade quantity in 1000 kilograms
    'cifvalue' -> The value of the traded quantity in 1000 USD
    'partnerWGI' -> The WGI political stability and absence of violence indicator (Normalized) for the partner country
    """
    baci_data.loc[:, "qty"] = baci_data["qty"].apply(replace_func).astype(float)
    baci_data.loc[:, "cifvalue"] = baci_data["cifvalue"].apply(replace_func).astype(float)
    if baci_data is None or isinstance(baci_data, type(None)) or len(baci_data) == 0:
        logging.debug(
            f"Problem with get the baci-data - {baci_data} - period == '{period}') - reporterCode == '{country}' - cmdCode == '{commoditycode}'"
        )
        baci_data = None
    return baci_data


def aggregateTrade(
    period: float, country: list, commoditycode: float, data=databases.baci_trade
):
    """
    The function is only to aggregate the trade for each partner country in the region.
    """
    def wgi_func(x):
        if isinstance(x, float):
            return x
        else:
            if x is None or isinstance(x, type(None)) or x.strip() == "NA":
                return 0.5
            else:
                return x
    SUMQTY, SUMVAL, SUMNUM = [], [], []
    for i, n in enumerate(country):
        baci_data = getbacidata(
            period, cvtcountry(n, type="ISO"), commoditycode, data=databases.baci_trade
        )
        if baci_data is None:
            QTY, WGI, VAL = [0], [0], [0]
        else:
            QTY = baci_data["qty"].tolist()
            WGI = baci_data["partnerWGI"].apply(wgi_func).astype(float).tolist()
            VAL = baci_data["cifvalue"].tolist()
        SUMQTY.append(sum(QTY))
        SUMVAL.append(sum(VAL))
        SUMNUM.append(sumproduct(QTY, WGI))

    Price = sum(SUMVAL) / sum(SUMQTY)
    """
    The function returns the numerator of the import risk, 
    The total trade for the region,
    The price calculated with the total value for all the countries in the region &
    the total quantity traded with the countries in the region.
    """
    return sum(SUMNUM), sum(SUMQTY), Price


###################################################
## Converting trade data into a usable dataframe ##
###################################################


def transformdata():
    folder_path = databases.directory + "/databases"
    file_name = "Company data.xlsx"
    file_path = glob.glob(os.path.join(folder_path, file_name))
    """
    The template excel file has the following headers
    'Metal': Specify the type of metal.
    'Country of Origin': Indicate the country where the metal was sourced.
    'Quantity (kg)': Enter the quantity of metal imported from each country.
    'Value (USD)': Value of the metal of the quantity imported.
    'Year': The year of the trade
    'Additional Notes': Include any additional relevant information.
    """
    Data = pd.read_excel(file_path, sheet_name="Template")
    HS_Code = []
    for resource in Data["Metal"].tolist():
        HS_Code.append(cvtresource(resource, type="HS"))
    ISO = []
    for country in Data["Country of Origin"].tolist():
        ISO.append(cvtcountry(country, type="HS"))
    MapWGIdf = databases.wgi
    wgi = []
    for i, iso in enumerate(ISO):
        try:
            wgi.append(
                MapWGIdf.loc[MapWGIdf["country_code"] == iso, Data["Year"].tolist()[i]]
            )
        except:
            print("The entered year is not available in our database!")
            logging.debug(f"Error while fetching the wgi, the ISO is {iso}")
    try:
        Data["Quantity (kg)"] = [
            float(x) * 1000 for x in Data["Quantity (kg)"].tolist()
        ]
    except:
        print(
            "Error in converting values to float, check the formatting in the Template"
        )
        logging.debug("Excel file not formatted correctly! numerical must be numbers")
        raise ValueError
    try:
        Data["Value (USD)"] = [float(x) * 1000 for x in Data["Value (USD)"].to_list()]
    except:
        print(
            "Error in converting values to float, check the formatting in the Template"
        )
        logging.debug("Excel file not formatted correctly! numerical must be numbers")
        raise ValueError
    Data["partnerISO"] = ISO
    Data["partnerWGI"] = wgi
    Data["cmdCode"] = HS_Code
    Data["reporterDesc"] = ["Company"] * len(ISO)
    Data["reporterISO"] = [999] * len(ISO)

    Data.columns = [
        "Commodity",
        "partnerDesc",
        "qty",
        "cifvalue",
        "period",
        "Notes",
        "partnerISO",
        "partnerWGI",
        "cmdCode",
        "reporterDesc",
        "reporterISO",
    ]
    return Data


########################################################
##   Extrade production data functions --  GeoPolRisk ##
########################################################
def getProd(resource):
    """
    The dictionary have a unique identifier that is accessed through a table called 'HS Code Map'
    The mapping table has the following structure
    'Sheet_name' -> The name of the table corresponding to the raw material
    'Category - WMD' -> The world mining data categorization of the raw material
    'ID' -> The name of the raw material (metals and minerals)
    'HS Code' -> The HS Code mapping of raw material
    'Description' -> The description of the HS code
    'Symbol' -> Element equivalent to the raw material
    """
    Mapdf = databases.production["HS Code Map"]
    if resource in Mapdf["ID"].tolist():
        MappedTableName = Mapdf.loc[Mapdf["ID"] == resource, "Sheet_name"]
    elif str(resource) in Mapdf["HS Code"].tolist() and resource != "Not Available":
        MappedTableName = Mapdf.loc[Mapdf["HS Code"] == str(resource), "Sheet_name"]
    else:
        print("Entered raw material does not exist in our database!")
        logging.debug(
            f"Error while fetching raw material. Entered raw material = {resource}"
        )
        raise ValueError
    
    """
    The returned dataframe is mapped based on the input resource.
    The output dataframe has the following structure.
    'Country' -> The country name, according to the BACI
    'Country_Code' -> The numeric ISO country code
    'Country_ISO' -> The ISO code of the country
    '2018', '2019', '2020', '2021', '2022' -> The production quantity of each raw material
    'unit' -> The units of the value
    'data_source' -> The data source of each value point
    """
 
    result = databases.production[MappedTableName.iloc[0]]
    return result


########################################################
##   Define multiple regions --  GeoPolRisk ##
########################################################


def regions(*args):
    trackregion = 0
    if len(args) != 0:
        for key, value in args[0].items():
            if type(key) is not str and type(value) is not list:
                logging.debug(
                    "Dictionary input to regions does not match required type."
                )
                return None
            Print_Error = [
                x
                for x in value
                if str(x) not in databases.production["Country_ISO"]["Country"].tolist()
                and str(x)
                not in databases.production["Country_ISO"]["ISO"].astype(str).tolist()
            ]
            if len(Print_Error) != 0:
                logging.debug(
                    "Error in creating a region! "
                    "Following list of countries not"
                    " found in the ISO list {}. "
                    "Please conform with the ISO list or use"
                    " 3 digit ISO country codes.".format(Print_Error)
                )
                return None
            else:
                trackregion += 1
                databases.regionslist[key] = value
    if trackregion > 0:
        databases.regional = True
    # The function must be called before calling any other functions in the core
    # module. The following lines populate the region list with all the countries
    # in the world including EU defined in the init file.
    for i in databases.production["Country_ISO"]["Country"].tolist():
        if i in databases.regionslist.keys():
            logging.debug("Country or region already exists cannot overwrite.")
        databases.regionslist[i] = [i]


###########
# core.py #
###########

def HHI(resource: Union[str, int], year: int, country: str):
    """
    Calculates the Herfindahl-Hirschman index of production of resources
    which is normalized to the scale of 0 - 1.
    The dataframe is fetched from a utlity function.
    """
    proddf = getProd(resource)
    proddf = proddf[proddf["Country_Code"] != "DELETE"]
    prod_year = proddf[str(year)].tolist()
    HHI_Num = sumproduct(prod_year, prod_year)
    try:
        hhi = HHI_Num / (sum(prod_year) * sum(prod_year))
    except:
        logging.debug(f"Error while calculating the HHI. Resource : {resource}, year : {year}")
        raise ValueError
    if cvtcountry(country, type="Name") in proddf["Country"].tolist():
        try:
            ProdQty = float(proddf.loc[proddf["Country"] == cvtcountry(country, type="Name"), str(year)].iloc[0])
        except:
            logging.debug(f"Error while extracting the production quantity, Resource : {resource}, Year: {year}, Country: {country} ")
            raise ValueError
    else:
        ProdQty = 0
    
    if proddf["unit"].tolist()[0] == "kg":
        ProdQty = ProdQty / 1000
    elif proddf["unit"].tolist()[0] != "metr. t" and proddf["unit"].tolist()[0] != "kg":
        raise ValueError
    elif proddf["unit"].tolist()[0] == "Mio m3":
        """
        1 m³ = 0.8 kg = 0.0008 metr. t
        """
        ProdQty = ProdQty * 0.0008
    """
    The output includes the production quantity of a resource for a country in a given year and the Herfindahl-Hirschman Indexfor that year.
    'ProdQty' : float
    'hhi': float
    """
    return ProdQty, hhi


def importrisk(resource: int, year: int, country: list):
    """
    The second part of the equation of the GeoPolRisk method is referred to as 'import risk'.
    This involves weighting the import quantity with the political stability score.
    The political stability score is derived from the 
    Political Stability and Absence of Violence indicator of the Worldwide Governance Indicators.
    For more information, see Koyamparambath et al. (2024).
    """
    def wgi_func(x):
        """
        For a country whose political stability score is missing, a score of 0.5 is assigned.
        """
        if isinstance(x, float):
            return x
        else:
            if x is None or isinstance(x, type(None)) or x.strip() == "NA":
                return 0.5
            else:
                return x
                  
    if databases.regional != True:
        ctry = cvtcountry(country[0], type="ISO")
        tradedf = getbacidata(year, ctry, resource, data=databases.baci_trade) #Dataframe from the utility function
        QTY = tradedf["qty"].astype(float).tolist()
        WGI = tradedf["partnerWGI"].apply(wgi_func).astype(float).tolist()
        VAL = tradedf["cifvalue"].astype(float).tolist()
        try:
            Price = sum(VAL) / sum(QTY)
            TotalTrade = sum(QTY)
            Numerator = sumproduct(QTY, WGI)
        except:
            logging.debug(f"Error while making calculations. Resource: {resource}, Country: {country}, Year: {year}")
            raise ValueError
    else:
        try:
            Numerator, TotalTrade, Price = aggregateTrade(
                year, country, resource, data=databases.baci_trade
            )
        except:
            logging.debug(f"The inputs for calculating the 'import risk' dont match, Country: {country}")

    """
    'Numerator' : float
    'TotalTrade' : float
    'Price' : float
    """
    return Numerator, TotalTrade, Price


def importrisk_company(resource: int, year: int):
    """
    The 'import risk' for a company differs from that of the country's.
    This data is provided in a template in the output folder.
    The utility function transforms the data into a 
    usable format similar to that of the country-level data.
    """
    tradedf = transformdata()
    df_query = f"(period == '{year}')  & (cmdCode == '{resource}')"
    data = tradedf.query(df_query)
    QTY = data["qty"].tolist()
    WGI = data["partnerWGI"].tolist()
    VAL = data["cifvalue"].tolist()
    try:
        Price = sum(VAL) / sum(QTY)
        TotalTrade = sum(QTY)
        Numerator = sumproduct(QTY, WGI)
    except:
        logging.debug(f"Error while making calculations. Resource: {resource}, Country: Company, Year: {year}")
        raise ValueError
    """
    'Numerator' : float
    'TotalTrade' : float
    'Price' : float
    """
    return Numerator, TotalTrade, Price


def GeoPolRisk(Numerator, TotalTrade, Price, ProdQty, HHI):
    """
    The GeoPolRisk method has two value outputs: the GeoPolRisk Score,
    a non-dimensional score useful for comparative risk assessment,
    and the characterization factor, which is used for evaluating
    the GeoPolitical Supply Risk in Life Cycle Assessment with units of eq. kg-Cu/kg.
    """
    Denominator = TotalTrade + ProdQty
    try:
        WTA = Numerator / Denominator
    except:
        logging.debug(f"Check the Numerator and Denominator. Numerator: {Numerator}, Denominator: {Denominator}")
    Score = HHI * WTA
    CF = Score * Price
    """
    'Score' : GeoPolRisk Score : float
    'CF' : GeoPolitical Supply Risk Potential : float
    'WTA': Import Risk : float
    """
    return Score, CF, WTA


###########
# main.py #
###########

def gprs_calc(period: list, country: list, resource: list, region_dict = {}):
    """
    A single aggregate function performs all calculations and exports the results as an Excel file.
    The inputs include a list of years, a list of countries, 
    and a list of resources, with an optional dictionary for defining new regions.
    The lists can contain resource names such as 'Cobalt' and 'Lithium',
    and country names like 'Japan' and 'Canada', or alternatively, HS codes and ISO digit codes.
    
    For regional assessments, regions must be defined in the dictionary with country names,
    not ISO digit codes.
    For example, the 'West Europe' region can be defined as 
    { 
        'West Europe': ['France', 'Germany', 'Italy', 'Spain', 'Portugal', 'Belgium', 'Netherlands', 'Luxembourg']
        }.
    """
    Score_list, CF_list = [], []
    hhi_list, ir_list, price_list = [], [], []
    dbid = []
    ctry_db, rm_db, period_db = [], [], []
    regions(region_dict) #Function to define region
    if databases.regional == False:
        #Calculation loop for non regional assessment
        for year, ctry, rm in tqdm(
            list(itertools.product(period, country, resource)),
            desc="Calculating the GeoPolRisk: "
            ):
            try:
                ProdQty, hhi = HHI(rm, int(year), ctry)
            except ValueError:
                logging.debug("Couldnt calculate the HHI. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Numerator, TotalTrade, Price = importrisk(
                    cvtresource(rm, type="HS"), year, databases.regionslist[cvtcountry(ctry, type="Name")]
                )
            except ValueError:
                logging.debug("Couldnt calculate the Import Risk. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Score, CF, IR = GeoPolRisk(Numerator, TotalTrade, Price, ProdQty, hhi)
            except ValueError:
                logging.debug("Couldnt calculate the GeoPolRisk. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Score_list.append(Score)
                CF_list.append(CF)
                hhi_list.append(hhi)
                ir_list.append(IR)
                price_list.append(Price)
                ctry_db.append(cvtcountry(ctry, type="Name"))
                rm_db.append(cvtresource(rm, type="Name"))
                period_db.append(year)
                dbid.append(create_id(cvtresource(rm, type="HS"), cvtcountry(ctry, type="ISO"), year))
            except Exception as e:
                logging.debug("Error while recording data for non regional assessment!", e)
    else:
        for year, ctry, rm in tqdm(
            list(itertools.product(period, country, resource)),
            desc="Calculating the GeoPolRisk: "):
            try:
                Numerator, TotalTrade, Price = aggregateTrade(
                    year, databases.regionslist[ctry], cvtresource(rm, type="HS")
                )
            except ValueError:
                logging.debug("Couldnt calculate the Import Risk - Regional. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                sum_ProdQty = []
                for j in databases.regionslist[ctry]:
                    ProdQty, hhi = HHI(rm, int(year), j)
                    sum_ProdQty.append(ProdQty)
            except ValueError:
                logging.debug("Couldnt calculate the HHI and Production Quantity - Regional. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Score, CF, IR = GeoPolRisk(Numerator, TotalTrade, Price, sum(sum_ProdQty), hhi)
            except ValueError:
                logging.debug("Couldnt calculate the GeoPolRisk - Regional. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            
            try:
                Score_list.append(Score)
                CF_list.append(CF)
                hhi_list.append(hhi)
                ir_list.append(IR)
                price_list.append(Price)
                ctry_db.append(ctry)
                rm_db.append(cvtresource(rm, type="Name"))
                period_db.append(year)
                dbid.append(create_id(cvtresource(rm, type="HS"), ctry, year))
            except Exception as e:
                logging.debug("Error while recording data for regional assessment!", e)

    result = createresultsdf()
    try:
        result["DBID"] = dbid
        result["Country [Economic Entity]"] = ctry_db
        result["Raw Material"] = rm_db
        result["Year"] = period_db
        result["GeoPolRisk Score"] = Score_list
        result["GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"] = CF_list
        result["HHI"] = hhi_list
        result["Import Risk"] = ir_list
        result["Price"] = price_list

        excel_path = databases.directory + "/output/results.xlsx"
        result.to_excel(excel_path, index=False)
    except Exception as e:
        logging.debug("Error while recording data into dataframe for regional assessment!", e)



