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
from .database import databases, logging
from .utils import *

if len(databases.regionslist) < 257:
    regions()


def HHI(rawmaterial: str, year: int, country: Union[str, int]):
    """
    Calculates the Herfindahl-Hirschman index of production of raw materials.
    which is normalized to the scale of 0 - 1.
    The dataframe is fetched from a utlity function.
    """
    proddf = getProd(rawmaterial).fillna(0)
    proddf = proddf[proddf["Country_Code"] != "DELETE"]

    if country == "Company":
        country = 975  # ASEAN Code (randomly chosen for no country)

    try:
        prod_year = proddf[str(year)].astype(int).tolist()
    except Exception as e:
        logging.debug(
            f"Error while extracting the production data, Raw Material : {rawmaterial}, Year: {year}, Country: {country} ",
            e,
        )
    HHI_Num = sumproduct(prod_year, prod_year)
    try:
        hhi = HHI_Num / (sum(prod_year) * sum(prod_year))
    except:
        logging.debug(
            f"Error while calculating the HHI. Raw Material : {rawmaterial}, year : {year}"
        )
        raise ValueError
    if cvtcountry(country, type="ISO") in proddf["Country_Code"].astype(int).tolist():
        try:
            ProdQty = float(
                proddf.loc[
                    proddf["Country_Code"].astype(int)
                    == cvtcountry(country, type="ISO"),
                    str(year),
                ].iloc[0]
            )
        except:
            logging.debug(
                f"Error while extracting the production quantity, Raw Material : {rawmaterial}, Year: {year}, Country: {country} "
            )
            raise ValueError
    else:
        ProdQty = 0
    try:
        if proddf["unit"].tolist()[0] == "kg":
            ProdQty = ProdQty / 1000
        elif (
            proddf["unit"].tolist()[0] != "metr. t"
            and proddf["unit"].tolist()[0] != "kg"
        ):
            logging.info("Raw material not in metric tonne or kilos")
        elif proddf["unit"].tolist()[0] == "Mio m3":
            """
            1 m³ = 0.8 kg = 0.0008 metr. t
            """
            ProdQty = ProdQty * 0.0008
    except Exception as e:
        logging.debug(
            f"Error while converting the production quantities, Raw Material : {rawmaterial}, Year: {year}, Country: {country} "
            f"Production Qty is {ProdQty} and the dataframe is {proddf}",
            e,
        )
        raise Exception from e

    """
    The output includes the production quantity of a raw material for a country in a given year and the Herfindahl-Hirschman Indexfor that year.
    'ProdQty' : float
    'hhi': float
    """
    return ProdQty, hhi


def importrisk(rawmaterial: str, year: int, country: str, data):
    """
    The second part of the equation of the GeoPolRisk method is referred to as 'import risk'.
    This involves weighting the import quantity with the political stability score.
    The political stability score is derived from the
    Political Stability and Absence of Violence indicator of the Worldwide Governance Indicators.
    For more information, see Koyamparambath et al. (2024).
    """

    def wgi_func(x):
        """
        For a country whose political stability score is missing, a score of 0.5 is assigned.
        """
        if isinstance(x, float):
            return x
        else:
            if x is None or isinstance(x, type(None)) or x.strip() == "NA":
                return 0.5
            else:
                return x

    Numerator, TotalTrade, Price = 0.0, 0.0, 0.0
    if type(country) is not list:
        ctry = databases.regionslist[cvtcountry(country, type="Name")]
    else:  # If the country is already a list, use it directly
        ctry = country
    try:
        Numerator, TotalTrade, Price = aggregateTrade(year, ctry, rawmaterial, data)
    except Exception as e:
        logging.debug(
            f"The inputs for calculating the 'import risk' dont match, Country: {country} + Error :{e}"
        )
        raise ValueError

    """
    'Numerator' : float
    'TotalTrade' : float
    'Price' : float
    """
    return Numerator, TotalTrade, Price


def importrisk_company(
    rawmaterial: str, year: int, file_name=None, excel_sheet_name=None, mode="prod"
):
    """
    The 'import risk' for a company differs from that of the country's.
    This data is provided in a template in the output folder.
    The utility function transforms the data into a
    usable format similar to that of the country-level data.
    """
    tradedf = transformdata(file_name, excel_sheet_name, mode)
    df_query = f"(period == {year}) & (rawMaterial == '{rawmaterial}')"

    data = tradedf.query(df_query)
    print(data)
    QTY = data["qty"].astype(float).tolist()
    WGI = data["partnerWGI"].astype(float).tolist()
    VAL = data["cifvalue"].astype(float).tolist()
    try:
        Price = sum(VAL) / sum(QTY)
        TotalTrade = sum(QTY)
        Numerator = sumproduct(QTY, WGI)
    except:
        logging.debug(
            f"Error while making calculations. Raw Material: {rawmaterial}, Country: Company, Year: {year}"
        )
        raise ValueError
    """
    'Numerator' : float
    'TotalTrade' : float
    'Price' : float
    """
    return Numerator, TotalTrade, Price


def GeoPolRisk(Numerator, TotalTrade, Price, ProdQty, hhi):
    """
    The GeoPolRisk method has two value outputs: the GeoPolRisk Score,
    a non-dimensional score useful for comparative risk assessment,
    and the characterization factor, which is used for evaluating
    the GeoPolitical Supply Risk in Life Cycle Assessment with units of eq. kg-Cu/kg.
    """
    Denominator = TotalTrade + ProdQty
    try:
        WTA = Numerator / Denominator
    except:
        logging.debug(
            f"Check the Numerator and Denominator. Numerator: {Numerator}, Denominator: {Denominator}"
        )
        WTA = 0
    Score = hhi * WTA
    CF_Cu = 0.409412948  # Average CF of copper for OECD countries for a period from 2017 - 2021
    CF = (Score * Price) / CF_Cu
    """
    'Score' : GeoPolRisk Score : float
    'CF' : GeoPolitical Supply Risk Potential : float
    'WTA': Import Risk : float
    """
    return Score, CF, WTA
