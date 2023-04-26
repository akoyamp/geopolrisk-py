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

from .__init__ import (
    instance,
    logging,
    Filename,
    outputdf,
    execute_query,
)
import numpy as np
from .core import *
import itertools, pandas as pd, time
from .utils import *
import sys

"""
The module implements the functions of the core module for ease of use.
Provide the list of mineral resources, countries and year to the main function.
Call the regions function to define any custom regions. Call the settradepath
function to define the trade data for specific trade calculation. 
The main function verifies if the above said functions are called or not to 
automatically detect the type of calculation required.
"""


try:
    regionslist, _outputfile = instance.regionslist, instance.exportfile
    _reporter = instance.reporter
    Country = _reporter.Country.to_list()
    _price = instance.price
    _wgi = instance.wgi
    db = _outputfile + "/" + instance.Output
    OutputList = outputdf.outputList
    counter, totalcounter, emptycounter = 0, 0, 0
except Exception as e:
    logging.debug(f"Error with database files or init file {e}")


def tradeagg(resource, year, listofcountries, sheetname=None):
    """
    This function is used to aggregate the trade data from COMTRADE API.
    The trade data is aggregated (summed) which is then
    processed for further calculation.
    """
    # resources is hs code of the commodity
    # New variables to aggregate trade data from COMTRADE API
    newcodelist = []
    newcountrylist = []
    newquantitylist = []
    # TradeData (from core module) fetchs the ISO country code,
    # country names and trade quantity in KG from COMTRADE
    newtradelist = [
        newcodelist,
        newcountrylist,
        newquantitylist,
    ]
    pricecifAGG = []
    # Variable to fetch production data
    TotalDomesticProduction, TDP = 0, []
    # If the aggregation is not from the specific trade data source,
    # then its not necessary to call the settradepath function and
    # input sheetname as None.
    if sheetname is None:
        for k in listofcountries:
            try:
                TradeData, pricecif = worldtrade(
                    year=year,
                    country=k,
                    commodity=resource,
                )
            except Exception as e:
                logging.debug(
                    f"""Failed COMTRADE attempt!: resource - {resource}
                            country - {k}, year - {year}, : {e}"""
                )
            # Logging null return of the trade data from the world trade.
            if (
                isinstance(TradeData[0], type(None))
                or len(TradeData) == 0
                or any(v is None for v in TradeData[0])
            ):
                logging.debug(f"Trade of {resource} to {k} returned None for {year}")
                newcodelist.append(0)
                newcountrylist.append(0)
                newquantitylist.append(0)
                pricecifAGG.append(0)
            else:
                # code to aggregate the data
                TradeData[2] = [0 if v is None else v for v in TradeData[2]]
                for ind, n in enumerate(TradeData[0]):
                    # Aggregation of the trade data
                    # EX: for a region of two countries (A, B) that import from similar set of countries
                    # The aggregation is the sum of the trade quantities for the two countries (A, B)
                    if n not in newcodelist:
                        newcodelist.append(n)
                        newquantitylist.append(TradeData[2][ind])
                        newcountrylist.append(TradeData[1][ind])
                    else:
                        index = newcodelist.index(n)
                        newquantitylist[index] = (
                            newquantitylist[index] + TradeData[2][ind]
                        )
                pricecifAGG.append(pricecif)
                
                logging.debug(f"The aggregated trade quantity {newtradelist}")
            avgpricecif = sum(pricecif)/len(pricecif)
            # Aggregation of the production of mineral resource data
            xresource, country, _ignore, _ignore2 = convertCodes(resource, k)
            X = ProductionData(xresource, country)
            index = X[2].index(year)
            TotalDomesticProduction += X[1][index]
            logging.info(f"The aggegated production quantity {TotalDomesticProduction}")
    else:
        TradeData = specifictrade(sheetname)
        for k in listofcountries:
            xresource, country, _ignore, _ignore2 = convertCodes(resource, k)
            X = ProductionData(xresource, country)
            index = X[2].index(year)
            TotalDomesticProduction += X[1][index]
        newtradelist = TradeData
        pricecif = None
    # Calculation of the components of the GeoPolRisk method
    TDP = [0] * len(X[1])
    TDP[X[2].index(year)] = TotalDomesticProduction
    productiondata = [X[0], TDP, X[2]]

    return newtradelist, productiondata, avgpricecif


def main_complete(
    resourcelist,
    yearlist,
    countrylist,
    recyclingrate=0.0,
    scenario=0,
    sheetname=None,
    PIindicator=None,
):

    if PIindicator is None:
        PIindicator = _wgi
    # Instantiate counters for logging
    logging.info("Running")
    newregion = []
    if len(regionslist) > 1:
        logging.info("Regional calculation started!")
        newregionlist = []
        # Compare if the region already exists withing the library.
        newregion = [
            i
            for i, x in enumerate(countrylist)
            if str(x) not in Country or str(x) not in [str(i) for i in ISO]
        ]
        logging.info(f"List of new regions {newregion}")

        # Extract new regions from the provided countrylist parameter (argument).
        if len(newregion) > 0:
            for i in newregion:
                newregionlist.append(countrylist[i])
                del countrylist[i]
        if len(newregionlist) > 0:  # Calculate the values for the new region(s)
            for l in newregionlist:
                # New regions can be defined as ISO nomenclature or ISO numeric.
                #  The values must be converted to numeric.newcountrylist
                ncountrylist = regionslist[l]
                logging.info(
                    f"The new region defined {l} and the countries in it are {ncountrylist}"
                )
                _ignore1, _ignore2, _ignore3, Xcountrylist = convertCodes(
                    ["Cobalt"], ncountrylist
                )

                # Iterate the resources, year for COMTRADE query
                for I in itertools.product(resourcelist, yearlist):
                    # LOGIC
                    DBID = create_id(I[0], l, I[1])
                    try:
                        verify = sqlverify(DBID)
                    except Exception as e:
                        logging.debug(f"SQL Verification failed! {e}")
                    if verify is False:
                        time.sleep(2)
                        TradeData, productiondata, avgpricecif = tradeagg(I[0], I[1], Xcountrylist)
                        if avgpricecif in [np.nan, 0, "nan"]:
                            AVGPrice = _price[str(I[1])].tolist()[
                            _price.HS.to_list().index(I[0])
                        ]
                        else:
                            AVGPrice = avgpricecif
                        Y = weightedtrade(
                            str(I[1]),
                            TradeData=TradeData,
                            PIData=PIindicator,
                            scenario=scenario,
                            recyclingrate=recyclingrate,
                        )
                        if Y is not None and productiondata is not None:
                            result = GeoPolRisk(productiondata, Y, str(I[1]), AVGPrice)
                            if result is not None:
                                HHI, WTA, Risk, CF = (
                                    result[0],
                                    result[1],
                                    result[2],
                                    result[3],
                                )
                            else:
                                HHI, WTA, Risk, CF = 0, 0, 0, 0
                        else:
                            HHI, WTA, Risk, CF = 0, 0, 0, 0
                        # Final outputs from the GeoPolRisk calculation
                        logging.info(
                            f"""
                        GeoPolRisk calculation completed successfully! The following
                        values are calculated: {HHI}, {WTA}, {Risk}, {CF} for resource {I[0]}
                        , year {I[1]} to region {l} with recyclingrate {recyclingrate} and 
                        scenario {scenario}
                        """
                        )
                        resource, _ignore1, _ignore2, _ignore3 = convertCodes(I[0], 174)
                        # Record or update data
                        recordData(
                            resource,
                            l,
                            I[1],
                            recyclingrate,
                            scenario,
                            Risk,
                            CF,
                            HHI,
                            WTA,
                            Filename,
                            OutputList,
                        )
                    else:
                        try:
                            sqlstatement = f""" SELECT  geopolrisk, hhi, wta, geopol_cf FROM
                            recordData WHERE id = '{DBID}'
                            """
                            row = execute_query(sqlstatement, db_path=db)
                            OutputList.append(
                                [
                                    str(I[1]),
                                    str(resource),
                                    str(l),
                                    str(recyclingrate),
                                    str(scenario),
                                    str(row[0][0]),
                                    str(row[0][3]),
                                    str(row[0][1]),
                                    str(row[0][2]),
                                ]
                            )
                        except Exception as e:
                            logging.debug(f"Cannot append into list of records {e}")
                        logging.debug(
                            "No transaction has been made. "
                            "Preexisting data has been inserted in output file."
                        )
        else:
            startmain(
                resourcelist,
                yearlist,
                countrylist,
                recyclingrate=0.0,
                scenario=0,
                sheetname=None,
                PIindicator=None,
            )
    else:
        regions()
        startmain(
            resourcelist,
            yearlist,
            countrylist,
            recyclingrate=0.0,
            scenario=0,
            sheetname=None,
            PIindicator=None,
        )

    endmain()


def startmain(
    resourcelist,
    yearlist,
    countrylist,
    recyclingrate=0.0,
    scenario=0,
    sheetname=None,
    PIindicator=None,
):
    if PIindicator is None:
        PIindicator = _wgi
    for I in itertools.product(resourcelist, countrylist, yearlist):
        # LOGIC
        # Need to verify if the data preexists to avoid limited API calls
        resource, country, _ignore, _ignore1 = convertCodes(I[0], I[1])
        DBID = create_id(I[0], I[1], I[2])
        try:
            verify = sqlverify(DBID)
        except Exception as e:
            logging.debug(f"Error with sqlverify or DBID {e}")
        if verify is False:
            # The program has to sleep inorder to avoid conflict in multiple API requests
            time.sleep(2)
            if sheetname is None:
                try:
                    TradeData, pricecif = worldtrade(
                        year=I[2],
                        country=I[1],
                        commodity=I[0],
                    )
                except Exception as e:
                    logging.debug(f"Error accessing world trade data {e}")
                    counter -= 1
                    break
            else:
                try:
                    TradeData = specifictrade(
                        year=I[2],
                        country=I[1],
                        commodity=I[0],
                    )
                except Exception as e:
                    logging.debug(f"Error accessing specific trade data {e}")
                    break

            try:
                if pricecif in [np.nan, 0, "nan"]:
                    AVGPrice = _price[str(I[2])].tolist()[_price.HS.to_list().index(I[0])]
                else:
                    AVGPrice = pricecif
                X = ProductionData(resource, country)
                Y = weightedtrade(
                    str(I[2]),
                    TradeData=TradeData,
                    PIData=PIindicator,
                    scenario=scenario,
                    recyclingrate=recyclingrate,
                )
                if Y is not None and X is not None:
                    result = GeoPolRisk(X, Y, str(I[2]), AVGPrice)
                    if result is not None:
                        HHI, WTA, Risk, CF = (
                            result[0],
                            result[1],
                            result[2],
                            result[3],
                        )
                    else:
                        HHI, WTA, Risk, CF = 0, 0, 0, 0
                else:
                    HHI, WTA, Risk, CF = 0, 0, 0, 0
            except Exception as e:
                logging.debug(
                    f"Error unpacking the production data/weighted trade data/price data {e}"
                )
                continue

            recordData(
                resource,
                country,
                I[2],
                recyclingrate,
                scenario,
                Risk,
                CF,
                HHI,
                WTA,
                Filename,
                OutputList,
            )
        else:
            try:
                sqlstatement = f""" SELECT  geopolrisk, hhi, wta, geopol_cf FROM
                recordData WHERE id = '{DBID}'
                """
                row = execute_query(sqlstatement, db_path=db)
                OutputList.append(
                    [
                        str(I[1]),
                        str(resource),
                        str(country),
                        str(recyclingrate),
                        str(scenario),
                        str(row[0][0]),
                        str(row[0][3]),
                        str(row[0][1]),
                        str(row[0][2]),
                    ]
                )
            except Exception as e:
                logging.debug(f"Cannot append into list of records {e}")
            logging.debug(
                "No transaction has been made. "
                "Preexisting data has been inserted in output file."
            )


def endmain():
    outputDF = pd.DataFrame(OutputList, columns=outputdf.columns)
    outputDF.to_csv(_outputfile + "/export.csv", index=False, encoding="utf-8")
    logging.info("GeoPolRisk calculation completed successfully!")


def update_cf():
    # Fetch Missing Data
    sqlstatement = (
        "SELECT resource_hscode, year, iso, geopol_cf FROM recordData WHERE "
        " wta = '0';"
    )
    row = execute_query(sqlstatement, db_path=db)
    df = pd.DataFrame(
        row, columns=["HS Code", "Year", "Country Alpha", "Characterziation Factors"]
    )
    logging.debug("Update of database! The shape of df is " + str(df.shape[0]))
    if df.shape[0] > 0:
        Year = [int(i) for i in df.Year.to_list()]
        ISO = [int(i) for i in df["Country Alpha"].tolist()]
        HS = [int(i) for i in df["HS Code"].tolist()]
    else:
        logging.debug("No updates required!")
        return None
    try:
        startmain(HS, Year, ISO, 0, 0)
        endmain()
    except Exception as e:
        logging.debug(f"Error while updating CF! {e}")


# Run this function if there is an update in the missing price data in the average yearly price json.
def updateprice():
    logging.info("Updating the characterization prices | price")
    sqlstatement = (
        "SELECT resource_hscode, year, iso, geopolrisk FROM recordData WHERE "
        " geopol_cf = 'NA' AND recycling_rate ='0' AND scenario ='0';"
    )
    row = execute_query(sqlstatement)
    df = pd.DataFrame(row, columns=["HS Code", "Year", "Country Alpha", "GeoPolRisk"])
    logging.debug("Update of database! The shape of df is " + str(df.shape[0]))
    if df.shape[0] > 0:
        Year = [int(i) for i in df.Year.to_list()]
        ISO = [int(i) for i in df["Country Alpha"].tolist()]
        _HS = [int(i) for i in df["HS Code"].tolist()]
        GPRS = [float(i) for i in df["GeoPolRisk"].tolist()]
    else:
        logging.debug("No updates required!")
        return None
    for i, n in enumerate(_HS):
        AVGPrice = _price[str(Year[i])].tolist()[_price.HS.to_list().index(n)]
        if isinstance(AVGPrice, (int, float)):
            index = ISO.index(ISO[i])
            CF = float(GPRS[index]) * AVGPrice
            sqlstatement = (
                "UPDATE recordData SET geopol_cf= '"
                + str(CF)
                + "', log_ref='"
                + str(Filename)
                + "' WHERE iso = '"
                + str(ISO[i])
                + "' AND resource_hscode= '"
                + str(n)
                + "' AND year = '"
                + str(Year[i])
                + "' AND recycling_rate = '0' AND scenario = '0';"
            )
            norow = execute_query(sqlstatement, db_path=db)
            logging.debug(f"Database update sucessfully! for {n} for {Year[i]}")
