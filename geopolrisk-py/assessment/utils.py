import pandas as pd, json
import comtradeapicall as ctac
from urllib.request import Request, urlopen
from pathlib import Path
from .__init__ import instance, logging, execute_query
from .Exceptions.warningsgprs import *

# Define Paths
tradepath = None
_production, _reporter = instance.production, instance.reporter
regionslist, _outputfile = instance.regionslist, instance.exportfile
_price = instance.price
db = _outputfile + "/" + instance.Output
# Extract list of all data
HS = _price.HS.to_list()
HS = [int(float(x)) for x in HS]
Resource = _price.Resource.to_list()
Country = _reporter.Country.to_list()
ISO = _reporter.ISO.to_list()
ISO = [int(x) for x in ISO]


def convertCodes(resource, country, output="numeric"):
    # Verify direction
    def check_variables(A, B):
        if (
            isinstance(A, list)
            and isinstance(B, list)
            and all(isinstance(element, str) for element in A)
            and all(isinstance(element, str) for element in B)
        ):
            return "numeric"
        elif (
            isinstance(A, int)
            and isinstance(B, int)
            or (
                isinstance(A, list)
                and isinstance(B, list)
                and all(isinstance(element, int) for element in A)
                and all(isinstance(element, int) for element in B)
            )
        ):
            return "text"
        else:
            return None

    def return_variables(X, A, B):
        if isinstance(X, list):
            X_transform = []
            for i, n in enumerate(X):
                try:
                    idx = A.index(n)
                    X_transform.append(B[idx])
                except Exception as e:
                    logging.debug("Failed to transform!")
                    logging.debug(e)
                    logging.debug("Transformation failed for " + str(n))
            return X_transform
        else:
            try:
                idx = A.index(X)
                X_transform = B[idx]
            except Exception as e:
                logging.debug("Failed to transform!")
                logging.debug(e)
                logging.debug("Transformation failed for " + str(X))
                X_transform = None
            return X_transform

    direction = check_variables(resource, country)
    if direction.lower() == output.lower() and direction.lower() == "numeric":
        ResourceCX = return_variables(resource, Resource, HS)
        CountryCX = return_variables(country, Country, ISO)
    elif direction.lower() == output.lower() and direction.lower() == "text":
        ResourceCX = return_variables(resource, HS, Resource)
        CountryCX = return_variables(country, ISO, Country)
    else:
        logging.debug("Failed to transform!")
        logging.debug(direction)
        ResourceCX, CountryCX = resource, country
    return ResourceCX, CountryCX


def replace_values(list_to_replace, item_to_replace, item_to_replace_with):
    return [
        item_to_replace_with if item == item_to_replace else item
        for item in list_to_replace
    ]


# Verify if the calculation is already stored in the database to avoid recalculation
def sqlverify(*args):
    resource, country, year, recyclingrate, scenario, outputList = (
        args[0],
        args[1],
        args[2],
        args[3],
        args[4],
        args[5],
    )
    sqlstatement = (
        "SELECT geopolrisk, hhi, wta, geopol_cf FROM recordData WHERE country = '"
        + country
        + "' AND resource= '"
        + resource
        + "' AND year = '"
        + str(year)
        + "' AND recycling_rate = '"
        + str(recyclingrate)
        + "' AND scenario = '"
        + str(scenario)
        + "';"
    )
    try:
        row = execute_query(sqlstatement, db_path=db)
    except InputError:
        logging.debug(sqlstatement)
    if not row:
        return None
    else:
        outputList.append(
            [
                str(year),
                resource,
                country,
                recyclingrate,
                scenario,
                row[0][0],
                row[0][3],
                row[0][1],
                row[0][2],
            ]
        )
        return True


# Updates the database using new values.
# This function doesnt override the calculaiton
def recordData(*args):
    # Verify
    (resource, country, year, recyclingrate, scenario) = (
        args[0],
        args[1],
        args[2],
        args[3],
        args[4],
    )
    (GPRS, CF, HHI, WTA, HSCODE, ISO, Log) = (
        args[5],
        args[6],
        args[7],
        args[8],
        args[9],
        args[10],
        args[11],
    )
    sqlstatement = (
        "SELECT geopolrisk, hhi, wta, geopol_cf from "
        "recordData WHERE country = '"
        + country
        + "' AND resource= '"
        + resource
        + "' AND year = '"
        + str(year)
        + "' AND recycling_rate = '"
        + str(recyclingrate)
        + "' AND scenario = '"
        + str(scenario)
        + "';"
    )
    row = execute_query(sqlstatement, db_path=db)
    dataframe = pd.DataFrame(row, columns=["geopolrisk", "hhi", "wta", "geopol_cf"])
    if dataframe.shape[0] > 2:
        logging.debug("Multiple data records found!")
        raise DataRecordError
        return None
    elif dataframe.shape[0] == 0:
        sqlstatement = (
            "INSERT INTO recordData (country, resource, year, recycling_rate,"
            " scenario, geopolrisk, hhi, wta, geopol_cf, resource_hscode, iso, log_ref) VALUES ('"
            "" + country + "','" + resource + "','" + str(year) + ""
            "','" + str(recyclingrate) + "','" + str(scenario) + "','"
            "" + str(GPRS) + "','" + str(HHI) + "','" + str(WTA) + ""
            "','" + str(CF) + "','" + str(HSCODE) + "','" + str(ISO) + "',"
            "'" + str(Log) + "');"
        )
        try:
            row = execute_query(sqlstatement, db_path=db)
            logging.debug("Database recorded sucessfully!")
            return True
        except Exception as e:
            logging.debug(e)
            raise DataRecordError
            return None
    else:
        if float(dataframe.iloc[0]["wta"]) == float(WTA):
            logging.debug("NO change in trade data detected! No SQL executed.")
            return None
        else:
            sqlstatement = (
                "UPDATE recordData SET hhi= '"
                + str(HHI)
                + "', wta ='"
                + str(WTA)
                + "', geopolrisk='"
                + str(GPRS)
                + "', geopol_cf= '"
                + str(CF)
                + "', log_ref='"
                + str(Log)
                + "' WHERE country = '"
                + country
                + "' AND resource= '"
                + resource
                + "' AND year = '"
                + str(year)
                + "' AND recycling_rate = '"
                + str(recyclingrate)
                + "' AND scenario = '"
                + str(scenario)
                + "';"
            )
            norow = execute_query(sqlstatement, db_path=db)
            logging.debug("Database update sucessfully!")
            return True


def callapirequest(period, country, commoditycode):
    try:
        if any( isinstance(period, int) 
            and  isinstance(country, int)
                and isinstance(commoditycode, int)):
            period=str(period)
            country=str(country)
            commoditycode=str(commoditycode)
        elif all( isinstance(period, str) 
                and  isinstance(country, str)
                and isinstance(commoditycode, str)):
            if country.isdigit() and commoditycode.isdigit():
                period=period
                country=country
                commoditycode=commoditycode
            else:
                period=period
                commoditycode, country = convertCodes(commoditycode, country, output = "numeric")
        logging.debug(f"Parsed values: Period: {period}, Country: {country}, Commodity: {commoditycode}")
    except Exception as e:
        logging.debug(e)
    try:
        get = ctac.previewTarifflineData(
            typeCode="C",
            freqCode="A",
            clCode="HS",
            period=period,
            reporterCode=country,
            cmdCode=commoditycode,
            flowCode="M",
            partnerCode=None,
            partner2Code=None,
            customsCode=None,
            motCode=None,
            maxRecords=500,
            format_output="JSON",
            countOnly=None,
            includeDesc=True,
        )
    except Exception as e:
        logging.debug(e)
    try:
        get["Qty"] = get.groupby(["partnerCode"])['qty'].transform(sum)
        get["CifValue"] = get.groupby(["partnerCode"])['cifvalue'].transform(sum)
        get = get.drop_duplicates(subset="partnerCode", keep="first")
        try:
            cifvalueToT = sum(get["CifValue"].to_list())
            totalQ = sum(get["Qty"].to_list())
            if totalQ == 0:
                pricecif = 0
            else:
                pricecif = cifvalueToT / totalQ
        except Exception as e:
            logging.debug(e)
    except Exception as e:
        logging.debug(e)
    get.to_excel(f"error.xlsx")
    return get, pricecif

_columns = [
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

