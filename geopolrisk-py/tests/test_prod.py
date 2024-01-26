import unittest
from .defaults import *
from assessment.utils import *
from assessment.mineproduction import productiondata
test_productiondata = productiondata()

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
class Testprodfunctions(unittest.TestCase):
     
    
    def test_fetchproductionData(self):
        randomresource = random.choice(listofresourcename)
        test_productiondata.get_prod_df(randomresource)
        df = test_productiondata.prod
        self.assertIsNotNone(df, msg="Fetching resource data failed!")

    def test_fetchHHi(self):
        randomresource = random.choice(listofresourcename)
        randomyear = random.choice(Year)
        test_productiondata.get_prod_df(randomresource)
        test_productiondata.get_hhi(randomyear)
        HHI = test_productiondata.HHI
        self.assertIsNotNone(HHI, msg = "Calculating HHI failed!")
        self.assertNotEqual(HHI,0, msg ="Error in calculating HHI check logs!")

    
    def test_fetchQty(self):
        randomcountry = random.choice(listofcountryname)
        randomresource = random.choice(listofresourcename)
        randomyear = random.choice(Year)
        test_productiondata.get_prod_df(randomresource)
        test_productiondata.get_prodQuantity(randomcountry, randomyear)
        Qty = test_productiondata.prodQty
        self.assertIsNotNone(Qty, msg = "Calculating Qty failed!")
        test_productiondata.get_prodQuantity(listofcountryname, randomyear)
        Qty_l = test_productiondata.prodQty
        self.assertIsNotNone(Qty_l, msg = "Calculating Qty_l failed!")

    def test_all(self):
        randomcountry = random.choice(listofcountryname)
        randomresource = random.choice(listofresourcename)
        randomyear = random.choice(Year)
        HHI, Qty = test_productiondata.getallprod(randomresource, randomcountry, randomyear)
        HHI_l, Qty_l = test_productiondata.getallprod(randomresource, listofcountryname, randomyear)
        self.assertIsNotNone(HHI, msg = "Calculating HHI failed!")
        self.assertIsNotNone(Qty, msg = "Calculating Qty failed!")
        self.assertIsNotNone(HHI_l, msg = "Calculating HHI_l failed!")
        self.assertIsNotNone(Qty_l, msg = "Calculating Qty_l failed!")