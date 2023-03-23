from tests.test_case_1 import test_1
#import comtradeapicall
"""get = comtradeapicall.previewTarifflineData(typeCode='C', freqCode='A', clCode='HS', period='2019',
                                             reporterCode='251', cmdCode='2605', flowCode='M', partnerCode=None,
                                             partner2Code=None,
                                             customsCode=None, motCode=None, maxRecords=500, format_output='JSON',
                                             countOnly=None, includeDesc=True)
print(get)"""
from assessment.core import worldtrade

data = worldtrade("2019", "97", "2605")