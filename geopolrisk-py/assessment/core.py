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
            return X_transform

    direction = check_variables(resource, country)    
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

# Verify if the calculation is already stored in the database to avoid recalculation
def sqlverify(*args):
    resource, country, year, recyclingrate, scenario = (
        args[0],
        args[1],
        args[2],
        args[3],
        args[4],
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

# Method 1
def settradepath(path):
    tradepath = path
    try:
        with open(tradepath) as openfile:
            pd.read_excel(openfile)
    except FileNotFoundError:
        tradepath = None
        raise FileNotFoundError
    except Exception as e:
        logging.debug(e)
        tradepath = None
        raise InputError

# Method 2
def regions(*args):
    if len(args) != 0:
        for key, value in args[0].items():
            if type(key) is not str and type(value) is not list:
                logging.debug(
                    "Dictionary input to regions does not match required type."
                )
                raise InputError
                return None
            Print_Error = [
                x
                for x in value
                if str(x) not in _reporter.Country.to_list()
                or str(x) not in _reporter["ISO"].astype(str).tolist()
            ]
            if len(Print_Error) != 0:
                logging.debug(
                    "Error in creating a region! "
                    "Following list of countries not"
                    " found in the ISO list {}. "
                    "Please conform with the ISO list or use"
                    " 3 digit ISO country codes.".format(Print_Error)
                )
                raise InputError
                return None
            else:
                regionslist[key] = value
    for i in _reporter.Country.to_list():
        if i in regionslist.keys():
            logging.debug("Country or region already exists cannot overwrite.")
            raise InputError
            return None
        regionslist[i] = [i]


# The following method connects to the COMTRADE API using request from urlopen module.
# Several inputs required to connect are provided as optional arguments. The user must
# modify the values of these optional arguments before calling the calculation function.

# Method 3
def COMTRADE_API(
    year="2010",
    country="276",
    commodity="2602",
):
    try:
        _request = (
            "https://comtrade.un.org/api/get?max=50000&type=C&freq=A&px="
            "HS&ps=" + str(year) + "&r=" + str(country) + "&p="
            "all&cc=" + str(commodity) + "&rg=1&fmt=json"
        )
    except Exception as e:
        logging.debug(e)
        raise InputError

    # # Section 3.1 connects to the COMTRADE API using the requests method of urlopen library.
    # The user must provide inputs to all of the non-default arguments for most
    # accurate and intended results. A request statement is prepared using the
    # inputs that is opened in the following line. Any error in the provided
    # arguments leads to broken request and finally raising an APIError.

    # APIError is a defined Exception class available in the warningsgprs.

    # 3.1 Section to connect to the COMTRADE API

    # logging.debug(_request) #Uncomment to debug the error
    try:
        request = Request(_request)
        response = urlopen(request)
    except Exception as e:
        logging.debug(e)
        raise APIError
        return None

    # 3.2 Section to read the request result
    try:
        elevations = response.read()
    except Exception as e:
        logging.debug(e)
        raise APIError
        return None

    try:
        data = json.loads(elevations)
        data = pd.json_normalize(data["dataset"]).fillna(0)
    except Exception as e:
        logging.debug(e)
        raise APIError
        return None

    # 3.3 Section to extract the results to variables

    if data.shape[0] != 0:
        err = data.ptCode.to_list().index(0)
        data = data.drop(data.index[[err]])
        code = data.ptCode.to_list()
        countries = data.ptTitle.to_list()
        quantity = data.TradeQuantity.to_list()

        TradeData = [code, countries, quantity]
    else:
        logging.debug(_request)
        logging.debug("API returned empty dataframe")

        TradeData = [None, None, None]
    return TradeData


# Method 4
def InputTrade(sheetname=None):
    trade_path = tradepath

    # This function reads the trade file specific to an organization/company.
    # It is possible to read excel or csv file. Section 1 validates if the
    # path to the file is set using method 1 and reads the file into a dataframe.

    # 4.1 Section to validate the path to trade file
    if trade_path == None:
        raise IncompleteProcessFlow
        return None
    else:

        # The file must be either in excel or csv file, failing which raises an
        # InputError from the warningsgprs module

        if Path(trade_path).suffix == ".xlsx" or Path(trade_path).suffix == ".xls":
            try:
                data = pd.read_excel(trade_path, sheet_name=sheetname)
            except Exception as e:
                logging.debug(e)
                raise FileNotFoundError
                return None
        elif Path(trade_path).suffix == ".csv":
            try:
                data = pd.read_csv(trade_path)
            except Exception as e:
                logging.debug(e)
                raise FileNotFoundError
                return None
        else:
            logging.debug(Path(trade_path).suffix)
            raise FileNotFoundError
            return None

        # The comtrade API results are categorized by imports to a region/country
        # per country and it includes the total imports to the region/country. The
        # code removes such imports to avoid erronous calculation.

        try:
            data = data[list(data.keys())[0]]
            if data.shape[0] != 0:
                try:
                    if 0 in data.ptCode.to_list():
                        Worldindex = data.ptCode.to_list().index(0)
                        data = data.drop(data.index[[Worldindex]])
                    else:
                        logging.debug("No worldindex found")
                except Exception as e:
                    logging.debug(e)
                code = data.ptCode.to_list()
                countries = data.ptTitle.to_list()
                quantity = data.TradeQuantity.to_list()
                TradeData = [code, countries, quantity]
            else:
                TradeData = [None, None, None]
            return TradeData

        except Exception as e:
            logging.debug(e)
            raise APIError
            return None


# The GeoPolRisk method is built with three components, HHI (production concentration),
# weighted trade average (WTA), yearly average price of the resource. With the
# extracted trade information either using COMTRADE or individual trade is weighted
# using a governance indicator and then averaged using the total imports and domestic
# production of the resource.

# The method 'WTA_calculation' requires the year, trade data, governance indicator,
# recycling rate and recycling scenario as inputs.


def WTA_calculation(
    year, TradeData=None, PIData=None, scenario=0, recyclingrate=0.00
):
    if TradeData is None or PIData is None:
        logging.debug("Trade data returned empty!")
        raise IncompleteProcessFlow
        return None
    elif TradeData[0] is not None:
        code, quantity = TradeData[0], TradeData[2]
        reducedmass, totalreduce = 0, 0

        # 1.2 Section to calculate the numerator and trade total
        try:
            PIData = PIData.fillna(0)
            PIData.columns = PIData.columns.astype(str)
            PI_year = [str(i) for i in PIData.Year.to_list()]
        except Exception as e:
            logging.debug(e)
            raise Exception
            return None
        try:
            index = PI_year.index(year)
            PI_score = []
            for i in code:
                if str(i) in PIData.columns.to_list():
                    PI_score.append(PIData[str(i)].tolist()[index])
                else:
                    # The political instability score from the WGI is not provided for few countries
                    # We assign them a score of 0.5 as most of these countries fall in this range
                    PI_score.append(0.5)
        except Exception as e:
            logging.debug(e)
            raise CalculationError
            return None

        # Version 0.2: Domestic recycling mitigates the supply risk of a raw material. However domestic recycling
        # can be attributed to decrease of imports from a country with low WGI score or high WGI score.
        # In other words, there can be two scenarios where imports are reduced from
        # a riskier country (best case scenario) or imports are reduced from
        # much stable country (worst case scenario). Both the cases are determined by the
        # WGI score, a higher WGI score is for a riskier country while lower for a stable
        # country. The following code intends to manipulate the trade data to incorporate
        # the domestic recycling.

        # Recyclability factor of GeoPolRisk

        # Usually users are supposed to provide an input between 0 and 1
        if recyclingrate >= 1.00001 and recyclingrate < 100:
            recyclingrate = recyclingrate / 100
        else:
            logging.debug(
                f"Recycling Rate out of bounds| Recycling Rate : {recyclingrate}"
            )
            recyclingrate = 0

        # The mitigation due to recycling has a redistribution and reduction effect
        # The reduction effect is symbolical because the reduced trade is included in the domestic production
        # Two cases are assumed for the redistribution
        # The function takes in the trade quantity, political instability indicator and sum of the trade quantity
        # This function sorts and reduces the trade quantity based on the scenario and returns the reduced quantity
        def redistribution(quantity, indicator, totQ, reverse):
            totQ = totQ * recyclingrate
            temp = [(v, i) for i, v in enumerate(indicator)]
            temp.sort(reverse=reverse)
            sortedVal, sortedInd = zip(*temp)
            dump = 0
            for i, n in enumerate(sortedInd):
                dump += quantity[n]
                if (totQ - dump) < quantity[sortedInd[i + 1]]:
                    quantity[sortedInd[i + 1]] = quantity[sortedInd[i + 1]] - (
                        totQ - dump
                    )
                    quantity[n] = 0
                    break
                else:
                    quantity[n] = 0
            return quantity

        # newdf = pd.DataFrame(columns = ["trade", "indicator", "tradetotal", "numerator", "production"])
        totQ = sum(quantity)
        try:
            if scenario == 1:  # Best case scenario
                newquantity = redistribution(quantity, PI_score, totQ, True)
                zipped_list = zip(newquantity, PI_score)
                wgiavg = [x * y for (x, y) in zipped_list]
                print(wgiavg)
                # newdf["trade"] = newquantity
                # newdf["indicator"] = PI_score
            elif scenario == 2:  # Worst case scenario
                newquantity = redistribution(quantity, PI_score, totQ, False)
                zipped_list = zip(newquantity, PI_score)
                wgiavg = [x * y for (x, y) in zipped_list]
                print(wgiavg)
            elif scenario == 0:  # No scenario
                try:
                    zipped_list = zip(quantity, PI_score)
                    wgiavg = [x * y for (x, y) in zipped_list]
                    print(wgiavg)
                except TypeError as e:
                    logging.debug(e)
                    logging.debug("The Comtrade API is broken")
                    raise CalculationError
        except Exception as e:
            logging.debug(e)
            raise CalculationError
            return None

        # After manipulation of the trade data it is multiplied with the WGI
        # score forming the numerator of the second factor of GeoPolRisk (WTA)

        try:
            numerator = sum(wgiavg)
            tradetotal = totQ
            # newdf["numerator"] = numerator
            # newdf["tradetotal"] = tradetotal
        except Exception as e:
            logging.debug(e)
            raise CalculationError
        # newdf.to_csv(_outputfile+'/TRADE.csv')
        return numerator, tradetotal
    else:
        return 0, 0


# The first component of the GeoPolRisk method involved calculating the herfindahl-hirschmann
# index (HHI) and total domestic production required for calculating the second factor (WTA).


def productionQTY(Resource, EconomicUnit):

    EconomicUnit = "EU" if EconomicUnit == "European Union" else EconomicUnit
    EconomicUnit = regionslist[EconomicUnit]
    try:
        prod = _production[Resource]
        Countries = prod.Country.to_list()
    except Exception as e:
        logging.debug(e)
        logging.warning(
            "There was an error while acessing the production data file with an exception as ",
            exc_info=True,
        )
        raise FileNotFoundError
        return None

    # P2. Fetching the production quantity from 'prod' dataframe.
    try:
        Prod_Year = prod.columns.to_list()[1:]
        temp = [0] * len(Prod_Year)
        for i in EconomicUnit:
            if i in Countries:
                Prod_Qty = prod[i].values.tolist()
                for k in range(len(Prod_Qty)):
                    if str(Prod_Qty[k]) == "nan" or Prod_Qty[k] is None:
                        Prod_Qty[k] = 0
                Prod_Qty = [sum(j) for j in zip(temp, Prod_Qty)]
                temp = Prod_Qty
            else:
                Prod_Qty = temp
    except Exception as e:
        logging.debug(e)
        raise CalculationError
        return None
    # logging.debug("The following will be the list of data", "This is the country "+str(i), "Next should be the list ",str(self.Prod_Qty))

    # P3. Calculating the HHI.
    Nom = pd.Series()
    try:
        for i in range(1, prod.shape[1]):
            temp = prod.iloc[:, i] * prod.iloc[:, i]
            Nom = Nom.add(temp, fill_value=0)
        DeNom = prod.sum(axis=1)
        hhi = (Nom / (DeNom * DeNom)).tolist()
        HHI = [round(i, 3) for i in hhi]
    except Exception as e:
        logging.debug(e)
        raise CalculationError
        return None
    return [HHI, Prod_Qty, Prod_Year]


def GeoPolRisk(ProductionData, WTAData, Year, AVGPrice):
    newdf = pd.DataFrame(columns=["production"])
    Index = ProductionData[2].index(int(Year))
    HHI = ProductionData[0][Index]
    PQT = ProductionData[1][Index] * 1000

    try:
        if isinstance(AVGPrice, (int, float)) and WTAData[1] != 0:
            WTA = WTAData[0] / (WTAData[1] + PQT)
            GeoPolRisk = HHI * WTA
            GeoPolCF = GeoPolRisk * AVGPrice
        elif WTAData[1] != 0:
            WTA = WTAData[0] / (WTAData[1] + PQT)
            GeoPolRisk = HHI * WTA
            GeoPolCF = "NA"
        else:
            WTA = 0
            GeoPolRisk = 0
            GeoPolCF = 0
            logging.debug("WTA has returned 0")
    except Exception as e:
        logging.debug(e)
        logging.debug("The Weighted Trade average value is {}".format(WTA))
        logging.debug("The HHI value is {}".format(HHI))
        logging.debug("The GeoPolRisk is {}".format(GeoPolRisk))
        logging.debug("The AVGPrice is {}".format(AVGPrice))
        raise CalculationError
        return None
    return [HHI, WTA, GeoPolRisk, GeoPolCF]
