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


from typing import Union
from .__init__ import databases, logging
from .utils import *


def HHI(resource: Union[str, int], year: int, country: str):
    proddf = getProd(resource)
    proddf = proddf[proddf["Country_Code"] != "DELETE"]
    prod_year = proddf[str(year)].tolist()
    HHI_Num = sumproduct(prod_year, prod_year)
    hhi = HHI_Num / (sum(prod_year) * sum(prod_year))
    ProdQty = proddf.loc[proddf["Country" == country, str(year)]]
    if proddf["unit"].tolist()[0] == "kg":
        ProdQty = float(ProdQty) / 1000
    elif proddf["unit"].tolist()[0] != "metr. t" and proddf["unit"].tolist()[0] != "kg":
        raise ValueError
    elif proddf["unit"].tolist()[0] != "Mio m3":
        """
        1 m³ = 0.8 kg = 0.0008 metr. t
        """
        ProdQty = float(ProdQty) * 0.0008
    return ProdQty, hhi


def importrisk(resource: int, year: int, country: list):
    if databases.regional != True:
        ctry = country[0]
        tradedf = getbacidata(year, ctry, resource, data=databases.baci_trade)
        QTY = tradedf["qty"].tolist()
        WGI = tradedf["partnerWGI"].tolist()
        VAL = tradedf["cifvalue"].tolist()

        Price = sum(VAL) / sum(QTY)
        TotalTrade = sum(QTY)
        Numerator = sumproduct(QTY, WGI)
    else:
        Numerator, TotalTrade, Price = aggregateTrade(
            year, country, resource, data=databases.baci_trade
        )

    return Numerator, TotalTrade, Price


def importrisk_company(resource: int, year: int):
    tradedf = transformdata()
    df_query = f"(period == '{year}')  & (cmdCode == '{resource}')"
    baci_data = tradedf.query(df_query)

    QTY = baci_data["qty"].tolist()
    WGI = baci_data["partnerWGI"].tolist()
    VAL = baci_data["cifvalue"].tolist()
    Price = sum(VAL) / sum(QTY)
    TotalTrade = sum(QTY)
    Numerator = sumproduct(QTY, WGI)
    return Numerator, TotalTrade, Price


def GeoPolRisk(Numerator, TotalTrade, Price, ProdQty, HHI):
    Denominator = TotalTrade + ProdQty
    WTA = Numerator / Denominator
    Score = HHI * WTA
    CF = Score * Price
    return Score, CF, WTA
