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


#Imports
import pandas as pd, sys, getpass, sqlite3, logging
from geopolrisk.__init__ import APIError, _commodity, _reporter, _resource, _logfile, _outputfile, _libfile
from difflib import get_close_matches
from datetime import datetime
from geopolrisk.gprs import comtrade


#Fetch username for the purpose of logging.
username = getpass.getuser()

class operations(comtrade):
    """Do not modify the path for the logs folder unless you specifically need
    it elsewhere. Modify the alert level depending on requirements for debugging. 
    """
    #Method 0
    def __init__(self):
        self.commodity = _commodity
        self.reporter = _reporter
        self.resource = _resource
        Filename = _logfile+'//function({:%Y-%m-%d(%H-%M-%S)}).log'.format(datetime.now())
        self.module = False
        self.notCOMTRADE = False
        self.logging = logging
        self.logging.basicConfig(
            level = logging.DEBUG,
            format = '%(asctime)s | %(levelname)s | %(threadName)-10s | %(filename)s:%(lineno)s - %(funcName)20s() | %(message)s',
            filename = Filename,
            filemode = 'w'
            )
        _columns = ["Year", "Resource", "Country","Recycling Rate","Recycling Scenario", "Risk","GeoPolRisk Characterization Factor", "HHI", "Weighted Trade AVerage"]
        self.outputDF = pd.DataFrame(columns = _columns)
        self.outputDFType = 'csv'
        self.counter, self.totcounter, self.emptycounter = 0 ,0 , 0
        self.logging.debug('Username: {}'.format(username))
        self.totalreduce = 0
        self.recordspath = _libfile+'/datarecords.db'
        
    """The program is equipped with a predefined database for production of a 
    raw materia. Change the path of the respective databases to customize the 
    calculation.
    """    
    #Method 2
    def setpath(self,
             prod_path = _libfile+'/production.xlsx',
             trade_path = None,
             wgi_path = _libfile+'/wgidataset.xlsx',
             ):
        self.prod_path = prod_path
        self.trade_path = trade_path
        self.wgi_path = wgi_path
        self.regions()
        #Confirmation of loading this function
        self.module = True
        if self.trade_path != None:
            self.notCOMTRADE = True

    """User can modify this section along with another section in the calculation
    if more trade blocs, regions or group of countries is necessary for the study
    """
    """It is important to note that the region EU is existing in the countries
    database which shall be used to call the COMTRADE API. Unfortunately, other 
    trade blocs or regions are unavailable and has to be called separately tallied
    and accounted. In version 1, such feature is not available in the code. If users
    modify the regions, ensure the countries and # section is modified accordingly. 
    """
            
    #Method 3
    def regions(self, **kwargs):
        self.EU = ['Austria', 'Belgium', 'Belgium-Luxembourg', 'Bulgaria',
                   'Croatia', 'Czechia', 'Czechoslovakia', 'Denmark', 
                   'Estonia','Finland', 'France', 'Fmr Dem. Rep. of Germany',
                   'Fmr Fed. Rep. of Germany', 'Germany', 'Greece', 'Hungary',
                   'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 
                   'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 
                   'Slovakia', 'Slovenia', 'Spain', 'Sweden']
        region_list = {}
        countries = _reporter.Country.to_list()
        ISO = _reporter["ISO"].astype(str).tolist()
        for key, value in kwargs.items():
            print(countries)
            Print_Error = [x for x in value if str(x) not in countries and str(x) not in ISO]
            if len(Print_Error) != 0:
                print("""Error in creating a region! Following list of countries not found in the ISO list {}. Please conform with the ISO list or use 3 digit ISO country codes.""".format(Print_Error))
            else:
                region_list[key] = value
        self.regionslist = region_list

    """
    Method 1, is the first method that will be called if exucting the main function 
    i.e Method 0 of API class. It ensures if the other methods are loaded before.
    """
    #Method 1    
    def run(self):
        self.createTable()
        if self.module != True:
            self.setpath()

    """
    A simple guided step by step method for new users. This method can be called 
    to any console based application if needed.
    """
    #Method 4   
    def simplerun(self):
        #4.1 Call Method 1
        self.run()
        
        def matchwords(word, List):
            word = word.lower()
            List = [x.lower() for x in List]
            if word in List:
                index = List.index(word)
                return index
            else:
                return -1
            
            
        
        """
        List of available production information of metals which is later cross
        verified for confirmation with the hs code. Also, the production information
        is organized using the common name of the raw material which can later be altered
        when automatic download of data is created.
        """
        #4.2 Extracting data from linking database
        Metals = self.resource.id.tolist()
        HS = self.resource.hs.tolist()
        
        """
        Connect country to country codes. These codes and files are only necessary
        for guided run.
        """
        #4.3 Extracting data from ISO country codes database
        Country = self.reporter.Country.tolist()
        
        
        """
        Following section gets the input of the resource/raw material from the user.
        Keeping in mind the possibility of error from the user, get close matches 
        library is used and reverified by the user. If found cumbersome an additional 
        code to verify letter to letter can be created. The input is fed as key to 
        fetch the resource hscode to be used in the API. Sections 4.5 also follows
        the same pattern.
        """
        #4.4 Input information on raw material
        _exit = True
        while _exit:
            print('Enter the name the resource whose supply risk you want to assess or type exit to exit')
            metal = input('Resource Name : ')
            Metalcloselist = get_close_matches(metal, Metals)
            if matchwords(metal, Metals) > -1:
                resource = Metals[matchwords(metal, Metals)]
                print("Selected resource is {} \n".format(resource))
                _exit = False
            elif len(Metalcloselist) > 1:
                print("The following metals are found close to your query ")
                print(Metalcloselist)
                try:
                    index = int(input("Enter the selected resources as 1, 2 etc., :" ))
                    resource = Metalcloselist[index - 1]
                    print("Selected resource is {} \n".format(resource))
                    _exit = False
                except ValueError:
                    print("Please enter proper value!")
            elif len(Metalcloselist) == 0 and metal.lower() != "exit":
                print("The entered resource is not found")
            elif len(Metalcloselist) == 1 and metal != Metalcloselist[0]:
                print("The entered resource is not found")
            elif metal.lower() == "exit":
                sys.exit(1)
            else:
                resource = Metalcloselist[0]
                print("Selected resource is {} \n".format(resource))
                _exit = False
                
        """
        self.resource countains data that is formated to general audience. i.e
        a description of a hs code is more detailed and not usually known to
        every user. Hence it is concised to the detail of the raw material name.
        However, for the assessment, neither the description nor consice name
        can be used and hence the following code extracts the hscode of the 
        raw material.
        """
        metal = resource
        HSCode = HS[Metals.index(resource)]
        
        #4.5 Input information on country/region
        _exit = True
        while _exit:
            print('Enter the name the country whose supply risk you want to assess or type exit to exit')
            Ctry = input('Country Name : ')
            countrycloselist = get_close_matches(Ctry, Country)
            if matchwords(Ctry, Country) > -1:
                country = Country[matchwords(Ctry, Country)]
                print("Selected country is {} \n".format(country))
                _exit = False
            elif len(countrycloselist) > 1:
                print("The following countries are found close to your query ")
                print(countrycloselist)
                try:
                    index = int(input("Enter the selected country as 1, 2 etc., :" ))
                    country = countrycloselist[index-1]
                    print("Selected country is {} \n".format(country))
                    _exit = False
                except ValueError:
                    print("Please enter a proper value!")
            elif len(countrycloselist) == 0 and metal.lower() != "exit":
                print("The entered Country not found")
            elif metal.lower() == "exit":
                raise APIError
            else:
                country = countrycloselist[0]
                print("Selected country is {} \n".format(country))
                _exit = False
                
        """
        Similar to hscode data, the assessment requires the iso digit code of
        the country/region in question.
        """
        reporter = self.reporter.iloc[Country.index(country),0]
        
        
        _exit = True
        while _exit:
            period = input("Enter the year of assessment :")
            try:
                period = int(period)
                _exit = False
            except Exception as e:
                self.logging.debug(e)

        _exit = True
        while _exit:
            print("Enter the rate of domestic recycling input of the raw material (in fractions) or type exit to exit")
            recyclingrate = input("Enter the recycling input rate: ")
            try:
                if float(recyclingrate) in range(0,101):
                    recyclingrate = float(recyclingrate)
                    _exit = False
                elif recyclingrate.lower() == 'exit':
                    raise APIError
            except Exception as e:
                print("Provide correct inputs! Try again")
                self.logging.debug(e)
                
        
        print("Select 0 for assuming a best case scenario where the imports from a riskier country is reduced")
        print("Select 1 for assuming a worst case scenario where the imports from a stable country is reduced")
        scenario = input("Select 1 or 0: ")
        
        _exit=True
        while _exit:
            try:
                if int(scenario) in [0, 1]:
                    scenario = int(scenario)
                    _exit = False
            except Exception as e:
                print("Provide correct inputs! Try again")
                self.logging.debug(e)

        
        #4.6 Calculating GeoPolRisk, calling method from api module
        print("Calculating the GeoPolRisk of "+str(resource)+" for "+
        str(country)+" over the period "+str(period))
        
        """
        Raw material name as defined in the hs file is important to reassure the user
        of which kind of assessment they are following. The following code has no other 
        purpose.
        """
        #4.7 Extracting information of hs files
        try:
            hs_element = self.commodity.iloc[self.commodity.HSCODE.to_list().index(HSCode),2]
        except Exception as e:
            self.logging.debug(e)
            raise APIError
        print("Info: The HS code used for the analysis is "+str(hs_element))
        
        #4.8 API CALL
        self.TotalCalculation(period = int(period), 
                              reporter = int(reporter), 
                              HSCode = int(HSCode),
                              recyclingrate = recyclingrate,
                              scenario = scenario)
        
        print("The GeoPolRisk Value for "+metal+" during "+str(period)+" for "+country+" is "+str(round(self.GPRS,3)))
        print("The Geopolitical supply risk potential characterization factor calculated is {} $/metric tonne".format(str(round(self.GPSRP,3))))
        self.endlog()


    

    #5 Create table
    """
    Create a database file incase the preexisting database doesnt exist.
    """
    def createTable(self):
        #5.1 Initial run to create a database if not exists
        try:
            sqlstatement = """CREATE TABLE "recordData" (
            	"id"	INTEGER,
            	"country"	TEXT,
            	"resource"	TEXT,
            	"year"	INTEGER,
            	"recycling_rate"	REAL,
            	"scenario"	REAL,
            	"geopolrisk"	REAL,
            	"hhi"	REAL,
            	"wta"	REAL,
            	"geopol_cf"	REAL,
            	"resource_hscode"	REAL,
            	"iso"	TEXT,
            	PRIMARY KEY("id")
            );""" 
            try:
                connect = sqlite3.connect(self.recordspath)
                cursor = connect.cursor()
            except:
                self.logging.debug('Database not found')
            cursor.execute(sqlstatement)
            connect.commit()
            connect.close()
        except Exception as e:
            self.logging.debug(e)

    
    #Method 6.1 SQL SELECT Method
    """
    SQL select method. This program is used
    only to pull records (ONLY SELECT STATEMENT)
    """
    def select(self, sqlstatement):
        try:
            connect = sqlite3.connect(self.recordspath)
            cursor = connect.cursor()
            cursor.execute(sqlstatement)
            row = cursor.fetchall()
            connect.commit()
            connect.close()
            return row
        except:
            self.logging.debug('Datarecords database not found')
            connect.commit()
            connect.close()
            return None
        
    #Method 6.2 SQL EXECUTE
    def execute(self, sqlstatement):
        try:
            connect = sqlite3.connect(self.recordspath)
            cursor = connect.cursor()
            cursor.execute(sqlstatement)
            self.logging.debug(sqlstatement)
            return True
        except:
            self.logging.debug('Datarecords database not found')
            return None
            
    """
    End of script logging and exporting database to specified format. End log 
    method requires extractdata method to be precalled to work. 
    """
    #Method 7
    def endlog(self):
        self.logging.debug("Number of successfull COMTRADE API attempts {}".format(self.counter))
        self.logging.debug("Number of total attempts {}".format(self.totcounter))
        self.logging.debug("Number of empty dataframes {}".format(self.emptycounter))
        if self.outputDFType == 'json':
            self.outputDF.to_json(_outputfile+'/export.json', orient='columns')
        elif self.outputDFType =='excel':
            self.outputDF.to_excel(_outputfile+'/export.xlsx')
        else:
            self.outputDF.to_csv(_outputfile+'/export.csv')
            
    """Convert entire database to required format
        **CHARACTERIZATION FACTORS
    Refer to python json documentation for more information on types of
    orientation required for the output.
    """
    def generateCF(self, exportType, orient):
        exportF = ['csv', 'excel', 'json']
        if exportType in exportF:
            self.logging.debug("Exporting database in the format {}".format(exportType))
            CFType=exportType
        else:
            self.logging.debug("Exporting format not supported {}. Using default format [csv]".format(exportType))
            CFType="csv"
        try:
            conn = sqlite3.connect(self.recordspath, isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
            db_df = pd.read_sql_query("SELECT * FROM recorddata", conn)
            if CFType == "csv":
                db_df.to_csv(_outputfile+'/database.csv', index=False)
            elif CFType == "excel":
                db_df.to_excel(_outputfile+'/database.xlsx', index=False)
            elif CFType == "json":
                 db_df.to_json(_outputfile+'/database.json', orient = orient, index=False)
        except Exception as e:
            self.logging.debug(e)
            

        