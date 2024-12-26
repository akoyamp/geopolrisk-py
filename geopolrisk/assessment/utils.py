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

import pandas as pd, os
from .database import databases, logging, execute_query

tradepath = None
db = databases.directory + "/output"

########################################
##   Utility functions --  GeoPolRisk ##
########################################


def replace_func(x):
    if isinstance(x, float):
        return x
    else:
        if x is None or isinstance(x, type(None)) or x.strip() == "NA" or x == " ":
            return 0
        else:
            return x


def cvtresource(resource, type="HS"):
    # Function to convert resource inputs, HS to name or name to HS
    """
    Type can be either 'HS' or 'Name'
    """
    MapHSdf = databases.production["HS Code Map"]
    if type == "HS":
        if resource in MapHSdf["ID"].tolist():
            return int(MapHSdf.loc[MapHSdf["ID"] == resource, "HS Code"].iloc[0])
        else:
            try:
                resource = int(resource)
            except Exception as e:
                logging.debug(
                    f"To HS: Entered raw material {resource} does not exist in our database!, {e}"
                )
                raise ValueError
            if str(resource) in MapHSdf["HS Code"].tolist():
                return int(resource)

    elif type == "Name":

        try:
            resource = int(resource)
        except:
            # print(f"Entered raw material '{resource}' does not exist in our database! Please enter numerical inputs")
            logging.debug(
                f"Entered raw material '{resource}' does not exist in our database! Please enter numerical inputs"
            )
            resource = str(resource)
        if str(resource) in MapHSdf["HS Code"].astype(str).tolist():
            return MapHSdf.loc[MapHSdf["HS Code"] == str(resource), "ID"].iloc[0]
        elif resource in MapHSdf["ID"].tolist():
            return resource
        else:
            logging.debug(
                f"To Name: Entered raw material '{resource}' does not exist in our database!"
            )
            raise ValueError


def cvtcountry(country, type="ISO"):
    # Function to convert country inputs, ISO to name or name to ISO
    """
    Type can be either 'ISO' or 'Name'
    """
    MapISOdf = databases.production["Country_ISO"]
    if type == "ISO":
        if country in MapISOdf["Country"].tolist():
            return MapISOdf.loc[MapISOdf["Country"] == country, "ISO"].iloc[0]
        elif country in MapISOdf["ISO"].astype(int).tolist():
            return country
        elif databases.regional == True and country in databases.regionslist:
            return country
        else:
            logging.debug(
                f"To int: Entered country '{country}' does not exist in our database!"
            )
            raise ValueError

    elif type == "Name":
        if country in MapISOdf["ISO"].astype(int).tolist():
            return MapISOdf.loc[MapISOdf["ISO"] == country, "Country"].iloc[0]
        elif str(country) in MapISOdf["Country"].tolist():
            return country
        elif databases.regional == True and country in databases.regionslist:
            return country
        else:
            logging.debug(
                f"To Name: Entered country '{country}' does not exist in our database!"
            )
            raise ValueError


def sumproduct(A: list, B: list):
    return sum(i * j for i, j in zip(A, B))


def create_id(HS, ISO, Year):
    return str(HS) + str(ISO) + str(Year)


# 2024-08-23 - this function is not being used - deleted
# Verify if the calculation is already stored in the database to avoid recalculation
# def sqlverify(DBID):
#     try:
#         sql = f"SELECT * FROM recordData WHERE id = '{DBID}';"
#         row = execute_query(
#             f"SELECT * FROM recordData WHERE id = '{DBID}';",
#             db_path=db,
#         )
#     except Exception as e:
#         logging.debug(f"Database error in sqlverify - {e}, {sql}")
#         row = None
#     if not row:
#         return False
#     else:
#         return True


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
            "DBID"	TEXT,
        	"Country [Economic Entity]"	TEXT,
        	"Raw Material"	TEXT,
        	"Year"	INTEGER,
        	"GeoPolRisk Score"	REAL,
        	"GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"	REAL,
        	"HHI"	REAL,
        	"Import Risk" REAL,
        	"Price"	REAL,
        	PRIMARY KEY("DBID")
        );"""
    row = execute_query(
        SQLQuery,
        db_path=dbpath,
    )
    return df


def writetodb(dataframe):
    dbpath = databases.directory + "/output/" + databases.Output
    for index, row in dataframe.iterrows():
        check_query = "SELECT 1 FROM recordData WHERE DBID = ?;"
        exists = execute_query(check_query, db_path=dbpath, params=(row["DBID"],))

        if exists:
            update_query = """
                UPDATE recordData
                SET 
                    "Country [Economic Entity]" = ?,
                    "Raw Material" = ?,
                    "Year" = ?,
                    "GeoPolRisk Score" = ?,
                    "GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]" = ?,
                    "HHI" = ?,
                    "Import Risk" = ?,
                    "Price" = ?
                WHERE DBID = ?;
            """
            params = (
                row["Country [Economic Entity]"],
                row["Raw Material"],
                row["Year"],
                row["GeoPolRisk Score"],
                row["GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"],
                row["HHI"],
                row["Import Risk"],
                row["Price"],
                row["DBID"],
            )
            try:
                execute_query(update_query, db_path=dbpath, params=params)
            except Exception as e:
                print(
                    "Failed to write to output database, Check logs! - Update failed!"
                )
                logging.debug(
                    f"Failed to write to output database - Update Query - Dataframe index = {index} | {update_query} | {row} | Error = {e}"
                )
        else:
            insert_query = """
                INSERT INTO recordData (
                    DBID,
                    "Country [Economic Entity]",
                    "Raw Material",
                    "Year",
                    "GeoPolRisk Score",
                    "GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]",
                    "HHI",
                    "Import Risk",
                    "Price"
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            params = (
                row["DBID"],
                row["Country [Economic Entity]"],
                row["Raw Material"],
                row["Year"],
                row["GeoPolRisk Score"],
                row["GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"],
                row["HHI"],
                row["Import Risk"],
                row["Price"],
            )
            try:
                execute_query(insert_query, db_path=dbpath, params=params)
            except Exception as e:
                print(
                    "Failed to write to output database, Check logs! - Insert failed!"
                )
                logging.debug(
                    f"Failed to write to output database - Insert Query - Dataframe index = {index} | {update_query} | {row} | Error = {e}"
                )


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
    baci_data.loc[:, "cifvalue"] = (
        baci_data["cifvalue"].apply(replace_func).astype(float)
    )
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
    partnerISO = []
    for i, n in enumerate(country):
        baci_data = getbacidata(
            period, cvtcountry(n, type="ISO"), commoditycode, data=data
        )
        partnerISO.append(cvtcountry(n, type="ISO"))
        if baci_data is None:
            QTY, WGI, VAL = [0], [0], [0]
        else:
            baci_data = baci_data.copy()
            baci_data.loc[baci_data["partnerISO"].isin(partnerISO), "partnerWGI"] = 0
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


###########################################################
## Converting company trade data into a usable dataframe ##
###########################################################


def transformdata(mode="prod"):
    folder_path = databases.directory + "/databases"
    file_name = "Company data.xlsx"
    excel_sheet_name = "Template"
    # file_path = glob.glob(os.path.join(folder_path, file_name))[0]
    file_path = os.path.join(folder_path, file_name)
    # in test-mode - use the excel-file from the test-folder
    if "test" in mode:
        test_dir = os.path.abspath("./geopolrisk/tests/")
        file_path = f"{test_dir}/{file_name}"
        excel_sheet_name = "Test"
    """
    The template excel file has the following headers
    'Metal': Specify the type of metal.
    'Country of Origin': Indicate the country where the metal was sourced.
    'Quantity (kg)': Enter the quantity of metal imported from each country.
    'Value (USD)': Value of the metal of the quantity imported.
    'Year': The year of the trade
    'Additional Notes': Include any additional relevant information.
    """
    Data = pd.read_excel(file_path, sheet_name=excel_sheet_name)
    HS_Code = []
    for resource in Data["Metal"].tolist():
        HS_Code.append(cvtresource(resource, type="HS"))
    ISO = []
    for country in Data["Country of Origin"].tolist():
        ISO.append(cvtcountry(country, type="ISO"))
    MapWGIdf = databases.wgi
    wgi = []
    for i, iso in enumerate(ISO):
        try:
            wgi.append(
                # MapWGIdf.loc[MapWGIdf["country_code"] == iso, Data["Year"].tolist()[i]]
                float(
                    MapWGIdf.query(f'country_code == "{iso}"')[
                        str(Data["Year"].tolist()[i])
                    ].iloc[0]
                )
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
        databases.regionslist[i] = [i]
