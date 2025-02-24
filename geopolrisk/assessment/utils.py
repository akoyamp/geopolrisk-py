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
    if pd.isna(x) or x in [
        None,
        "NA",
        " ",
        "",
    ]:
        return 0
    return x


def cvtcountry(country, type="ISO"):
    # Function to convert country inputs, ISO to name or name to ISO
    """
    Type can be either 'ISO' or 'Name'
    Convert between country name and ISO code.
    - `type="ISO"`: Convert country name to ISO.
    - `type="Name"`: Convert ISO to country name.
    """
    MapISOdf = databases.production["Country_ISO"]
    MapISOdf["ISO"] = MapISOdf["ISO"].astype(int)

    if type == "ISO":
        if country in MapISOdf["Country"].tolist():
            return MapISOdf.loc[MapISOdf["Country"] == country, "ISO"].iloc[0]
        elif country in MapISOdf["ISO"].astype(int).tolist():
            return country
        elif databases.regional == True and country in databases.regionslist:
            if country in MapISOdf["Country"].values:
                return MapISOdf.loc[MapISOdf["Country"] == country, "ISO"].values[0]
            elif isinstance(country, int) and country in MapISOdf["ISO"].values:
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
            if isinstance(country, int) and country in MapISOdf["ISO"].values:
                return MapISOdf.loc[MapISOdf["ISO"] == country, "Country"].values[0]
            elif country in MapISOdf["Country"].values:
                return country
        else:
            logging.debug(
                f"To Name: Entered country '{country}' does not exist in our database!"
            )
            raise ValueError
    if databases.regional and country in databases.regionslist:
        return country

    logging.debug(f"Entered country '{country}' does not exist in our database!")
    raise ValueError(f"Country '{country}' not found.")


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


def getbacidata(period: int, country: int, rawmaterial: str, data):
    """
    get the baci-trade-data from the baci_trade dataframe
    """
    df_query = f"(period == {period}) & (reporterCode == {country}) & (rawMaterial == '{rawmaterial}')"
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
    'Raw Material' -> The Reference name of the commodity traded
    """
    baci_data.loc[:, "qty"] = baci_data["qty"].apply(replace_func).astype(float)
    baci_data.loc[:, "cifvalue"] = (
        baci_data["cifvalue"].apply(replace_func).astype(float)
    )
    if baci_data is None or isinstance(baci_data, type(None)) or len(baci_data) == 0:
        logging.debug(
            f"Problem with get the baci-data - {baci_data} - period == {period} - reporterCode == {country} - Raw Material == '{rawmaterial}'"
        )
        baci_data = None
    return baci_data


def aggregateTrade(period: int, country: list, rawmaterial: str, data):
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
    pISO = []
    for n in country:
        pISO.append(int(cvtcountry(n, type="ISO")))
    logging.info(f"The partner list is {pISO}")
    for i, n in enumerate(country):
        try:
            baci_data = getbacidata(
                period, cvtcountry(n, type="ISO"), rawmaterial, data
            )
        except Exception as e:
            logging.debug(f"Error when filtering database - getbacidata function + {e}")
        if baci_data is None:
            QTY, WGI, VAL = [0], [0], [0]
        else:
            tradedata = baci_data.copy()
            logging.debug(tradedata["partnerCode"].tolist())
            tradedata.loc[tradedata["partnerCode"].isin(pISO), "partnerWGI"] = 0.00
            logging.debug(tradedata)
            QTY = tradedata["qty"].tolist()
            WGI = tradedata["partnerWGI"].apply(wgi_func).astype(float).tolist()
            VAL = tradedata["cifvalue"].tolist()
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
    def cvtresource():
        pass

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


def getProd(rawmaterial):
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
    if rawmaterial in Mapdf["Reference ID"].tolist():
        MappedTableName = Mapdf.loc[Mapdf["Reference ID"] == rawmaterial, "Sheet_name"]
    else:
        print("Entered raw material does not exist in our database!")
        logging.debug(
            f"Error while fetching raw material. Entered raw material = {rawmaterial}"
        )
        raise ValueError

    """
    The returned dataframe is mapped based on the input raw material.
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

    databases.regional = True
    # The function must be called before calling any other functions in the core
    # module. The following lines populate the region list with all the countries
    # in the world including EU defined in the init file.
    for i in databases.production["Country_ISO"]["Country"].tolist():
        databases.regionslist[i] = [i]


########################################################
##   Mapping Functions - GeoPolRisk ##
########################################################


def Mapping():
    """
    Creates a dictionary mapping 'Reference ID' to a list of HS Codes.
    Extracts data from 'HS Code Map' in 'databases.production' and ensures data validity.
    Returns an empty dictionary in case of errors.
    """
    try:
        temp = databases.production.get("HS Code Map")

        if temp is None or temp.empty:
            logging.debug("HS Code Map dataset is empty or missing.")
            return {}
        hs_map = {}

        for _, row in temp.iterrows():
            try:
                hs_codes = [int(row["HS Code"])]

                if (
                    pd.notna(row["HS Code - Complementary"])
                    and row["HS Code - Complementary"]
                ):
                    hs_codes.extend(
                        [
                            int(code)
                            for code in row["HS Code - Complementary"].split(";")
                        ]
                    )

                hs_map[row["Reference ID"]] = list(set(hs_codes))
            except (ValueError, KeyError) as e:
                logging.debug(f"Skipping row - {row} due to data error: {e}")

        return hs_map

    except KeyError as e:
        logging.debug(f"Missing required column: {e}")
    except ValueError as e:
        logging.debug(f"Data validation error: {e}")
    except Exception as e:
        logging.debug(f"Unexpected error: {e}")

    return {}


def mapped_baci():
    """
    This function processes trade data by mapping commodity codes to raw materials.
    It aggregates trade information (such as quantities and CIF values) for each raw material,
    while handling cases where multiple commodity codes exist for a raw material.
    The function will group trade data by raw material, period, and other relevant fields,
    summing quantities and CIF values, and concatenating commodity codes where applicable.
    """
    try:
        hs_map = Mapping()
        master_data = []
        for raw_material, codes in hs_map.items():
            temp = databases.baci_trade
            filtered_data = temp.loc[temp["cmdCode"].astype(int).isin(codes)].copy()
            filtered_data["rawMaterial"] = raw_material
            filtered_data["cmdCode"] = filtered_data["cmdCode"].astype(int)
            filtered_data["period"] = filtered_data["period"].astype(int)
            filtered_data["reporterCode"] = filtered_data["reporterCode"].astype(int)
            filtered_data["partnerCode"] = filtered_data["partnerCode"].astype(int)
            filtered_data["qty"] = (
                filtered_data["qty"].apply(replace_func).astype(float, errors="ignore")
            )
            filtered_data["cifvalue"] = (
                filtered_data["cifvalue"]
                .apply(replace_func)
                .astype(float, errors="ignore")
            )
            grouped_data = filtered_data.groupby(
                [
                    "period",
                    "reporterCode",
                    "reporterDesc",
                    "reporterISO",
                    "partnerCode",
                    "partnerDesc",
                    "partnerISO",
                    "rawMaterial",
                ],
                as_index=False,
            ).agg(
                {
                    "cmdCode": lambda x: ";".join(map(str, sorted(set(x)))),
                    "qty": "sum",
                    "cifvalue": "sum",
                    "partnerWGI": "first",
                }
            )

            master_data.append(grouped_data)
        master_df = pd.concat(master_data, ignore_index=True)
        return master_df

    except Exception as e:
        logging.debug(f"Error in mapped_baci function: {e}")
        raise


def default_rmlist():
    hs_map = Mapping()
    return list(hs_map.keys())
