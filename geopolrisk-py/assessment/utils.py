import pandas as pd, json
from urllib.request import Request, urlopen
from pathlib import Path
from .__init__ import instance, logging, execute_query
from .Exceptions.warningsgprs import *



# Define Paths
tradepath = None
_production, _reporter = instance.production, instance.reporter
regionslist, _outputfile = instance.regionslist, instance.exportfile
_price = instance.price
db = _outputfile + '/' + instance.Output
# Extract list of all data
HS = _price.HS.to_list()
HS = [int(float(x)) for x in HS]
Resource = _price.Resource.to_list()
Country = _reporter.Country.to_list()
ISO = _reporter.ISO.to_list()

def convertCodes(resource, country, *args, **kwargs):
    # Verify direction
    def check_variables(A, B):
        if (isinstance(A, list) and 
            isinstance(B, list) and 
            all(isinstance(element, str) 
                for element in A) and 
                all(isinstance(element, str) for element in B)):
            return "Numeric"
        elif (isinstance(A, int) and isinstance(B, int) or 
              (isinstance(A, list) and isinstance(B, list) and 
               all(isinstance(element, int) for element in A) and 
               all(isinstance(element, int) for element in B))):
            return "Text"
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
                    logging.debug("Failed to transform")
                    logging.debug(e)
                    logging.debug("Transformation failed for " + str(n))
            return X_transform
        else:
            try:
                idx = A.index(X)
                X_transform = B[idx]
            except Exception as e:
                    logging.debug("Failed to transform")
                    logging.debug(e)
                    logging.debug("Transformation failed for " + str(X))
                    X_transform = None
            return X_transform

    direction = check_variables(resource, country)
    print(direction)    
    if direction == "Numeric":
        ResourceCX = return_variables(resource, Resource, HS)
        CountryCX = return_variables(country, Country, ISO)
    elif direction == "Text":
        ResourceCX = return_variables(resource, HS, Resource)
        CountryCX = return_variables(country, ISO, Country)
    else:
        logging.debug("Failed to verify direction")
        logging.debug(direction)
        ResourceCX, CountryCX = None, None
    return ResourceCX, CountryCX

def replace_values(list_to_replace, item_to_replace, item_to_replace_with):
    return [item_to_replace_with if item == item_to_replace else item for item in list_to_replace]

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
    (resource, country, year, recyclingrate, scenario)= (
        args[0],
        args[1],
        args[2],
        args[3],
        args[4],
    )
    (   GPRS,
        CF,
        HHI,
        WTA,
        HSCODE,
        ISO,
        Log
    ) = (
        args[5],
        args[6],
        args[7],
        args[8],
        args[9],
        args[10],
        args[11]
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
    dataframe = pd.DataFrame(row, columns=["geopolrisk", "hhi", "wta",
                                           "geopol_cf"])
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
