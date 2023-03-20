

from .__init__ import (
    _reporter,
    execute_query,
    _price,
    exportfile,
    _wgi,
    regionslist,
    logging,
    Filename,
)

_outputfile = exportfile
from .core import *
from .Exceptions.warningsgprs import *
import itertools, sqlite3, pandas as pd, time

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

def gprs_comtrade(
    resourcelist, countrylist, 
    yearlist, recyclingrate, 
    scenario, database="record"
):
    if len(regionslist) > 0:
        pass
    else:
        regions()

    # Counter to calculate the number of requests sent to API.
    # Easier to debug the problem
    counter, totalcounter, emptycounter = 0, 0, 0

    # Iterate for each value in each list
    for I in itertools.product(resourcelist, countrylist, yearlist):
        totalcounter += 1
        # Need to verify if the data preexists to avoid limited API calls
        try:
            resource, country = convertCodes(I[0], I[1], 2)
            verify = sqlverify(resource, country, I[2], recyclingrate, scenario)
        except Exception as e:
            logging.debug(e)
            raise IncompleteProcessFlow

        if verify is None or database == "update":
            # The program has to sleep inorder to avoid conflict in multiple API requests
            time.sleep(5)

            try:
                counter += 1
                TradeData = COMTRADE_API(
                    year=I[2],
                    country=I[1],
                    commodity=I[0],
                )
            except APIError as e:
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
                X = productionQTY(resource, country)
                Y = WTA_calculation(
                    str(I[2]),
                    TradeData=TradeData,
                    PIData=_wgi,
                    scenario=scenario,
                    recyclingrate=recyclingrate,
                )
                HHI, WTA, Risk, CF = GeoPolRisk(X, Y, str(I[2]), AVGPrice)
            except Exception as e:
                logging.debug(e)
                logging.debug("The resource is {}".format(resource))
                logging.debug("The country and year are {} {}".format(country, I[2]))
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
            if database == "record":
                recorddata(
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
            elif database == "update":
                updatedata(
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
                )
        else:
            logging.debug(
                "No transaction has been made. "
                "Preexisting data has been inserted in output file."
            )

    outputDF = pd.DataFrame(outputList, columns=_columns)
    outputDF.to_csv(_outputfile + "/export.csv")
    endlog(counter, totalcounter, emptycounter)


# Function for regional level assesment. Must define the regions in a dictionary
# using a function from the core module.
# The assessment is similar to that of gprs_comtrade


def gprs_regional(
    resourcelist, countrylist, yearlist, recyclingrate, scenario, database="record"
):
    # Function to calculate the GeoPolitical related supply risk potential using the GeoPolRisk method for
    # a list of countries including group of countries or newly defined regions.
    # Correct functioning of this function is dependent on the function 'regions' from core module.
    # regions function allows to declare a new region or group of countries as a dictionary.

    newregionlist = []
    # Instantiate counters for logging
    counter, totalcounter, emptycounter = 0, 0, 0
    # Compare if the region already exists withing the library.
    newregion = [
        i
        for i, x in enumerate(countrylist)
        if str(x) not in _reporter.Country.to_list()
        and str(x) not in _reporter["ISO"].astype(str).tolist()
    ]
    # Extract new regions from the provided countrylist parameter (argument).
    for i in newregion:
        newregionlist.append(countrylist[i])
        del countrylist[i]

    # Calculate the values for the new region(s)
    for l in newregionlist:
        # New regions can be defined as ISO nomenclature or ISO numeric. The values must be converted to numeric.
        Xcountrylist = regionslist[l]
        _ignore, Xcountrylist = (
            convertCodes("Cobalt", Xcountrylist)
            if str(Xcountrylist[0]) not in _reporter["ISO"].astype(str).tolist()
            else None,
            Xcountrylist,
        )

        # Iterate the resources, year for COMTRADE query
        for I in itertools.product(resourcelist, yearlist):
            # LOGIC
            """
            A group of countries such as G7, G8 or region such as middle east, ASEAN are declared in the regions function.
            The name of the group or region is provided as the key and the values as a list of countries in the group or region.
            ex: The G7 group can be presented as {"G7" : ["Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "USA"]} or
            ISO numeric can provided instead of the names.

            The logic behind the code is to iterate the list of countries in the group/region and fetch its individual trade data.
            The trade data is aggregated (summed) which is then processed for further calculation.
            """

            # New variables to aggregate trade data from COMTRADE API
            newcodelist, newcountrylist, newquantitylist = (
                [],
                [],
                [],
            )  # TradeData (from core module) fetchs the ISO country code, country names and trade quantity in KG from COMTRADE
            newtradelist = [
                newcodelist,
                newcountrylist,
                newquantitylist,
            ]  # The newtradelist appends the list and aggregates them
            TotalDomesticProduction, TDP = 0, []  # Variable to fetch production data
            try:
                resource, _ignore = convertCodes(I[0], 124)
                verify = sqlverify(resource, l, I[1], recyclingrate, scenario)
            except Exception as e:
                logging.debug(e)
                logging.debug("SQL Verification failed!")
                raise IncompleteProcessFlow
            if verify is None or database == "update":
                for k in Xcountrylist:
                    # Counters
                    counter += 1
                    totalcounter += 1
                    try:
                        # Code to fetch from COMTRADE API
                        resource, country = convertCodes(I[0], k)
                        TradeData = COMTRADE_API(
                            classification="HS",
                            period=I[1],
                            partner="all",
                            reporter=k,
                            HSCode=I[0],
                            TradeFlow="1",
                            recyclingrate=recyclingrate,
                            scenario=scenario,
                        )
                    except Exception as e:
                        logging.debug(e)
                        logging.debug(
                            f"""Failed COMTRADE attempt!: resource - {resource}
                                      country - {country}, year - {I[1]}"""
                        )

                    # counter
                    if TradeData[0] is None or len(TradeData[0]) == 0:
                        emptycounter += 1
                        logging.debug(
                            f"Trade of {resource} to {country} returned None for {I[1]}"
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
                    X = productionQTY(resource, country)
                    index = X[2].index(I[1])
                    TotalDomesticProduction += X[1][index]

                # Calculation of the components of the GeoPolRisk method
                TDP = [0] * len(X[1])
                TDP[X[2].index(I[1])] = TotalDomesticProduction
                AVGPrice = _price[str(I[1])].tolist()[_price.HS.to_list().index(I[0])]
                Y = WTA_calculation(
                    str(I[1]),
                    TradeData=newtradelist,
                    PIData=_wgi,
                    scenario=scenario,
                    recyclingrate=recyclingrate,
                )

                HHI, WTA, Risk, CF = GeoPolRisk(
                    [X[0], TDP, X[2]], Y, str(I[1]), AVGPrice
                )  # Final outputs from the GeoPolRisk calculation
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
                if database == "record":
                    recorddata(
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
                elif database == "update":
                    updatedata(
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
                    )

    # The remaining countries in the provided parameter that does not require aggregation is calculated using comtrade aggregat
    gprs_comtrade(
        resourcelist, countrylist, yearlist, recyclingrate, scenario, database="record"
    )


# Organizational level assessment require declaring the regions if necessary and a
# path to the trade document as specified.
def gprs_organization(
    resourcelist, countrylist, yearlist, recyclingrate, scenario, sheetname
):
    newregionlist = []
    newregion = [
        i
        for i, x in enumerate(countrylist)
        if str(x) not in _reporter.Country.to_list()
        and str(x) not in _reporter["ISO"].astype(str).tolist()
    ]
    for i in newregion:
        newregionlist.append(countrylist[i])
        del countrylist[i]
    for l in newregionlist:
        countrylist = regionslist[l]
        _ignore, countrylist = convertCodes([], countrylist, 1)
        for I in itertools.product(resourcelist, yearlist):
            TotalDomesticProduction = 0
            TradeData = InputTrade(sheetname)
            for k in countrylist:
                resource, country = convertCodes(I[0], k, 2)
                try:
                    X = productionQTY(resource, country)
                    index = X[2].index(I[1])
                    TotalDomesticProduction += X[1][index]
                except Exception as e:
                    logging.debug(e)
            AVGPrice = _price[str(I[1])].tolist()[_price.HS.to_list().index(i)]

            Y = WTA_calculation(str(I[1]), TradeData=TradeData)
            HHI, WTA, Risk, CF = GeoPolRisk(
                [X[0], TotalDomesticProduction, X[2]], Y, str(I[1]), AVGPrice
            )
            outputList.append(
                [str(I[1]), resource, l, recyclingrate, scenario, Risk, CF, HHI, WTA]
            )

    outputDF = pd.DataFrame(outputList, columns=_columns)
    outputDF.to_csv(_outputfile + "/export.csv")
    outputDF.to_csv(_outputfile + "/export.csv")


# Function to update the characterization factors. Run this function if there are missing
# values for some select resources. The COMTRADE API is broken, and it sometimes results in
# a null return which is stored in the database as 0. This function retries fetching the values.


def update_cf():
    # Fetch Missing Data
    sqlstatement = (
        "SELECT resource_hscode, year, iso, geopol_cf FROM recordData WHERE "
        " wta = '0';"
    )
    row = execute_query(sqlstatement)
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
        gprs_comtrade(HS, ISO, Year, 0, 0, database="update")
    except Exception as e:
        logging.debug(e)


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
            norow = execute_query(sqlstatement)
            logging.debug(f"Database update sucessfully! for {n} for {Year[i]}")


"""
End of script logging and exporting database to specified format. End log 
method requires extractdata method to be precalled to work. 
"""


# Tracking the comtrade attempts for debugging.
def endlog(counter=0, totalcounter=0, emptycounter=0):
    logging.debug("Number of successfull COMTRADE API attempts {}".format(counter))
    logging.debug("Number of total attempts {}".format(totalcounter))
    logging.debug("Number of empty dataframes {}".format(emptycounter))


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
            _outputfile + "/datarecords.db",
            isolation_level=None,
            detect_types=sqlite3.PARSE_COLNAMES,
        )
        db_df = pd.read_sql_query("SELECT * FROM recorddata", conn)
        if CFType == "csv":
            db_df.to_csv(_outputfile + "/database.csv", index=False)
        elif CFType == "excel":
            db_df.to_excel(_outputfile + "/database.xlsx", index=False)
        elif CFType == "json":
            db_df.to_json(_outputfile + "/database.json", orient=orient, index=False)
    except Exception as e:
        logging.debug(e)
