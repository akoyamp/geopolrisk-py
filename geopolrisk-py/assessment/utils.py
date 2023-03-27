import pandas as pd, json
import comtradeapicall as ctac
from urllib.request import Request, urlopen
from pathlib import Path
from .__init__ import instance, logging, execute_query, outputDF
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


def convertCodes(resource, country):
    # Verify direction
    def check_variables(A, B):
        if (isinstance(A, list)
            and isinstance(B, list)):
            if (
            all(isinstance(element, str) for element in A)
            and all(isinstance(element, str) for element in B)
            ):
                return "numeric"
            elif (
                all(isinstance(element, int) for element in A)
                and all(isinstance(element, int) for element in B)
            ):
                return "text"
            else:
                return None
        elif (
            isinstance(A, str)
            and isinstance(B, str)
            ):
            return "numeric"
        elif (
            isinstance(A, int)
            and isinstance(B, int)):
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
                    logging.debug(f"Failed to transform! {e}")
                    logging.debug(f"Transformation failed for {n}")
            return X_transform
        else:
            try:
                idx = A.index(X)
                X_transform = B[idx]
            except Exception as e:
                    logging.debug(f"Failed to transform! {e}")
                    logging.debug(f"Transformation failed for {X}")
                    X_transform = None
            return X_transform

    direction = check_variables(resource, country)
    
    commodity, countryname, HSCode, ISOCode = None, None, None, None
    if direction.lower() == "numeric":
        ResourceCX = return_variables(resource, Resource, HS)
        CountryCX = return_variables(country, Country, ISO)
        commodity = resource
        countryname = country
        HSCode = ResourceCX
        ISOCode = CountryCX
    elif direction.lower() == "text":
        ResourceCX = return_variables(resource, HS, Resource)
        CountryCX = return_variables(country, ISO, Country)
        commodity = ResourceCX
        countryname = CountryCX
        HSCode = resource
        ISOCode = country
    else:
        logging.debug("Failed to transform!")
        logging.debug(direction)
        ResourceCX, CountryCX = resource, country
    return commodity, countryname, HSCode, ISOCode

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
                _ignore, _ignore2, commoditycode, country = convertCodes(commoditycode, country)
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

def replace_values(list_to_replace, item_to_replace, item_to_replace_with):
    return [
        item_to_replace_with if item == item_to_replace else item
        for item in list_to_replace
    ]

def create_id(HS, ISO, Year):
    HS, ISO, Year = str(HS), str(ISO), str(Year)
    if len(HS) == 4:
        HSID = "xx"+HS
    elif len(HS) == 5:
        HSID = "x"+HS
    else:
        HSID = HS
    if len(ISO) == 2:
        ISOID = "x"+ISO
    elif len(ISO) == 1:
        ISOID = "xx"+ISO
    else:
        ISOID = ISO
    DBID = HSID+ISOID+Year
    return DBID

# Verify if the calculation is already stored in the database to avoid recalculation
def sqlverify(DBID, RR, Scenario):
    try:
        row = execute_query(f"SELECT 'recycling_rate' ,'scenario' FROM recordData WHERE id = '{DBID}';", db_path=db)
    except Exception as e:
        logging.debug(f"Database error in sqlverify - {e.message}")
        row = None
    if not row:
        return False
    else:
        return True

# This function doesnt override the calculaiton
def recordData(Resource, Country, Year, RR, Scenario,
               GPRS, CF, HHI, WTA, LogFile, OuputList):
    resource, country, HSCODE, ISO = convertCodes(Resource, Country)
    DBID = create_id(HSCODE, ISO, Year)
    if sqlverify(DBID) is True:
        sqlstatement = f"""SELECT 'recycling_rate' ,'scenario', 'geopolrisk'
        FROM recordData WHERE id = '{DBID}';
        """
        try:
            row = execute_query(sqlstatement, db_path=db)
        except Exception as e:
                    logging.debug(f"Failed to execute statement {e} with {sqlstatement}")
        if str(row[0][0]) == str(RR) and str(row[0][1]) == str(Scenario):
            if str(row[0][2]) != str(GPRS):
                sqlstatement = f"""UPDATE recordData SET hhi =
                '{HHI}', wta = '{WTA}', geopolrisk = '{GPRS}', geopol_cf = '{CF}',
                log_ref = '{LogFile}'
                """
                try:
                    row = execute_query(sqlstatement, db_path=db)
                except Exception as e:
                    logging.debug(f"Failed to execute statement {e} with {sqlstatement}")
                OuputList.append(str(Year), str(resource), str(country),
                            str(RR), str(Scenario),
                            str(GPRS), str(CF), str(HHI), str(WTA))
            else:
                logging.info("The database already exists with the data")
        else:
            sqlstatement = f""" INSERT INTO recordData (id, country, resource, year,
            recycling_rate, scenario, geopolrisk, hhi, wta, geopol_cf, resource_hscode, 
            iso, log_ref) VALUES ('{DBID}','{country}', '{resource}', '{Year}',
            '{RR}', '{Scenario}', '{GPRS}', '{HHI}', '{WTA}', '{CF}', '{HSCODE}',
            '{ISO}', '{LogFile}');
            """
            try:
                    row = execute_query(sqlstatement, db_path=db)
            except Exception as e:
                logging.debug(f"Failed to execute statement {e} with {sqlstatement}")
            OuputList.append(str(Year), str(resource), str(country),
                            str(RR), str(Scenario),
                            str(GPRS), str(CF), str(HHI), str(WTA))
    else:
        sqlstatement = f""" INSERT INTO recordData (id, country, resource, year,
            recycling_rate, scenario, geopolrisk, hhi, wta, geopol_cf, resource_hscode, 
            iso, log_ref) VALUES ('{DBID}','{country}', '{resource}', '{Year}',
            '{RR}', '{Scenario}', '{GPRS}', '{HHI}', '{WTA}', '{CF}', '{HSCODE}',
            '{ISO}', '{LogFile}');
            """
        try:
                row = execute_query(sqlstatement, db_path=db)
        except Exception as e:
            logging.debug(f"Failed to execute statement {e} with {sqlstatement}")
        OuputList.append(str(Year), str(resource), str(country),
                            str(RR), str(Scenario),
                            str(GPRS), str(CF), str(HHI), str(WTA))






