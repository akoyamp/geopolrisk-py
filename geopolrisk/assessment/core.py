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

import pandas as pd, json
from urllib.request import Request, urlopen
from pathlib import Path
from .__init__ import instance, logging, execute_query
from .utils import *


# Define class for storing the path information for trade data
class classPath:
    tradepath = None


classpath = classPath()

# Create instances of data required for calculation of the GeoPolRisk
try:
    # All instances are extracted from the library database
    _production, _reporter = instance.production, instance.reporter
    regionslist, _outputfile = instance.regionslist, instance.exportfile
    db = _outputfile + "/" + instance.Output
except Exception as e:
    logging.debug(f"Error with database files or init file {e}")


# Function to set the path of the trade data file for specific trade data calculation
# Provide the absolute path of the trade data file or relative to the current working directory
def settradepath(path):
    tradepath = path
    try:
        df = pd.read_excel(tradepath)
        classpath.tradepath = path
    except FileNotFoundError:
        logging.debug(f"File {tradepath} not found")
        tradepath = None
    except Exception as e:
        logging.debug(e)
        tradepath = None
    return tradepath


# Function to define new regions
# Provide a dictionary of the new regions
# The key should be the name of the negion
# The value should be the list of countries in the new region
# In case of using aggregate function from the main module,
# use the key as the country
def regions(*args):
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
                if str(x) not in _reporter.Country.to_list()
                and str(x) not in _reporter["ISO"].astype(str).tolist()
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
                regionslist[key] = value
    # The function must be called before calling any other functions in the core
    # module. The following lines populate the region list with all the countries
    # in the world including EU defined in the init file.
    for i in _reporter.Country.to_list():
        if i in regionslist.keys():
            logging.debug("Country or region already exists cannot overwrite.")
        regionslist[i] = [i]
    return regionslist


# Extrade the trade data using the COMTRADE API
def worldtrade(
    year="2010",
    country="276",
    commodity="2602",
):
    try:
        # pricecif is the cif price of traded commodity
        # it is included in case of change of methodology or
        # unavailability of price data from USGS or LME
        data = oldapirequest(year, country, commodity)
    except Exception as e:
        logging.debug(f"Error with the comtrade API request: {e}")

    if data is None or data.shape[0] == 0:
        data, pricecif = callapirequest(year, country, commodity)
        if data is None or data.shape[0] == 0:
            logging.debug("API returned empty dataframe")
            TradeData = [None, None, None], None
        else:
            if 0 in data.partnerCode.astype(int).to_list():
                err = data.partnerCode.to_list().index(0)
                data = data.drop(data.index[[err]])
                logging.info(
                    "Partner code 0 is found in the trade file. "
                    "Please check the trade file."
                )
            try:
                code = data.partnerCode.to_list()
                countries = data.partnerDesc.to_list()
                quantity = data.Qty.to_list()
                cifvalue = data.Cifvalue.to_list()
                pricecif = sum(cifvalue)/sum(quantity)
                TradeData = [code, countries, quantity]
            except Exception as e:
                logging.debug(
                    f"The fetched dataframe from "
                    "the API does not have the required columns. {e}"
                )
                TradeData = [None, None, None], None
    elif data is not None and data.shape[0] != 0:
        if data is not None and data.shape[0] != 0:
            Worldindex = data.ptCode.to_list().index(0)
            data = data.drop(data.index[[Worldindex]])
            code = data.ptCode.to_list()
            countries = data.ptTitle.to_list()
            quantity = data.TradeQuantity.to_list()
            TradeData = [code, countries, quantity]
        else:
            logging.debug("API returned empty dataframe")
            TradeData = [None, None, None], None
    else:

        logging.info("API returned empty dataframe")
        TradeData = [None, None, None], None
    return TradeData, pricecif


# Extract trade data from the specific trade data file whose path is defined in
# the method earlier.
def specifictrade(sheetname=None):
    trade_path = classpath.tradepath

    # This function reads the trade file specific to an organization/company.
    # It is possible to read excel or csv file. Section 1 validates if the
    # path to the file is set using method 1 and reads the file into a dataframe.

    # 4.1 Section to validate the path to trade file
    if trade_path == None:
        logging.debug("Trade file path is not set.")
        return None
    else:

        # The file must be either in excel or csv file, failing which raises an
        # InputError from the warningsgprs module

        if Path(trade_path).suffix == ".xlsx" or Path(trade_path).suffix == ".xls":
            try:
                data = pd.read_excel(trade_path, sheet_name=sheetname)
            except Exception as e:
                logging.debug(f"Error while accessing the trade file {e}")
                return None
        elif Path(trade_path).suffix == ".csv":
            try:
                data = pd.read_csv(trade_path)
            except Exception as e:
                logging.debug(f"Error while accessing the trade file {e}")
                return None
        else:
            logging.debug(Path(trade_path).suffix)
            return None

        # The comtrade API results are categorized by imports to a region/country
        # per country and it includes the total imports to the region/country. The
        # code removes such imports to avoid erronous calculation.
        try:
            if data.shape[0] != 0:
                if 0 in data.ptCode.astype(int).to_list():
                    err = data.ptCode.to_list().index(0)
                    data = data.drop(data.index[[err]])
                    logging.info(
                        "Partner code 0 is found in the trade file. "
                        "Please check the trade file."
                    )
                try:
                    code = data.ptCode.to_list()
                    countries = data.ptTitle.to_list()
                    quantity = data.TradeQuantity.to_list()
                    TradeData = [code, countries, quantity]
                except Exception as e:
                    logging.debug(
                        f"The fetched dataframe from "
                        f"the API does not have the required columns. {e}"
                    )
                    TradeData = None
            else:
                logging.info("API returned empty dataframe")
                TradeData = None
            return TradeData
        except Exception as e:
            logging.debug(f"Error in the trade file {e}")
            return None


# Fetch the mineral resource ore production data from the library
def ProductionData(Resource, EconomicUnit):

    EconomicUnit = "EU" if EconomicUnit == "European Union" else EconomicUnit
    EconomicUnit = regionslist[EconomicUnit]
    try:
        prod = _production[Resource].fillna(0)
        Countries = prod.Country.to_list()
    except Exception as e:
        logging.debug(
            f"There was an error while acessing"
            f" the production data file with an exception as {e}"
        )
        return None

    # P2. Fetching the production quantity from 'prod' dataframe.
    try:
        Prod_Year = prod.columns.to_list()[1:-1]
        Prod_Year = [int(i) for i in Prod_Year]
        temp = [0] * len(Prod_Year)
        for i in EconomicUnit:
            if i in Countries:
                Prod_Qty = (
                    prod.loc[prod["Country"] == i]
                    .reset_index()
                    .loc[0, :]
                    .values.flatten()
                    .tolist()[2:-1]
                )
                Prod_Qty = replace_values(Prod_Qty, "^", 0)
                Prod_Qty = [float(i) for i in Prod_Qty]
                Prod_Qty = [sum(j) for j in zip(temp, Prod_Qty)]
                temp = Prod_Qty
            else:
                Prod_Qty = temp
    except Exception as e:
        logging.debug(f"Error while processing production data {e}")
        return None

    # P3. Calculating the HHI.
    HHI = []
    try:
        for i in Prod_Year:
            temp = prod[str(i)].values.tolist()
            temp = replace_values(temp, "^", 0)
            temp = [float(i) for i in temp]
            DeNom = sum(temp)
            Nom = sum([j[0] * j[1] for j in zip(temp, temp)])
            try:
                HHI.append(round(Nom / (DeNom * DeNom), 3))
            except Exception as e:
                HHI.append(0)
    except Exception as e:
        logging.debug(f"Error while calculating the HHI {e}")
        return None
    length = len(Prod_Year)
    if all(len(lst) == length for lst in [Prod_Qty, HHI]):
        return [HHI, Prod_Qty, Prod_Year]
    else:
        return None


# Weight the extracted trade data with the political instability indicator data.
# WGI is used as the default PI indicator that can be replaced with any other
# normalized indicator data.
def weightedtrade(year, TradeData=None, PIData=None, scenario=0, recyclingrate=0.00):
    if TradeData is None or PIData is None:
        logging.debug("Trade data or Indicator data returned empty!")
        return None
    elif TradeData is not None:
        code, quantity = TradeData[0], TradeData[2]
        reducedmass, totalreduce = 0, 0

        # 1.2 Section to calculate the numerator and trade total
        try:
            PIData = PIData.fillna(0)
            PIData.columns = PIData.columns.astype(str)
            PI_year = [str(i) for i in PIData.Year.to_list()]
        except Exception as e:
            logging.debug(f"Error while working with Indicator Data {e}")
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
            logging.debug(f"Error while working with Indicator Data {e}")
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
        elif recyclingrate >= 0 and recyclingrate < 1.00001:
            recyclingrate = recyclingrate
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
            try:
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
            except Exception as e:
                logging.debug(f"Error while redistributing the trade {e}")
                quantity = None
            return quantity

        totQ = sum(quantity)
        if scenario == 1:  # Best case scenario
            newquantity = redistribution(quantity, PI_score, totQ, True)
            if newquantity is not None:
                try:
                    zipped_list = zip(newquantity, PI_score)
                    wgiavg = [x * y for (x, y) in zipped_list]
                except Exception as e:
                    logging.debug(f"Error while weighting the trade data {e}")
                    return None
            else:
                logging.debug("Error while redistributing the trade")
                return None
        elif scenario == 2:  # Worst case scenario
            newquantity = redistribution(quantity, PI_score, totQ, False)
            if newquantity is not None:
                try:
                    zipped_list = zip(newquantity, PI_score)
                    wgiavg = [x * y for (x, y) in zipped_list]
                except Exception as e:
                    logging.debug(f"Error while weighting the trade data {e}")
                    return None
            else:
                logging.debug("Error while redistributing the trade")
                return None
        elif scenario == 0:  # No scenario
            try:
                zipped_list = zip(quantity, PI_score)
                wgiavg = [x * y for (x, y) in zipped_list]
            except Exception as e:
                logging.debug(f"Error while weighting the trade data {e}")
                return None

        # After manipulation of the trade data it is multiplied with the WGI
        # score forming the numerator of the second factor of GeoPolRisk (WTA)

        try:
            numerator = sum(wgiavg)
            tradetotal = totQ
        except Exception as e:
            logging.debug(f"Error while summing the weighted trade data{e}")
        return numerator, tradetotal
    else:
        return 0, 0


# The first component of the GeoPolRisk method involved calculating the herfindahl-hirschmann
# index (HHI) and total domestic production required for calculating the second factor (WTA).
def GeoPolRisk(ProductionData, WTAData, Year, AVGPrice):
    newdf = pd.DataFrame(columns=["production"])
    Index = ProductionData[2].index(int(Year))
    HHI = ProductionData[0][Index]
    PQT = ProductionData[1][Index] * 1000  # Converting from Mtonnes to kilograms
    if isinstance(AVGPrice, (int, float)) and WTAData[1] != 0:
        try:
            WTA = WTAData[0] / (WTAData[1] + PQT)
            GeoPolRisk = HHI * WTA
            GeoPolCF = GeoPolRisk * AVGPrice
        except Exception as e:
            logging.debug(f"Error while calculating GeoPolRisk {e}")
            return None
    elif WTAData[1] != 0:
        try:
            WTA = WTAData[0] / (WTAData[1] + PQT)
            GeoPolRisk = HHI * WTA
            GeoPolCF = "NA"
        except Exception as e:
            logging.debug(f"Error while calculating GeoPolRisk {e}")
            return None
    else:
        WTA = 0
        GeoPolRisk = 0
        GeoPolCF = 0
        logging.info("WTA has returned 0")
        return None
    results = [HHI, WTA, GeoPolRisk, GeoPolCF]
    return results
