from .__init__ import instance, logging, execute_query
from .utils import *
from trade import tradedata as td
from mineproduction import productiondata as prd
import pandas as pd
td = td()
prd = prd()

class geopolrisk:

    def __init__(self):
        self.importrisk = None
        self.gprs = None
        self.cf = None

    def getdata(self):
        #verify if the extracted data are goods
        if not (isinstance(td.tradedata, pd.DataFrame),
            isinstance(prd.HHI, float),
            isinstance(prd.prodQty, float)):
            raise Exception("Error while extracting data!")
        else:
            self.tradedata = td.tradedata
            self.hhi = prd.HHI
            self.prod_qty = prd.prodQty
        
    def importrisk(self, year=int, resource=str, country=list):
        pass