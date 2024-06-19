from geopolrisk.assessment.core import *
from geopolrisk.assessment.__init__ import instance #Optional


_price = instance.price
_wgi = instance.wgi
Resource = "Nickel"
HS = "260400"
Country = "Germany"
ISO = "276"
Year = "2020"

regions()
TradeData, priceif = worldtrade(year = Year, country = ISO, commodity = HS)
ProductionData = ProductionData(Resource, Country)
WTAData = weightedtrade(Year, TradeData = TradeData, PIData = _wgi, scenario = 0, recyclingrate = 0.00)


YearlyAveragePrice = 10203.98
YearlyAveragePrice =  _price[Year].tolist()[_price.HS.to_list().index(HS)] #Optional - A database already exists that can be used to fetch the price data.

result = GeoPolRisk(ProductionData, WTAData, Year, YearlyAveragePrice)