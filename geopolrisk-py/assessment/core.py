import pandas as pd, json
from urllib.request import Request, urlopen
from pathlib import Path
from .__init__ import instance, logging, execute_query
from .Exceptions.warningsgprs import *
from .utils import *


# Define Paths
tradepath = None
_production, _reporter = instance.production, instance.reporter
regionslist, _outputfile = instance.regionslist, instance.exportfile
_price = instance.price
db = _outputfile + '/' + instance.Output

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

# Method 3
def worldtrade(
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
def specifictrade(sheetname=None):
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

def productiondata(Resource, EconomicUnit):

    EconomicUnit = "EU" if EconomicUnit == "European Union" else EconomicUnit
    EconomicUnit = regionslist[EconomicUnit]
    try:
        prod = _production[Resource].fillna(0)
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
        Prod_Year = prod.columns.to_list()[1:-1]
        Prod_Year = [int(i) for i in Prod_Year]
        temp = [0] * len(Prod_Year)
        for i in EconomicUnit:
            if i in Countries:
                Prod_Qty = prod.loc[prod['Country'] == i].reset_index().loc[0, :].values.flatten().tolist()[2:-1]
                Prod_Qty = replace_values(Prod_Qty, "^", 0) 
                Prod_Qty = [float(i) for i in Prod_Qty]
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
    HHI = []
    try:
        for i in Prod_Year:
            temp = prod[str(i)].values.tolist()
            temp = replace_values(temp, "^", 0) 
            temp = [float(i) for i in temp]
            DeNom = sum(temp)
            Nom = sum([j[0]*j[1] for j in zip(temp, temp)])
            try:
                HHI.append(round(Nom/(DeNom*DeNom), 3))
            except Exception as e:
                HHI.append(0)
    except Exception as e:
        logging.debug(e)
        raise CalculationError
        return None
    length = len(Prod_Year)
    if all(len(lst) == length for lst in [Prod_Qty, HHI]):
        return [HHI, Prod_Qty, Prod_Year]
    else:
        return None

def weightedtrade(
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
                # newdf["trade"] = newquantity
                # newdf["indicator"] = PI_score
            elif scenario == 2:  # Worst case scenario
                newquantity = redistribution(quantity, PI_score, totQ, False)
                zipped_list = zip(newquantity, PI_score)
                wgiavg = [x * y for (x, y) in zipped_list]
            elif scenario == 0:  # No scenario
                try:
                    zipped_list = zip(quantity, PI_score)
                    wgiavg = [x * y for (x, y) in zipped_list]
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
