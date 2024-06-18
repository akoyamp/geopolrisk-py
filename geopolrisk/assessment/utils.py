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

import pandas as pd, json, sqlite3
import comtradeapicall as ctac
from urllib.request import Request, urlopen
from .__init__ import instance, logging, execute_query
import os

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
        if isinstance(A, list) and isinstance(B, list):
            if all(isinstance(element, str) for element in A) and all(
                isinstance(element, str) for element in B
            ):
                return "numeric"
            elif all(isinstance(element, int) for element in A) and all(
                isinstance(element, int) for element in B
            ):
                return "text"
            else:
                return None
        elif isinstance(A, str) and isinstance(B, str):
            return "numeric"
        elif isinstance(A, int) and isinstance(B, int):
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
                    if n in regionslist.keys():
                        logging.debug(f"Region transformation cannot be applied!")
                        X_transform.append(n)
                    else:
                        logging.debug(f"Failed to transform! {e}")
                        logging.debug(f"Transformation failed for {n}")
                        X_transform = None
            return X_transform
        else:
            try:
                idx = A.index(X)
                X_transform = B[idx]
            except Exception as e:
                if X in regionslist.keys():
                    logging.debug(f"Region transformation cannot be applied!")
                    X_transform = X
                else:
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


def get_baci_data(period, country, commoditycode):
    '''
    get the baci-trade-data from the sqlite-db "baci.db"
    '''
    period = str(period)
    country = str(country)
    commoditycode = str(commoditycode)
    
    current_dir = os.path.abspath("..")
    baci_db = f"{current_dir}/oert/output-files/baci/baci.db"
    # connect to db
    conn = sqlite3.connect(baci_db)
    # define query - that returns the same format as the comtradeapi
    sql_query = f"""select 
	'' as typeCode,
	'' as freqCode,
	'' as refPeriodId,
	bacitab.t as period,
	bacitab.i as reporterCode,
    (SELECT cc.country_name FROM country_codes_V202401b cc WHERE bacitab.i = cc.country_code) AS reporterDesc,
    (SELECT cc.country_iso3 FROM country_codes_V202401b cc WHERE bacitab.i = cc.country_code) AS reporterISO,
    '' as flowCode,
    '' as flowDesc,
    bacitab.j as partnerCode,
    (SELECT cc.country_name FROM country_codes_V202401b cc WHERE bacitab.j = cc.country_code) AS partnerDesc,
    (SELECT cc.country_iso3 FROM country_codes_V202401b cc WHERE bacitab.j = cc.country_code) AS partnerISO,
	'' as partner2Code,
	'' as partner2Desc,	
	'' as partner2ISO,
	'' as classificationCode,
	bacitab.k as cmdCode,
	'' as cmdDesc,
	'' as customsCode,
	'' as customsDesc,
	'' as mosCode,
	'' as motCode,
	'' as motDesc,
	'8' as qtyUnitCode,
	'kg' as qtyUnitAbbr,
	-- unit in baci in metric tons --> converation * 1000 to kg - see http://www.cepii.fr/DATA_DOWNLOAD/baci/doc/DescriptionBACI.html
	bacitab.q * 1000 as qty,
	'' as altQtyUnitCode,
	'' as altQtyUnitAbbr,
	'' as altQty,
	-- unit in baci in metric tons --> converation * 1000 to kg - see http://www.cepii.fr/DATA_DOWNLOAD/baci/doc/DescriptionBACI.html
	bacitab.q * 1000 as netWgt,
	'' as grossWgt,
	bacitab.v as cifvalue,
	'' as fobvalue,
	'' as primaryValue
	-- '' as Qty,
	-- '' as CifValue,
    from baci_trade bacitab
    where bacitab.t = '{period}'
    and bacitab.i = '{country}'
    and bacitab.k like '{commoditycode}'
    ;
    """
    # read data to df
    get = pd.read_sql_query(sql_query, conn)
    # close db-connection
    conn.close()
    
    try:
        if get is not None or not isinstance(get, type(None)) or len(get) == 0:
            get["Qty"] = get.groupby(["partnerCode"])["qty"].transform(sum)
            get["CifValue"] = get.groupby(["partnerCode"])["cifvalue"].transform(sum)
            get = get.drop_duplicates(subset="partnerCode", keep="first")
            try:
                cifvalueToT = sum(get["CifValue"].to_list())
                totalQ = sum(get["Qty"].to_list())
                if totalQ == 0:
                    pricecif = 0
                else:
                    pricecif = cifvalueToT / totalQ
            except Exception as e:
                logging.debug(f"Error while extracting cifvalue! {e}")
                get, pricecif = None, None
        else:
            logging.debug(f"Problem with the new API call! {get}")
            get, pricecif = None, None
    except Exception as e:
        logging.debug(f"Error while extracting and combining data! {e}")
        get, pricecif = None, None
    return get, pricecif

def callapirequest(period, country, commoditycode):
    period = str(period)
    country = str(country)
    commoditycode = str(commoditycode)
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
        logging.debug(f"Error while calling API! {e}")
        return None, None
    try:
        if get is not None or not isinstance(get, type(None)) or len(get) == 0:
            get["Qty"] = get.groupby(["partnerCode"])["qty"].transform(sum)
            get["CifValue"] = get.groupby(["partnerCode"])["cifvalue"].transform(sum)
            get = get.drop_duplicates(subset="partnerCode", keep="first")
            try:
                cifvalueToT = sum(get["CifValue"].to_list())
                totalQ = sum(get["Qty"].to_list())
                if totalQ == 0:
                    pricecif = 0
                else:
                    pricecif = cifvalueToT / totalQ
            except Exception as e:
                logging.debug(f"Error while extracting cifvalue! {e}")
                get, pricecif = None, None
        else:
            logging.debug(f"Problem with the new API call! {get}")
            get, pricecif = None, None
    except Exception as e:
        logging.debug(f"Error while extracting and combining data! {e}")
        get, pricecif = None, None
    return get, pricecif


def oldapirequest(period, country, commoditycode):
    period = str(period)
    country = str(country)
    commoditycode = str(commoditycode)
    url = f"""https://comtrade.un.org/api/get?max=50000&type=C&freq=A&px=HS&ps={period}&r={country}&p=all&cc={commoditycode}&rg=1&fmt=json"""
    logging.info(url)
    try:
        request = Request(url)
        response = urlopen(request)
        elevations = response.read()
    except Exception as e:
        logging.debug(url)
        logging.debug(f"Error while calling native API! {e}")
        return None

    try:
        data = json.loads(elevations)
        data = pd.json_normalize(data["dataset"])
    except Exception as e:
        logging.debug("Error while parsing JSON!")
        return None

    return data


def replace_values(list_to_replace, item_to_replace, item_to_replace_with):
    return [
        item_to_replace_with if item == item_to_replace else item
        for item in list_to_replace
    ]


def create_id(HS, ISO, Year):
    HS, ISO, Year = str(HS), str(ISO), str(Year)
    if len(HS) == 4:
        HSID = "xx" + HS
    elif len(HS) == 5:
        HSID = "x" + HS
    else:
        HSID = HS
    if len(ISO) == 2:
        ISOID = "x" + ISO
    elif len(ISO) == 1:
        ISOID = "xx" + ISO
    else:
        ISOID = ISO
    DBID = HSID + ISOID + Year
    return DBID


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


# This function doesnt override the calculaiton
def recordData(
    Resource, Country, Year, RR, Scenario, GPRS, CF, HHI, WTA, LogFile, OuputList
):
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
                    logging.debug(
                        f"Failed to execute statement {e} with {sqlstatement}"
                    )
                OuputList.append(
                    str(Year),
                    str(resource),
                    str(country),
                    str(RR),
                    str(Scenario),
                    str(GPRS),
                    str(CF),
                    str(HHI),
                    str(WTA),
                )
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
            OuputList.append(
                [
                    str(Year),
                    str(resource),
                    str(country),
                    str(RR),
                    str(Scenario),
                    str(GPRS),
                    str(CF),
                    str(HHI),
                    str(WTA),
                ]
            )
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
        OuputList.append(
            [
                str(Year),
                str(resource),
                str(country),
                str(RR),
                str(Scenario),
                str(GPRS),
                str(CF),
                str(HHI),
                str(WTA),
            ]
        )


"""Convert entire database to required format
**CHARACTERIZATION FACTORS
Refer to python json documentation for more information on types of
orientation required for the output.
"""

# Extract CFs
def generateCF(exportType="csv", orient=""):
    exportF = ["csv", "excel", "json"]
    if exportType in exportF:
        logging.debug("Exporting database in the format {}".format(exportType))
        CFType = exportType
    else:
        logging.debug(
            "Exporting format not supported {}. "
            "Using default format [csv]".format(exportType)
        )
        CFType = "csv"
    try:
        conn = sqlite3.connect(
            db,
            isolation_level=None,
            detect_types=sqlite3.PARSE_COLNAMES,
        )
        db_df = pd.read_sql_query("SELECT * FROM recorddata", conn)
        if CFType == "csv":
            db_df.to_csv(_outputfile + "/database.csv", index=False, encoding="utf-8")
        elif CFType == "excel":
            db_df.to_excel(
                _outputfile + "/database.xlsx", index=False, encoding="utf-8"
            )
        elif CFType == "json":
            db_df.to_json(_outputfile + "/database.json", orient=orient, index=False)
    except Exception as e:
        logging.debug(f"Error while exporting database! {e}")
