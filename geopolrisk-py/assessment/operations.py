# Copyright 2020-2021 by Anish Koyamparambath and University of Bordeaux. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Anish Koyamparambath (AK) or 
# University of Bordeaux (UBx) will not be used in advertising or publicity pertaining 
# to distribution of the software without specific, written prior permission.
# BOTH AK AND UBx DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# BOTH AK AND UBx BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


from .__init__ import (
    _reporter,
    SQL,
    _price,
    _outputfile,
    _wgi,
    regionslist,
    logging,
    Filename)

from .core import (
    regions,
    COMTRADE_API,
    InputTrade,
    WTA_calculation,
    productionQTY,
    GeoPolRisk,
    )
from .Exceptions.warningsgprs import *
import itertools, sqlite3, pandas as pd, time

_columns = ["Year", "Resource", "Country","Recycling Rate",
            "Recycling Scenario", "Risk","GeoPolRisk Characterization Factor",
            "HHI", "Weighted Trade AVerage"]
outputList = []



# The function converts resource names and country names to the HS commodity codes
# and country ISO codes.

def convertCodes(resource, country, direction):
    resourceCX, countryCX = None, None 
    
    if isinstance(resource,  list):
        listofresource = []
        for i in resource:
            if isinstance(i, str) and direction == 1:
                listofresource.append(_price.iloc[_price.id.to_list().index(i),26])
            elif isinstance(i, int) and direction == 2:
                listofresource.append(_price.iloc[_price.hs.to_list().index(i),25])
        resourceCX = listofresource
    elif isinstance(resource, int) and direction == 2:
        resourceCX = _price.iloc[_price.hs.to_list().index(resource),25]
    elif isinstance(resource, str) and direction == 1:
        resourceCX = _price.iloc[_price.id.to_list().index(resource),26]
    else:
        logging.debug(f"Unknown input type or direction. Input resource = {resource}; direction = {direction}.")
        raise InputError
    
    
    if isinstance(country,  list):
        listofcountries = []
        for i in country:
            if isinstance(i, str) and direction == 1:
                listofcountries.append(_reporter.ISO.to_list()[_reporter.Country.to_list().index(i)])
            elif isinstance(i, int) and direction == 2:
                listofcountries.append(_reporter.Country.to_list()[_reporter.ISO.astype(str).to_list().index(str(i))])
        countryCX = listofcountries
    elif isinstance(resource, int) and direction == 2:
        countryCX = _reporter.Country.to_list()[_reporter.ISO.astype(str).to_list().index(str(country))]
    elif isinstance(resource, str) and direction == 1:
        countryCX = _reporter.ISO.to_list()[_reporter.Country.to_list().index(country)]
    else:
        logging.debug(f"Unknown input type or direction. Input country = {country}; direction = {direction}.")
        raise InputError
    
    if resourceCX is None or countryCX is None:
        logging.debug("Something went wrong in the convertcodes function!")
        raise IncompleteProcessFlow
    else:
        return resourceCX, countryCX
    



# Verify if the calculation is already stored in the database to avoid recalculation
def sqlverify(*args):
    resource, country, year, recyclingrate, scenario = args[0], args[1], args[2], args[3], args[4] 
    sqlstatement = "SELECT geopolrisk, hhi, wta, geopol_cf FROM recordData WHERE country = '"+country+"' AND resource= '"+resource+"' AND year = '"+str(year)+"' AND recycling_rate = '"+str(recyclingrate)+"' AND scenario = '"+str(scenario)+"';"
    try:
        row = SQL(sqlstatement, SQL = 'select')
    except InputError:
        logging.debug(sqlstatement)
    if not row:
        return None
    else:
        outputList.append([str(year), resource , country ,recyclingrate, scenario, row[0][0],row[0][3],row[0][1],row[0][2]])
        return True

# Store the calculation into a database
# Please note that database is not included in the library, this is automatically created
# in the documents directory of the operating system
def recorddata(*args):
    resource, country, year, recyclingrate, scenario, GPRS, CF, HHI, WTA, HSCODE, ISO, Log= args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7],args[8], args[9], args[10], args[11] 
    sqlstatement = "INSERT INTO recordData (country, resource, year, recycling_rate, scenario, geopolrisk, hhi, wta, geopol_cf, resource_hscode, iso, log_ref) VALUES ('"\
                 ""+country+"','"+resource+"','"+str(year)+""\
                 "','"+str(recyclingrate)+"','"+str(scenario)+"','"\
                 ""+str(GPRS)+"','"+str(HHI)+"','"+str(WTA)+""\
                 "','"+str(CF)+"','"+str(HSCODE)+"','"+str(ISO)+"',"\
                 "'"+str(Log)+"');"
    try:
        row = SQL(sqlstatement, SQL = 'execute')
        return True
    except Exception as e:
        logging.debug(e)


# Updates the database using new values.
# This function doesnt override the calculaiton
def updatedata(*args):
    #Verify
    resource, country, year, recyclingrate, scenario = args[0], args[1], args[2], args[3], args[4]
    GPRS, CF, HHI, WTA, Log = args[5], args[6], args[7], args[8], args[9]
    sqlstatement = "SELECT geopolrisk, hhi, wta, geopol_cf from "\
                    "recordData WHERE country = '"+country+"' AND resource= '"+resource+"' AND year = '"+str(year)+"' AND recycling_rate = '"+str(recyclingrate)+"' AND scenario = '"+str(scenario)+"';"
    row = SQL(sqlstatement)
    dataframe = pd.DataFrame(row, columns = ["geopolrisk", "hhi", "wta", "geopol_cf"])
    if dataframe.shape[0]>2:
        logging.debug("Multiple data records found!")
        raise DataRecordError
        return None
    elif dataframe.shape[0]>2:
        logging.debug("No data records found!")
        raise DataRecordError
        return None
    else:
        if int(dataframe.iloc[0]['wta']) == int(WTA):
            logging.debug("NO change in trade data detected! No SQL executed.")
            return None
        else:
            sqlstatement = "UPDATE recordData SET hhi= '"+str(HHI)+"', wta ='"+str(WTA)+"', geopolrisk='"+str(GPRS)+"', geopol_cf= '"+str(CF)+"', log_ref='"+str(Log)+"' WHERE country = '"+country+"' AND resource= '"+resource+"' AND year = '"+str(year)+"' AND recycling_rate = '"+str(recyclingrate)+"' AND scenario = '"+str(scenario)+"';"
            norow = SQL(sqlstatement, SQL='execute')
            logging.debug("Database update sucessfully!")



# Function to calculate the geopolitical supply risk and CFs for the midpoint indicator
# A single point calculation function. It takes in the list of resources (HS code commodities),
# list of countries (ISO 3 digit code) and list of years. The recycling rate and scenario are provided as
# float and integers. 
# The argument 'record' for database overrides the capacity to update the database. That means if 
# a calculation exists, a repeated calculation is not done. 'update' as an argument updates the database
# instead of recording.
def gprs_comtrade(resourcelist, countrylist, yearlist, recyclingrate, scenario, database="record"):
    if len(regionslist) > 0:
        pass
    else:
        regions()
    
    #Counter to calculate the number of requests sent to API. 
    #Easier to debug the problem
    counter, totalcounter, emptycounter = 0, 0, 0
    
    #Iterate for each value in each list
    for I in itertools.product(resourcelist, countrylist, yearlist):
        totalcounter += 1
        #Need to verify if the data preexists to avoid limited API calls
        try:
            resource, country = convertCodes(I[0], I[1], 2)
            verify = sqlverify(resource, country, I[2], recyclingrate, scenario)
        except Exception as e:
            logging.debug(e)    
            raise IncompleteProcessFlow
            
            
        if verify is None or database == "update":
            #The program has to sleep inorder to avoid conflict in multiple API requests
            time.sleep(5)
            try:
                counter  += 1
                TradeData = COMTRADE_API(classification = "HS",
                period = I[2],
                partner = "all",
                reporter = I[1],
                HSCode = I[0],
                TradeFlow = "1",
                recyclingrate = recyclingrate,
                scenario = scenario)
            except APIError as e:
                logging.debug(e)
                counter -= 1
                break
            
            #From the core methods, TradeData is None only when the dataframe is empty
            if TradeData[0] == None or TradeData[0] == 0:
                emptycounter += 1
            else:
                pass
                
            try:
                AVGPrice = _price[str(I[2])].tolist()[_price.hs.to_list().index(I[0])]
                X = productionQTY(resource, country)
                Y = WTA_calculation(str(I[2]), TradeData = TradeData, PIData = _wgi, scenario = scenario, recyclingrate = recyclingrate)
                HHI, WTA, Risk, CF = GeoPolRisk(X, Y, str(I[2]), AVGPrice)
            except Exception as e:
                logging.debug(e)
                logging.debug("The resource is {}".format(resource))
                logging.debug("The country and year are {} {}".format(country, I[2]))
                continue
                
            outputList.append([str(I[2]), resource, country ,recyclingrate, scenario, Risk, CF, HHI, WTA])
            if database == "record":
                recorddata(resource, country, I[2], recyclingrate, scenario, Risk, CF, HHI, WTA, I[0], I[1], Filename)
            elif database == "update":
                updatedata(resource, country, I[2], recyclingrate, scenario, Risk, CF, HHI, WTA, Filename)
        else:
            logging.debug("No transaction has been made. "
                          "Preexisting data has been inserted in output file.")
    
    outputDF = pd.DataFrame(outputList, columns=_columns)
    outputDF.to_csv(_outputfile+'/export.csv')        
    endlog(counter, totalcounter, emptycounter)


# Function for regional level assesment. Must define the regions in a dictionary 
# using a function from the core module.
# The assessment is similar to that of gprs_comtrade


def gprs_regional(resourcelist, countrylist, yearlist, recyclingrate, scenario, database="record"):
    # Function to calculate the GeoPolitical related supply risk potential using the GeoPolRisk method for 
    # a list of countries including group of countries or newly defined regions.
    # Correct functioning of this function is dependent on the function 'regions' from core module.
    # regions function allows to declare a new region or group of countries as a dictionary.
    
    
    
    newregionlist = []
    # Instantiate counters for logging
    counter, totalcounter, emptycounter = 0, 0, 0
    # Compare if the region already exists withing the library.
    newregion = [i for i , x  in enumerate(countrylist) if str(x) not
                   in _reporter.Country.to_list() and str(x) not 
                   in _reporter["ISO"].astype(str).tolist()]
    # Extract new regions from the provided countrylist parameter (argument).
    for i in newregion:
        newregionlist.append(countrylist[i])
        del countrylist[i]
    
    # Calculate the values for the new region(s)
    for l in newregionlist:
        # New regions can be defined as ISO nomenclature or ISO numeric. The values must be converted to numeric.
        Xcountrylist = regionslist[l]
        _ignore, Xcountrylist = convertCodes("Cobalt", Xcountrylist, 1) if str(Xcountrylist[0]) not in _reporter["ISO"].astype(str).tolist() else None,Xcountrylist
        
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
            newcodelist, newcountrylist, newquantitylist = [], [], [] # TradeData (from core module) fetchs the ISO country code, country names and trade quantity in KG from COMTRADE
            newtradelist = [newcodelist, newcountrylist, newquantitylist] # The newtradelist appends the list and aggregates them
            TotalDomesticProduction, TDP = 0, [] # Variable to fetch production data
            try:
                resource, _ignore = convertCodes(I[0], 124, 2)
                verify = sqlverify(resource, l, I[1], recyclingrate, scenario)
            except Exception as e:
                    logging.debug(e)    
                    logging.debug("SQL Verification failed!")
                    raise IncompleteProcessFlow
            if verify is None or database == "update":
                for k in Xcountrylist:
                    #Counters
                    counter  += 1
                    totalcounter += 1
                    try:
                        #Code to fetch from COMTRADE API
                        resource, country = convertCodes(I[0], k, 2)
                        TradeData = COMTRADE_API(classification = "HS",
                        period = I[1],
                        partner = "all",
                        reporter = k,
                        HSCode = I[0],
                        TradeFlow = "1",
                        recyclingrate = recyclingrate,
                        scenario = scenario)
                    except Exception as e:
                        logging.debug(e)
                        logging.debug(f"""Failed COMTRADE attempt!: resource - {resource}
                                      country - {country}, year - {I[1]}""")
                    
                    #counter
                    if TradeData[0] is None or len(TradeData[0]) == 0:
                        emptycounter += 1
                        logging.debug(f"Trade of {resource} to {country} returned None for {I[1]}")
                        newtradelist = [[0], [0], [0]]
                    else:
                        #code to aggregate the data
                        for ind, n in enumerate(TradeData[0]):
                            if n not in newcodelist:
                                newcodelist.append(n)
                                newquantitylist.append(TradeData[2][ind])
                                newcountrylist.append(TradeData[1][ind])
                            else:
                                index = newcodelist.index(n)
                                newquantitylist[index] = newquantitylist[index] + TradeData[2][ind]      
                    X = productionQTY(resource, country)
                    index = X[2].index(I[1])
                    TotalDomesticProduction += X[1][index]
                 
                # Calculation of the components of the GeoPolRisk method
                TDP = [0]*len(X[1])
                TDP[X[2].index(I[1])] = TotalDomesticProduction
                AVGPrice = _price[str(I[1])].tolist()[_price.hs.to_list().index(I[0])]
                Y = WTA_calculation(str(I[1]), TradeData = newtradelist, PIData = _wgi, scenario = scenario, recyclingrate = recyclingrate )
                
                HHI, WTA, Risk, CF = GeoPolRisk([X[0], TDP, X[2]], Y, str(I[1]), AVGPrice)# Final outputs from the GeoPolRisk calculation
                outputList.append([str(I[1]), resource, l ,recyclingrate, scenario, Risk, CF, HHI, WTA])
                
                #Record or update data
                if database == "record":
                    recorddata(resource, l, I[1], recyclingrate, scenario, Risk, CF, HHI, WTA, I[0], l, Filename)
                elif database == "update":
                    updatedata(resource, l, I[1], recyclingrate, scenario, Risk, CF, HHI, WTA, Filename)
    
    #The remaining countries in the provided parameter that does not require aggregation is calculated using comtrade aggregat
    gprs_comtrade(resourcelist, countrylist, yearlist, recyclingrate, scenario, database="record")
    
    

# Organizational level assessment require declaring the regions if necessary and a
# path to the trade document as specified.
def gprs_organization(resourcelist, countrylist, yearlist, recyclingrate, scenario, sheetname):
    newregionlist = []
    newregion = [i for i , x  in enumerate(countrylist) if str(x) not
                   in _reporter.Country.to_list() and str(x) not 
                   in _reporter["ISO"].astype(str).tolist()]
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
            AVGPrice = _price[str(I[1])].tolist()[_price.hs.to_list().index(i)]
            
            Y = WTA_calculation(str(I[1]), TradeData = TradeData)
            HHI, WTA, Risk, CF = GeoPolRisk([X[0], TotalDomesticProduction, X[2]], Y, str(I[1]), AVGPrice)
            outputList.append([str(I[1]), resource, l ,recyclingrate, scenario, Risk, CF, HHI, WTA])
    
    outputDF = pd.DataFrame(outputList, columns=_columns)
    outputDF.to_csv(_outputfile+'/export.csv')
    outputDF.to_csv(_outputfile+'/export.csv')


# Function to update the characterization factors. Run this function if there are missing
# values for some select resources. The COMTRADE API is broken, and it sometimes results in 
# a null return which is stored in the database as 0. This function retries fetching the values.

def update_cf():
    #Fetch Missing Data
    sqlstatement = "SELECT resource_hscode, year, iso, geopol_cf FROM recordData WHERE "\
                    " wta = '0';"
    row = SQL(sqlstatement)
    df = pd.DataFrame(row, columns = ['HS Code', 'Year', 'Country Alpha', 'Characterziation Factors'])
    logging.debug("Update of database! The shape of df is "+str(df.shape[0]))
    if df.shape[0] > 0:
        Year = [int(i) for i in df.Year.to_list()]
        ISO = [int(i) for i in df['Country Alpha'].tolist()]
        HS = [int(i) for i in df['HS Code'].tolist()]
    else:
        logging.debug("No updates required!")
        return None
    try:
        gprs_comtrade(HS,ISO,Year,0,0, database="update")
    except Exception as e:
        logging.debug(e)
        
# Run this function if there is an update in the missing price data in the average yearly price json.
def updateprice():
    logging.info("Updating the characterization prices | price")
    sqlstatement = "SELECT resource_hscode, year, iso, geopolrisk FROM recordData WHERE "\
                    " geopol_cf = 'NA' AND recycling_rate ='0' AND scenario ='0';"
    row = SQL(sqlstatement)
    df = pd.DataFrame(row, columns = ['HS Code', 'Year', 'Country Alpha', 'GeoPolRisk'])
    logging.debug("Update of database! The shape of df is "+str(df.shape[0]))
    if df.shape[0] > 0:
        Year = [int(i) for i in df.Year.to_list()]
        ISO = [int(i) for i in df['Country Alpha'].tolist()]
        HS = [int(i) for i in df['HS Code'].tolist()]
        GPRS = [float(i) for i in df['GeoPolRisk'].tolist()]
    else:
        logging.debug("No updates required!")
        return None
    for i, n in enumerate(HS):
        AVGPrice = _price[str(Year[i])].tolist()[_price.hs.to_list().index(n)]             
        if isinstance(AVGPrice, (int, float)):
            index = ISO.index(ISO[i])
            CF = float(GPRS[index])*AVGPrice
            sqlstatement = "UPDATE recordData SET geopol_cf= '"+str(CF)+"', log_ref='"+str(Filename)+"' WHERE iso = '"+str(ISO[i])+"' AND resource_hscode= '"+str(n)+"' AND year = '"+str(Year[i])+"' AND recycling_rate = '0' AND scenario = '0';"
            norow = SQL(sqlstatement, SQL='execute')
            logging.debug(f"Database update sucessfully! for {n} for {Year[i]}")

"""
End of script logging and exporting database to specified format. End log 
method requires extractdata method to be precalled to work. 
"""


# Tracking the comtrade attempts for debugging.
def endlog( counter=0, totalcounter=0, emptycounter=0):
    logging.debug("Number of successfull COMTRADE API attempts {}".format(counter))
    logging.debug("Number of total attempts {}".format(totalcounter))
    logging.debug("Number of empty dataframes {}".format(emptycounter))
    

    
"""Convert entire database to required format
**CHARACTERIZATION FACTORS
Refer to python json documentation for more information on types of
orientation required for the output.
"""

# Extract CFs 
def generateCF(exportType='csv', orient=""):
    exportF = ['csv', 'excel', 'json']
    if exportType in exportF:
        logging.debug("Exporting database in the format {}".format(exportType))
        CFType=exportType
    else:
        logging.debug("Exporting format not supported {}. "
                      "Using default format [csv]".format(exportType))
        CFType="csv"
    try:
        conn = sqlite3.connect(_outputfile+"/datarecords.db", isolation_level=None,
                   detect_types=sqlite3.PARSE_COLNAMES)
        db_df = pd.read_sql_query("SELECT * FROM recorddata", conn)
        if CFType == "csv":
            db_df.to_csv(_outputfile+'/database.csv', index=False)
        elif CFType == "excel":
            db_df.to_excel(_outputfile+'/database.xlsx', index=False)
        elif CFType == "json":
             db_df.to_json(_outputfile+'/database.json', orient = orient, index=False)
    except Exception as e:
        logging.debug(e)
    

