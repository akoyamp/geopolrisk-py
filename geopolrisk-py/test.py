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

from assessment.operations import update_cf, gprs_comtrade
import time


# ListofMetals = [2606, 261710, 2524, 2511, 8106, 8107, 2610, 2701, 810520, 2603, 7108, 2504, 
#                  2601, 2607, 283691, 251910, 2602, 280540, 2613, 271111, 2604, 2709, 2846, 261610, 
#                  2609, 2611, 2608, 261510 ]

# #ShortListofMetals = [2602, 2601, 2603, 2846, 2614,]
# ListofCountries = [36, 124, 97, 251, 276, 392, 826, 842,] 
# #ShortListofCountries = [36, 124, 97, 251]#
# Year = [2002, 2003,  2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
#         2014, 2015, 2016, 2017, 2018, 2019, 2020]#,
# #ShortListofYear = [2017, 2018, 2019, 2020]

# for i in range(100):
#     try:
#         gprs_comtrade(ListofMetals, ListofCountries, Year, 0, 0)
#     except Exception as e:
#         print(e)
#         continue
#     time.sleep(3600)

# for i in range (10):
#     try:
#         update_cf()
#     except Exception as e:
#         print(e)
#         continue
#     time.sleep(3600)
# from assessment.gprsplots import compareplot

# dip = compareplot(["Australia", "France", "Canada", "European Union"],[2014], ["Manganese","Iron", "Copper", "Petroleum"], 0)
# dip.show()

from assessment.operations import updateprice 
updateprice()

#gprs_comtrade([7108,2504], [97], [2020], 0, 0, database="update")

# #Recycling Scenarios
# ShortListofMetals = [283691, 2602, 2603, 2604, 810520]#,  283691, 2602, 2603, 2604, 810520
# ShortListofCountries = [97]#
# ShortListofYear = [2016]
# try:
#     gprs_comtrade(ShortListofMetals,ShortListofCountries, ShortListofYear, 0  , 0 )
# except Exception as e:
#     print(e)

# from tests import test