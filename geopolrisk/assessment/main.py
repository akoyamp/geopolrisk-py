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


from .__init__ import databases, logging

from .core import *
from .utils import *


def gprs_calc(period: list, country: list, resource: list):
    Score_list, CF_list = [], []
    hhi_list, ir_list, price_list = [], [], []
    dbid = []

    def returntrade(country: list, resource: list):
        HS_Map = databases.production["HS Code Map"]
        ISO_Map = databases.production["Country_ISO"]
        resource_HS = []
        for i in resource:
            if i in HS_Map["ID"].tolist():
                resource_HS.append(HS_Map.loc[HS_Map["ID"] == resource, "HS Code"][0])
            elif i in HS_Map["HS Code"].tolist():
                resource_HS.append(i)
            else:
                raise ValueError
        country_ISO = []
        for j in country:
            if j in ISO_Map["Country"].tolist():
                country_ISO.append(ISO_Map.loc[ISO_Map["Country"] == country, "ISO"])
            elif j in ISO_Map["ISO"].tolist():
                country_ISO.append(i)
            else:
                raise ValueError
        return country_ISO, resource_HS

    ISO, HS = returntrade(country, resource)
    for year, ctry, rm in zip(period, country, resource):
        ProdQty, hhi = HHI(rm, int(year), ctry)
        Numerator, TotalTrade, Price = importrisk(
            HS[resource.index(rm)], year, ISO[country.index(ctry)]
        )
        Score, CF, IR = GeoPolRisk(Numerator, TotalTrade, Price, ProdQty, hhi)
        Score_list.append(Score)
        CF_list.append(CF)
        hhi_list.append(hhi)
        ir_list.append(IR)
        price_list.append(Price)
        dbid.append(create_id(HS[resource.index(rm)], ISO[country.index(ctry)], year))

    result = createresultsdf()
    result["DBID"] = dbid
    result["Country [Economic Entity]"] = country
    result["Raw Material"] = resource
    result["Year"] = period
    result["GeoPolRisk Score"] = Score_list
    result["GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"] = CF_list
    result["HHI"] = hhi_list
    result["Import Risk"] = ir_list
    result["Price"] = price_list

    excel_path = databases.directory + "/output/results.xlsx"
    result.to_excel(excel_path, index=False)
