import unittest
from .defaults import *
from assessment.utils import *
from assessment.trade import tradedata
test_tradedata = tradedata()

# testcase to test the gprs_comtrade function

#Extracting samples data from a list of resources, countries and years
Resources = random_sampler(ListofMetals, 5)
Countries = random_sampler(ListofCountries, 5)
Year = random_sampler(ListofYears, 5)
listofcountryname, listofresourcename = [], []
for i, n in enumerate(Resources):
    listofcountryname.append(ListofCountryName[ListofCountries.index(Countries[i])])
    listofresourcename.append(
        ListofMetalName[ListofMetals.index(n)]
    )


#Test class to test the functions in utils module
#Please note functions such as record data, extract data are excluded
class Testtradefunctions(unittest.TestCase):
     
    #Test to verify the functionality of the new Comtrade API
    
    def test_fetchcomtradeAPI(self):
        randomresource = random.choice(listofresourcename)
        randomyear = random.choice(Year)
        randomcountry = random.choice(listofcountryname)
        test_tradedata.callapirequestV2(str(randomyear), randomcountry, randomresource)
        tradedata = test_tradedata.tradedata
        price = test_tradedata.price
        self.assertIsNotNone(tradedata, msg="COMTRADE API non functional!")
        self.assertIsNotNone(price, msg="COMTRADE API non functional!")

    
    #Test to verify the functionality of the old Comtrade API
    def test_fetchOLDAPI(self):
        randomresource = random.choice(listofresourcename)
        randomyear = random.choice(Year)
        randomcountry = random.choice(listofcountryname)
        test_tradedata.callapirequestV1(str(randomyear), randomcountry, randomresource)
        tradedata = test_tradedata.tradedata
        self.assertIsNotNone(tradedata, msg="Old COMTRADE API non functional!")

    def test_fetchtradefiles(self):
        test_tradedata.tradefolder = r"C:\Users\anish\Documents\Folder"
        test_tradedata.setfolder()
        files = test_tradedata.tradefiles
        self.assertIsNotNone(files, msg="Trade data folder not found!")

    def test_fetchdata(self):
        test_tradedata.tradefolder = r"C:\Users\anish\Documents\Folder"
        test_tradedata.setfolder()
        test_tradedata.fetchdata()
        df = test_tradedata.tradedata
        self.assertIsNotNone(df, msg="Concatenation not working!")


    def test_writestats(self):
        test_tradedata.tradefolder = r"C:\Users\anish\Documents\Folder"
        test_tradedata.fetchdata()
        files = test_tradedata.tradefiles
        test_tradedata.fetchdata()
        test_tradedata.tradestatistics()