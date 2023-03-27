from .__init__ import (
    instance,
    logging,
    Filename,
    outputdf,
    execute_query,
)
from .core import *
import itertools, pandas as pd, time
from .utils import *


try:
    regionslist, _outputfile = instance.regionslist, instance.exportfile
    _price = instance.price
    _wgi = instance.wgi
    db = _outputfile + '/' + instance.Output
except Exception as e:
    logging.debug(f"Error with database files or init file {e}")

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
            except Exception as e:
                logging.debug(
                    f"""Failed COMTRADE attempt!: resource - {resource}
                            country - {k}, year - {year}, : {e}"""
                )

            # counter balance
            if TradeData is None:
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
            xresource, country, _ignore, _ignore2 = convertCodes(resource, k)
            X = ProductionData(xresource, country)
            index = X[2].index(year)
            TotalDomesticProduction += X[1][index]
    else:
        TradeData =  specifictrade(sheetname)
        for k in listofcountries:
            xresource, country, _ignore, _ignore2 = convertCodes(resource, k)
            X = ProductionData(xresource, country)
            index = X[2].index(year)
            TotalDomesticProduction += X[1][index]

    # Calculation of the components of the GeoPolRisk method
    TDP = [0] * len(X[1])
    TDP[X[2].index(year)] = TotalDomesticProduction
    productiondata = [X[0], TDP, X[2]]

    return newtradelist, productiondata

def main(
    resourcelist,
    yearlist,
    countrylist,
    recyclingrate = 0.0,
    scenario = 0,
    sheetname = None,
    PIindicator = None

):  
    OutputList = outputdf.outputList
    
    
    if PIindicator is None:
        PIindicator = _wgi
    # Instantiate counters for logging
    counter, totalcounter, emptycounter = 0, 0, 0
    logging.info("Running")
    if len(regionslist) > 1:
        newregionlist = []
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
            _ignore1, _ignore2, _ignore3, Xcountrylist = convertCodes("Cobalt", ncountrylist)
                
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
                    TradeData , productiondata = tradeagg(I[0], I[1], Xcountrylist)
                    AVGPrice = _price[str(I[1])].tolist()[_price.HS.to_list().index(I[0])]
                    Y = weightedtrade(
                        str(I[1]),
                        TradeData=TradeData,
                        PIData=PIindicator,
                        scenario=scenario,
                        recyclingrate=recyclingrate,
                    )
                    if Y is not None and X is not None:
                        result = GeoPolRisk(
                        productiondata, Y, str(I[1]), AVGPrice
                    )
                        if result is not None:
                            HHI, WTA, Risk, CF = result[0], result[1], result[2], result[3]
                        else:
                            HHI, WTA, Risk, CF = 0, 0, 0, 0
                    else:
                        HHI, WTA, Risk, CF = 0, 0, 0, 0
                      # Final outputs from the GeoPolRisk calculation
                    logging.info(f"""
                    GeoPolRisk calculation completed successfully! The following
                    values are calculated: {HHI}, {WTA}, {Risk}, {CF} for resource {I[0]}
                    , year {I[1]} to region {l} with recyclingrate {recyclingrate} and 
                    scenario {scenario}
                    """)
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
                            OutputList
                        )
                else:
                    try:
                        sqlstatement = f""" SELECT  geopolrisk, hhi, wta, geopol_cf FROM
                        recordData WHERE id = '{DBID}'
                        """
                        row = execute_query(sqlstatement, db_path=db)
                        OutputList.append(str(I[1]), str(resource), str(l),
                                str(recyclingrate), str(scenario),
                                str(row[0][0]), str(row[0][3]), str(row[0][1]), str(row[0][2]))
                    except Exception as e:
                        logging.debug(f"Cannot append into list of records {e}")
                    logging.debug(
                    "No transaction has been made. "
                    "Preexisting data has been inserted in output file."
                )        
    else:
        regions()
        for I in itertools.product(resourcelist, countrylist, yearlist):
            # LOGIC
            totalcounter += 1
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
                        counter += 1
                        TradeData = worldtrade(
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
                        counter += 1
                        TradeData = specifictrade(
                            year=I[2],
                            country=I[1],
                            commodity=I[0],
                        )
                    except Exception as e:
                        logging.debug(f"Error accessing specific trade data {e}")
                        counter -= 1
                        break
                # From the core methods, TradeData is None only when the dataframe is empty
                if TradeData[0] == None or TradeData[0] == 0:
                    emptycounter += 1
                else:
                    pass

                try:
                    AVGPrice = _price[str(I[2])].tolist()[_price.HS.to_list().index(I[0])]
                    X = ProductionData(resource, country)
                    Y = weightedtrade(
                        str(I[2]),
                        TradeData=TradeData,
                        PIData=_wgi,
                        scenario=scenario,
                        recyclingrate=recyclingrate,
                    )
                    if Y is not None and X is not None:
                        result = GeoPolRisk(X, Y, str(I[2]), AVGPrice)
                        if result is not None:
                            HHI, WTA, Risk, CF = result[0], result[1], result[2], result[3]
                        else:
                            HHI, WTA, Risk, CF = 0, 0, 0, 0
                    else:
                        HHI, WTA, Risk, CF = 0, 0, 0, 0
                except Exception as e:
                    logging.debug(f"Error unpacking the production data/weighted trade data/price data {e}")
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
                            OutputList
                        )
            else:
                try:
                    sqlstatement = f""" SELECT  geopolrisk, hhi, wta, geopol_cf FROM
                    recordData WHERE id = '{DBID}'
                    """
                    row = execute_query(sqlstatement, db_path=db)
                    OutputList.append([str(I[1]), str(resource), str(country),
                            str(recyclingrate), str(scenario),
                            str(row[0][0]), str(row[0][3]), str(row[0][1]), str(row[0][2])])
                except Exception as e:
                    logging.debug(f"Cannot append into list of records {e}")
                logging.debug(
                "No transaction has been made. "
                "Preexisting data has been inserted in output file."
            )        

    outputDF = pd.DataFrame(OutputList, columns=outputdf.columns)
    outputDF.to_csv(_outputfile+'/export.csv')  
    endlog(counter, totalcounter, emptycounter)
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
        main(HS, Year, ISO, 0, 0)
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