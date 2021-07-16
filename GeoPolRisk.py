# Copyright 2020-2021 by Anish Koyamparambath and University of Bordeaux. All Rights Reserved.
#
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



import pandas as pd, sys, getpass, json, sqlite3, logging
from api import comtrade, RUNError
from difflib import get_close_matches
from datetime import datetime



#Fetch username for the purpose of logging.
username = getpass.getuser()

class main(comtrade):
    """Do not modify the path for the logs folder unless you specifically need
    it elsewhere. Modify the alert level depending on requirements for debugging. 
    """
    #Method 0
    def __init__(self):
        Filename = './logs//function({:%Y-%m-%d(%H-%M-%S)}).log'.format(datetime.now())
        self.module = False
        self.logging = logging
        self.logging.basicConfig(
            level = logging.DEBUG,
            format = '%(asctime)s | %(levelname)s | %(threadName)-10s | %(filename)s:%(lineno)s - %(funcName)20s() | %(message)s',
            filename = Filename,
            filemode = 'w'
            )
        _columns = ["Year", "Resource", "Country", "GeoPolRisk", "HHI", "WA"]
        self.outputDF = pd.DataFrame(columns = _columns)
        self.counter = 0
        self.totcounter = 0
        self.logging.debug('Username: {}'.format(username))
        self.totalreduce = 0
        
    """The program is equipped with a predefined database for production of a 
    raw material, HS codes of those raw materials, ISO country codes and a
    database to link the HS codes to the production of raw material. Change the 
    path of the respective databases to customize the calculation.
    """    
    #Method 2
    def setpath(self,
             prod_path = './lib/production.xlsx',
             reporter_path = './lib/rep.json',
             hs_code = './lib/hs.json',
             metals = './lib/metalsg.csv'):
        self.prod_path = prod_path
        self.reporter_path = reporter_path
        self.hs = hs_code
        self.metals = metals
        self.regions()
        #Confirmation of loading this function
        self.module = True

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
    def regions(self):
        self.EU = ['Austria', 'Belgium', 'Belgium-Luxembourg', 'Bulgaria',
                   'Croatia', 'Czechia', 'Czechoslovakia', 'Denmark', 
                   'Estonia','Finland', 'France', 'Fmr Dem. Rep. of Germany',
                   'Fmr Fed. Rep. of Germany', 'Germany', 'Greece', 'Hungary',
                   'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 
                   'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 
                   'Slovakia', 'Slovenia', 'Spain', 'Sweden']

      
    """
    Method 1, is the first method that will be called if exucting the main function 
    i.e Method 0 of API class. It ensures if the other methods are loaded before.
    """
    #Method 1    
    def run(self):
        if self.module != True:
            self.setpath()
            self.regions()


    """
    A simple guided step by step method for new users. This method can be called 
    to any console based application if needed.
    """
    #Method 4   
    def simplerun(self):
        #4.1 Call Method 1
        self.run()
        
        """
        List of available production information of metals which is later cross
        verified for confirmation with the hs code. Also, the production information
        is organized using the common name of the raw material which can later be altered
        when automatic download of data is created.
        """
        #4.2 Extracting data from linking database
        MetalsDF = pd.read_csv(self.metals)
        Metals = MetalsDF.id.tolist()
        HS = MetalsDF.hs.tolist()
        
        """
        Connect country to country codes. These codes and files are only necessary
        for guided run.
        """
        #4.3 Extracting data from ISO country codes database
        json_file = open(self.reporter_path, 'r')
        data = pd.json_normalize(json.loads(json_file.read())['results'])
        Country = data.text.tolist()
        
        
        """
        Following section gets the input of the resource/raw material from the user.
        Keeping in mind the possibility of error from the user, get close matches 
        library is used and reverified by the user. If found cumbersome an additional 
        code to verify letter to letter can be created. The input is fed as key to 
        fetch the resource hscode to be used in the API. Sections 4.5 also follows
        the same pattern.
        """
        #4.4 Input information on raw material
        print('Enter the name the resource whose supply risk you want to assess')
        metal = input('Resource Name : ')
        Metalcloselist = get_close_matches(metal, Metals)
        if len(Metalcloselist) > 1:
            print("The following metals are found close to your query ")
            print(Metalcloselist)
            try:
                index = int(input("Enter the selected resources as 1, 2 etc., :" ))
                resource = Metalcloselist[index - 1]
            except ValueError:
                print("Please enter proper value!")
                raise RUNError(1)
        elif len(Metalcloselist) == 0:
            print("The entered resource is not found")
            sys.exit(1)
        elif len(Metalcloselist) == 1 and metal != Metalcloselist[0]:
            print("The entered resource is not found")
            sys.exit(1)
        else:
            resource = Metalcloselist[0]
        metal = resource
        HSCode = HS[Metals.index(resource)]
        
        #4.5 Input information on country/region
        print('Enter the name the country whose supply risk you want to assess')
        Ctry = input('Country Name : ')
        countrycloselist = get_close_matches(Ctry, Country)
        if len(countrycloselist) > 1:
            print("The following metals are found close to your query ")
            print(countrycloselist)
            try:
                index = int(input("Enter the selected country as 1, 2 etc., :" ))
                country = countrycloselist[index-1]
            except ValueError:
                print("Please enter a proper value!")
                raise RUNError(1)
        elif len(countrycloselist) == 0:
            print("The entered Country not found")
            sys.exit(1)
        else:
            country = countrycloselist[0]
        reporter = data.loc[data['text'] == str(country), 'id'].iloc[0]
        
        period = input("Enter the year of assessment :")
        try:
            period = int(period)
        except Exception as e:
            self.logging.debug(e)
            raise RUNError(1)
        
        print("Enter the rate of domestic recycling input of the raw material (in fractions)")
        recyclingrate = input("Enter the recycling input rate: ")
        try:
            if float(recyclingrate) in range(0,101):
                recyclingrate = float(recyclingrate)
        except Exception as e:
            print("Provide correct inputs! Try again")
            self.logging.debug(e)
            raise RUNError(1)
        
        print("Select 0 for assuming a best case scenario where the imports from a riskier country is reduced")
        print("Select 1 for assuming a best case scenario where the imports from a stable country is reduced")
        scenario = input("Select 1 or 0: ")
        
        try:
            if int(scenario) in [0, 1]:
                scenario = int(scenario)
        except Exception as e:
            print("Provide correct inputs! Try again")
            self.logging.debug(e)
            raise RUNError(1)
        
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
            json_file = open(self.hs, 'r')
            hs_element = pd.json_normalize(json.loads(json_file.read())['results'])
            hs_element = hs_element.loc[hs_element['id'] == str(HSCode), 'text'].iloc[0]
        except Exception as e:
            self.logging.debug(e)
            raise RUNError(1)
        print("Info: The HS code used for the analysis is "+str(hs_element))
        
        #4.8 API CALL
        self.TotalCalculation(period = int(period), 
                              reporter = int(reporter), 
                              HSCode = int(HSCode),
                              recyclingrate = recyclingrate,
                              scenario = scenario)
        print("The GeoPolRisk Value for "+metal+" during "+str(period)+" for "+country+" is "+str(self.GPRS))


    
    """
    SQL select method, to pull records in method 5 and 6. This program is used
    only to pull records (ONLY SELECT STATEMENT)
    """
    def select(self, sqlstatement):
            try:
                connect = sqlite3.connect('./lib/datarecords.db')
                cursor = connect.cursor()
            except:
                self.logging.debug('Database not found')
            cursor.execute(sqlstatement)
            row = cursor.fetchall()
            connect.commit()
            connect.close()
            return row

    """
    Records the data to an sqlite database. The database is not protected.
    """
    #Method 5   
    def recorddata(self, Year, GPRS, WA, HHI, Country, Metal):
        #5.1 Method to execute non select
        def execute(sqlstatement):
            try:
                connect = sqlite3.connect('./lib/datarecords.db')
                cursor = connect.cursor()
            except:
                self.logging.debug('Database not found')
            cursor.execute(sqlstatement)
            connect.commit()
            connect.close()
        
        """
        The sql statement below is executed everytime this method (Method 5) is
        called. Negates any error in storing data by verifying the existance of 
        such table.
        """
        #5.1 Initial run to create a database if not exists
        try:
            sqlstatement = """CREATE TABLE IF NOT EXISTS recordData 
            (id INTEGER PRIMARY KEY, Country TEXT NOT NULL, Resource 
            TEXT NOT NULL, Year INTEGER NOT NULL, GeoPolRisk TEXT, WeightAvg TEXT);""" 
            execute(sqlstatement)
        except Exception as e:
            self.logging.debug(e)
                   
        """
        Insert new data after verifying if the data is not available.
        """
        #5.2 Select run to fetch if the data preexists
        try:
            sqlstatement = "SELECT * FROM recordData WHERE Country = '"+Country+"' AND Resource= '"+Metal+"' AND Year = '"+Year+"';"
            row = self.select(sqlstatement)   
            if len(row) == 0 or Year not in row:
                sqlstatement = "INSERT INTO recordData (Country, Resource, Year, GeoPolRisk, Weightavg) VALUES ('"+Country+"','"+Metal+"','"+Year+"','"+GPRS+"','"+WA+"');"
                execute(sqlstatement)
            else:
                self.logging.debug("Redundancy detected! Entry not recorded.")
        except Exception as e:
            self.logging.debug(e)
    
    
    """
    Data extraction method, into csv, json or excel
    """        
    #Method 6
    def extractdata(self, Year, Country, Metal, Type="csv"):
        exportF = ['csv', 'excel', 'json']
        if Type in exportF:
            self.logging.debug("Exporting database in the format {}".format(Type))
            self.outputDFType=Type
        else:
            self.logging.debug("Exporting format not supported {}. Using default format [csv]".format(Type))
            self.outputDFType="csv"
        try:
            data = self.select("SELECT GeoPolRisk, WeightAvg FROM recordData WHERE Country = '"+Country+"' AND Resource= '"+Metal+"' AND Year='"+Year+"'")
        except Exception as e:
            self.logging.debug(e)
        if len(data) !=0:
            toappend = [Year,Metal,Country,data[0][0],0,data[0][1]]
            self.GPRS = data[0][0]
            self.outputDF.loc[len(self.outputDF)] = toappend
            
    """
    End of script logging and exporting database to specified format. End log 
    method requires extractdata method to be precalled to work. 
    """
    #Method 7
    def endlog(self):
        self.logging.debug("Number of successfull COMTRADE API attempts {}".format(self.counter))
        self.logging.debug("Number of total attempts {}".format(self.totcounter))
        if self.outputDFType == 'json':
            self.outputDF.to_json('./output/export.json', orient='columns')
        elif self.outputDFType =='csv':
            self.outputDF.to_csv('./output/export.csv')
        elif self.outputDFType == 'excel':
            self.outputDF.to_excel('./output/export.excel')