from .__init__ import (
    instance,
    logging,
    Filename,
)
from .core import *
import itertools, sqlite3, pandas as pd, time
from .utils import *
import argparse


try:
    regionslist, _outputfile = instance.regionslist, instance.exportfile
    _price = instance.price
    _wgi = instance.wgi
    db = _outputfile + '/' + instance.Output
except Exception as e:
    logging.debug(f"Error with database files or init file {e}")

def main():
    """
    The main function to calculate the GeoPolRisk method.
    """
    # Read the parameters from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--resourcelist",
        type=list,
        default=[],
        help="The list of mineral resources.",
    )
    parser.add_argument(
        "-y",
        "--yearlist",
        type=list,
        default=[],
        help="The list of years.",
    )
    parser.add_argument(
        "-c",
        "--countrylist",
        type=list,
        default=[],
        help="The list of countries.",
    )
    parser.add_argument(
        "-rr",
        "--recyclingrate",
        type=float,
        default=0.0,
        help="The list of countries.",
    )
    parser.add_argument(
        "-s",
        "--scenario",
        type=int,
        default=0,
        help="The list of countries.",
    )
    parser.add_argument(
        "-h",
        "--sheetname",
        type=str,
        default=None,
        help="The name of the output file.",
    )
    parser.add_argument(
        "-w",
        "--PIindicator",
        type=object,
        default=_wgi,
        help="The list of countries.",
    )

    args = parser.parse_args()
    resourcelist = args.resourcelist
    yearlist = args.yearlist
    countrylist = args.countrylist
    recyclingrate = args.recyclingrate
    scenario = args.scenario
    sheetname = args.sheetname
    PIindicator = args.PIindicator
    
    
    if PIindicator is None:
        PIindicator = _wgi

    logging.info("Running")
    if len(regionslist) > 0:
        newregionlist = []
        # Instantiate counters for logging
        counter, totalcounter, emptycounter = 0, 0, 0
        # Compare if the region already exists withing the library.
        newregion = [
            i
            for i, x in enumerate(countrylist)
            if str(x) not in Country
            or str(x) not in [str(i) for i in ISO]
        ]

        # Extract new regions from the provided countrylist parameter (argument).
        if len(newregion) > 0:
            for i in newregion:
                newregionlist.append(countrylist[i])
                del countrylist[i]

        # Calculate the values for the new region(s)
        for l in newregionlist:
            # New regions can be defined as ISO nomenclature or ISO numeric. The values must be converted to numeric.newcountrylist
            ncountrylist = regionslist[l]
            _ignore, Xcountrylist = convertCodes("Cobalt", ncountrylist, output = "numeric")
                
            # Iterate the resources, year for COMTRADE query
            for I in itertools.product(resourcelist, yearlist):
                # LOGIC
                """
                A group of countries such as G7, G8 or region such as middle east,
                ASEAN are declared in the regions function.
                The name of the group or region is provided as 
                the key and the values as a list of countries in the group or region.
                ex: The G7 group can be presented as 
                {"G7" : ["Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "USA"]} or
                ISO numeric can provided instead of the names.

                The logic behind the code is to iterate the list of countries 
                in the group/region and fetch its individual trade data.
                The trade data is aggregated (summed) which is then 
                processed for further calculation.
                """

                try:
                    resource, _ignore = convertCodes(I[0], 124, output = "text")
                    verify = sqlverify(resource, l, I[1], recyclingrate, scenario, outputList)
                except Exception as e:
                    logging.debug(f"SQL Verification failed! {e}")

                if verify is None:
                    time.sleep(5)
                    TradeData , productiondata = tradeagg(I[0], I[1], Xcountrylist)
                    AVGPrice = _price[str(I[1])].tolist()[_price.HS.to_list().index(I[0])]
                    Y = weightedtrade(
                        str(I[1]),
                        TradeData=TradeData,
                        PIData=PIindicator,
                        scenario=scenario,
                        recyclingrate=recyclingrate,
                    )
                    HHI, WTA, Risk, CF = GeoPolRisk(
                        productiondata, Y, str(I[1]), AVGPrice
                    )  # Final outputs from the GeoPolRisk calculation
                    logging.info(f"""
                    GeoPolRisk calculation completed successfully! The following
                    values are calculated: {HHI}, {WTA}, {Risk}, {CF} for resource {I[0]}
                    , year{I[1]} to region {l} with recyclingrate {recyclingrate} and 
                    scenario {scenario}
                    """)
                    
                    outputList.append(
                        [
                            str(I[1]),
                            resource,
                            l,
                            recyclingrate,
                            scenario,
                            Risk,
                            CF,
                            HHI,
                            WTA,
                        ]
                    )

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
                            I[0],
                            l,
                            Filename,
                        )
                else:
                    logging.debug(
                    "No transaction has been made. "
                    "Preexisting data has been inserted in output file."
                )        
    else:
        regions()
        for I in itertools.product(resourcelist, countrylist, yearlist):
            totalcounter += 1
            # Need to verify if the data preexists to avoid limited API calls
            try:
                resource, country = convertCodes(I[0], I[1], "text")
                verify = sqlverify(resource, country, I[2], recyclingrate, scenario, outputList)
            except Exception as e:
                logging.debug(e)

            if verify is None:
                # The program has to sleep inorder to avoid conflict in multiple API requests
                time.sleep(5)
                if sheetname is not None:
                    try:
                        counter += 1
                        TradeData = worldtrade(
                            year=I[2],
                            country=I[1],
                            commodity=I[0],
                        )
                    except Exception as e:
                        logging.debug(e)
                        counter -= 1
                        break
                else:
                    try:
                        counter += 1
                        TradeData = specifictrade(
                            year=I[2],
                            country=I[1],
                            commodity=I[0],
                        )
                    except Exception as e:
                        logging.debug(e)
                        counter -= 1
                        break
                # From the core methods, TradeData is None only when the dataframe is empty
                if TradeData[0] == None or TradeData[0] == 0:
                    emptycounter += 1
                else:
                    pass

                try:
                    AVGPrice = _price[str(I[2])].tolist()[_price.HS.to_list().index(I[0])]
                    X = productiondata(resource, country)
                    Y = weightedtrade(
                        str(I[2]),
                        TradeData=TradeData,
                        PIData=_wgi,
                        scenario=scenario,
                        recyclingrate=recyclingrate,
                    )
                    HHI, WTA, Risk, CF = GeoPolRisk(X, Y, str(I[2]), AVGPrice)
                except Exception as e:
                    logging.debug(e)
                    continue

                outputList.append(
                    [
                        str(I[2]),
                        resource,
                        country,
                        recyclingrate,
                        scenario,
                        Risk,
                        CF,
                        HHI,
                        WTA,
                    ]
                )
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
                        I[0],
                        I[1],
                        Filename,
                    )
            else:
                logging.debug(
                    "No transaction has been made. "
                    "Preexisting data has been inserted in output file."
                )


def tradeagg(resource, year, listofcountries, sheetname):
    """
    This function is used to aggregate the trade data from COMTRADE API.
    The trade data is aggregated (summed) which is then 
    processed for further calculation.
    """
    #resources is hs code of the commodity
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
    #counters
    counter, totalcounter, emptycounter = 0, 0, 0
    # Variable to fetch production data
    TotalDomesticProduction, TDP = 0, []
    if sheetname is not None:  
        for k in listofcountries:
            try:
                TradeData = worldtrade(
                    year=year,
                    country=k,
                    commodity=resource,
                )
                counter += 1
                totalcounter += 1
            except Exception as e:
                logging.debug(
                    f"""Failed COMTRADE attempt!: resource - {resource}
                            country - {k}, year - {year}, : {e}"""
                )

            # counter balance
            if TradeData is None:
                emptycounter += 1
                logging.debug(
                    f"Trade of {resource} to {k} returned None for {year}"
                )
                newtradelist = [[0], [0], [0]]
            else:
                # code to aggregate the data
                for ind, n in enumerate(TradeData[0]):
                    if n not in newcodelist:
                        newcodelist.append(n)
                        newquantitylist.append(TradeData[2][ind])
                        newcountrylist.append(TradeData[1][ind])
                    else:
                        index = newcodelist.index(n)
                        newquantitylist[index] = (
                            newquantitylist[index] + TradeData[2][ind]
                        )
    else:
        TradeData =  specifictrade(sheetname)
        xresource, country = convertCodes(resource, k, "text")
        
        X = productiondata(xresource, country)
        index = X[2].index(year)
        TotalDomesticProduction += X[1][index]

    # Calculation of the components of the GeoPolRisk method
    TDP = [0] * len(X[1])
    TDP[X[2].index(year)] = TotalDomesticProduction
    productiondata = [X[0], TDP, X[2]]

    return newtradelist, productiondata