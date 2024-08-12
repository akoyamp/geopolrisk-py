# Copyright (C) 2024 University of Bordeaux, CyVi Group & University of Bayreuth,
# Ecological Resource Technology & Anish Koyamparambath, Christoph Helbig, Thomas Schraml
# This file is part of geopolrisk-py library.
# geopolrisk-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# geopolrisk-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with geopolrisk-py.  If not, see <https://www.gnu.org/licenses/>.

import itertools
from tqdm import tqdm
from .database import databases, logging
from .core import *
from .utils import *


def gprs_calc(period: list, country: list, resource: list, region_dict = {}):
    """
    A single aggregate function performs all calculations and exports the results as an Excel file.
    The inputs include a list of years, a list of countries, 
    and a list of resources, with an optional dictionary for defining new regions.
    The lists can contain resource names such as 'Cobalt' and 'Lithium',
    and country names like 'Japan' and 'Canada', or alternatively, HS codes and ISO digit codes.
    
    For regional assessments, regions must be defined in the dictionary with country names,
    not ISO digit codes.
    For example, the 'West Europe' region can be defined as 
    { 
        'West Europe': ['France', 'Germany', 'Italy', 'Spain', 'Portugal', 'Belgium', 'Netherlands', 'Luxembourg']
        }.
    """
    Score_list, CF_list = [], []
    hhi_list, ir_list, price_list = [], [], []
    dbid = []
    ctry_db, rm_db, period_db = [], [], []
    regions(region_dict) #Function to define region
    if databases.regional == False:
        #Calculation loop for non regional assessment
        for year, ctry, rm in tqdm(
            list(itertools.product(period, country, resource)),
            desc="Calculating the GeoPolRisk: "
            ):
            try:
                ProdQty, hhi = HHI(rm, int(year), ctry)
            except ValueError:
                logging.debug("Couldnt calculate the HHI. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Numerator, TotalTrade, Price = importrisk(
                    cvtresource(rm, type="HS"), year, databases.regionslist[cvtcountry(ctry, type="Name")]
                )
            except ValueError:
                logging.debug("Couldnt calculate the Import Risk. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Score, CF, IR = GeoPolRisk(Numerator, TotalTrade, Price, ProdQty, hhi)
            except ValueError:
                logging.debug("Couldnt calculate the GeoPolRisk. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Score_list.append(Score)
                CF_list.append(CF)
                hhi_list.append(hhi)
                ir_list.append(IR)
                price_list.append(Price)
                ctry_db.append(cvtcountry(ctry, type="Name"))
                rm_db.append(cvtresource(rm, type="Name"))
                period_db.append(year)
                dbid.append(create_id(cvtresource(rm, type="HS"), cvtcountry(ctry, type="ISO"), year))
            except Exception as e:
                logging.debug("Error while recording data for non regional assessment!", e)
    else:
        for year, ctry, rm in tqdm(
            list(itertools.product(period, country, resource)),
            desc="Calculating the GeoPolRisk: "):
            try:
                Numerator, TotalTrade, Price = aggregateTrade(
                    year, databases.regionslist[ctry], cvtresource(rm, type="HS")
                )
            except ValueError:
                logging.debug("Couldnt calculate the Import Risk - Regional. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                sum_ProdQty = []
                for j in databases.regionslist[ctry]:
                    ProdQty, hhi = HHI(rm, int(year), j)
                    sum_ProdQty.append(ProdQty)
            except ValueError:
                logging.debug("Couldnt calculate the HHI and Production Quantity - Regional. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            try:
                Score, CF, IR = GeoPolRisk(Numerator, TotalTrade, Price, sum(sum_ProdQty), hhi)
            except ValueError:
                logging.debug("Couldnt calculate the GeoPolRisk - Regional. Check functional error!")
                break
            except Exception as e:
                logging.debug("Unknwon exception at ", e)
                break
            
            try:
                Score_list.append(Score)
                CF_list.append(CF)
                hhi_list.append(hhi)
                ir_list.append(IR)
                price_list.append(Price)
                ctry_db.append(ctry)
                rm_db.append(cvtresource(rm, type="Name"))
                period_db.append(year)
                dbid.append(create_id(cvtresource(rm, type="HS"), ctry, year))
            except Exception as e:
                logging.debug("Error while recording data for regional assessment!", e)

    result = createresultsdf()
    try:
        result["DBID"] = dbid
        result["Country [Economic Entity]"] = ctry_db
        result["Raw Material"] = rm_db
        result["Year"] = period_db
        result["GeoPolRisk Score"] = Score_list
        result["GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"] = CF_list
        result["HHI"] = hhi_list
        result["Import Risk"] = ir_list
        result["Price"] = price_list

        excel_path = databases.directory + "/output/results.xlsx"
        result.to_excel(excel_path, index=False)
    except Exception as e:
        logging.debug("Error while recording data into dataframe for regional assessment!", e)