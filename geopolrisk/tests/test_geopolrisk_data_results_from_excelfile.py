import unittest
import pandas as pd
import numpy as np
import os
from pathlib import Path

from geopolrisk.assessment.core import HHI, importrisk, GeoPolRisk

# Load Excel file once globally for all tests
EXCEL_PATH = os.path.join(Path(__file__).parent.resolve().parent, "tests", "Testing case - tool.xlsx")

class TestGeoPolRiskPy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Load all required sheets from the Excel file into class variables as pandas DataFrames.
        This avoids reloading for each test and ensures consistent test data.
        """
        cls.df_geopolrisk = pd.read_excel(EXCEL_PATH, sheet_name="GeoPolRisk")
        cls.df_nickel = pd.read_excel(EXCEL_PATH, sheet_name="Nickel")
        cls.df_manganese = pd.read_excel(EXCEL_PATH, sheet_name="Manganese")
        cls.df_graphite = pd.read_excel(EXCEL_PATH, sheet_name="Graphite")
        cls.df_trade = pd.read_excel(EXCEL_PATH, sheet_name="Trade Data")
        cls.df_wgi = pd.read_excel(EXCEL_PATH, sheet_name="WGI")

        # Prepare WGI data as dictionary or DataFrame indexed by country code and year for fast lookup
        # WGI sheet has columns: country_code and years as columns
        # We will convert to a dict {(country_code, year): wgi_value}
        wgi_data = {}
        years = [col for col in cls.df_wgi.columns if str(col).isdigit()]
        for _, row in cls.df_wgi.iterrows():
            country_code_raw = row['country_code']
            if pd.isna(country_code_raw):
                # Skip rows without valid country_code
                continue
            country_code = int(country_code_raw)
            for year in years:
                val = row[year]
                if pd.isna(val):
                    # Optional: skip missing WGI values or set default
                    continue
                wgi_data[(country_code, int(year))] = val
        cls.wgi_data = wgi_data

        # Create dictionary of production data for quick lookup by (rawmaterial, year, country_code)
        # For Nickel/Manganese/Graphite, map from respective sheet
        def create_production_dict(df):
            prod_dict = {}
            for _, row in df.iterrows():
                country_code = row['Country_Code']
                for year in [2018, 2019, 2020, 2021, 2022]:
                    prod_dict[(country_code, year)] = row.get(str(year), 0)
            return prod_dict

        cls.prod_nickel = create_production_dict(cls.df_nickel)
        cls.prod_manganese = create_production_dict(cls.df_manganese)
        cls.prod_graphite = create_production_dict(cls.df_graphite)

    def get_production_qty(self, rawmaterial: str, year: int, country_code: int):
        """
        Return production quantity from the respective production dataframe based on rawmaterial.
        """
        if rawmaterial.lower() == "nickel":
            return self.prod_nickel.get((country_code, year), 0)
        elif rawmaterial.lower() == "manganese":
            return self.prod_manganese.get((country_code, year), 0)
        elif rawmaterial.lower() == "graphite":
            return self.prod_graphite.get((country_code, year), 0)
        else:
            return 0

    def get_wgi(self, country_code: int, year: int):
        """
        Return WGI value from preprocessed WGI data dictionary.
        """
        return self.wgi_data.get((country_code, year), np.nan)

    def filter_trade_data(self, year: int, importer_code: int, rawmaterial: str):
        """
        Filters the trade data DataFrame for a given year, importing country, and raw material.
        The function matches the HS code of the raw material with the semicolon-separated list
        of HS codes in the 'Resource HSCODE' column and returns only the matching rows.

        Parameters:
            year (int): The year to filter by.
            importer_code (int): The code of the importing country.
            rawmaterial (str): The raw material name (used to look up the HS code).

        Returns:
            pd.DataFrame: Filtered DataFrame containing only rows matching the criteria.
        """

        # Filter for the specified year and importing country
        df = self.df_trade[
            (self.df_trade['Year'] == year) &
            (self.df_trade['Importing Country'] == importer_code) &
            (self.df_trade['rawMaterial'] == rawmaterial)
        ].copy()

        return df

    def map_trade_data_columns(self, df_excel: pd.DataFrame) -> pd.DataFrame:
        """
        Maps the columns from the Excel 'Trade Data' sheet to the expected
        column names as in the baci_trace database table.
        """
        # Create a copy to avoid modifying the original DataFrame
        df = df_excel.copy()

        # Define mapping: Excel column -> database column
        column_mapping = {
            "Year": "period",
            "Exporting Country": "partnerCode",
            # You can add 'partnerDesc' and 'partnerISO' if you have the info
            "Importing Country": "reporterCode",
            # You can add 'reporterDesc' and 'reporterISO' if you have the info
            "rawMaterial": "rawMaterial",  # keep as is if needed
            "Resource HSCODE": "cmdCode",
            "Quantity (mTonnes)": "qty",
            "Trade Value (1000 USD)": "cifvalue",
            "WGI": "partnerWGI",
            # "QUANTITY * WGI": not needed for importrisk()
        }

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Ensure all required columns exist (fill with NaN if missing)
        required_columns = [
            "period", "reporterCode", "rawMaterial", "reporterDesc", "reporterISO",
            "partnerCode", "partnerDesc", "partnerISO",
            "cmdCode", "qty", "cifvalue", "partnerWGI"
        ]
        for col in required_columns:
            if col not in df.columns:
                df[col] = pd.NA

        # Reorder columns as expected by importrisk (optional)
        df = df[required_columns]

        # change the dtype for cmdCode to str
        df['cmdCode'] = df['cmdCode'].astype(str)

        return df

    def test_HHI_function(self):
        for rawmaterial in ["Nickel", "Manganese", "Graphite"]:
            df_subset = self.df_geopolrisk[self.df_geopolrisk['Raw Material'] == rawmaterial]
            for _, row in df_subset.iterrows():
                year = int(row['Year'])
                country_code = int(row['Importer Code'])
                result = HHI(rawmaterial=rawmaterial, year=year, country=country_code)
                
                prodqty = result[0]
                hhi = result[1]
                
                expected_prodqty = row['Domestic Production']
                expected_hhi = row['HHI']
                
                print("\n")
                print(f"compare ProdQty: calculatete by geopolrisk: {prodqty} value from Excel-File: {expected_prodqty} - for {rawmaterial} {year} {country_code}")
                self.assertAlmostEqual(prodqty, expected_prodqty, places=2, msg=f"ProdQty mismatch for {rawmaterial} {year} {country_code}")
                print(f"compare HHI: calculatete by geopolrisk: {hhi} value from Excel-File: {expected_hhi} - for {rawmaterial} {year} {country_code}")
                self.assertAlmostEqual(hhi, expected_hhi, places=6, msg=f"HHI mismatch for {rawmaterial} {year} {country_code}")

    def test_importrisk_function(self):
        for rawmaterial in ["Nickel", "Manganese", "Graphite"]:
            df_subset = self.df_geopolrisk[self.df_geopolrisk['Raw Material'] == rawmaterial]
            for _, row in df_subset.iterrows():
                year = int(row['Year'])
                importer_code = int(row['Importer Code'])
                trade_data_filtered = self.filter_trade_data(year, importer_code, rawmaterial)
                # Map columns for compatibility
                if not trade_data_filtered.empty:
                    trade_data_arg = self.map_trade_data_columns(trade_data_filtered)
                else:
                    # Create empty DataFrame with correct columns
                    trade_data_arg = self.map_trade_data_columns(pd.DataFrame(columns=self.df_trade.columns))
                # hscode = str(row['HS CODE'])
                result = importrisk(rawmaterial=rawmaterial, year=year, country=importer_code, data=trade_data_arg)
                
                numerator = result[0]
                totaltrade = result[1]
                price = result[2]

                expected_numerator = row['Numerator']
                expected_totaltrade = row['Total Trade']
                expected_price = row['Price']
                
                print("\n")
                print(f"compare Numerator: calculatete by geopolrisk: {numerator} value from Excel-File: {expected_numerator} - for {rawmaterial} {year} {importer_code}")
                self.assertAlmostEqual(numerator, expected_numerator, places=5, msg=f"Numerator mismatch for {rawmaterial} {year} {importer_code}")
                print(f"compare TotalTrade: calculatete by geopolrisk: {totaltrade} value from Excel-File: {expected_totaltrade} - for {rawmaterial} {year} {importer_code}")
                self.assertAlmostEqual(totaltrade, expected_totaltrade, places=5, msg=f"TotalTrade mismatch for {rawmaterial} {year} {importer_code}")
                print(f"compare Price: calculatete by geopolrisk: {price} value from Excel-File: {expected_price} - for {rawmaterial} {year} {importer_code}")
                self.assertAlmostEqual(price, expected_price, places=2, msg=f"Price mismatch for {rawmaterial} {year} {importer_code}")

    def test_GeoPolRisk_function(self):
        for rawmaterial in ["Nickel", "Manganese", "Graphite"]:
            df_subset = self.df_geopolrisk[self.df_geopolrisk['Raw Material'] == rawmaterial]
            for _, row in df_subset.iterrows():
                year = int(row['Year'])
                importer_code = int(row['Importer Code'])
                hhi_result = HHI(rawmaterial=rawmaterial, year=year, country=importer_code)
                trade_data_filtered = self.filter_trade_data(year, importer_code, rawmaterial)
                # Map columns for compatibility
                if not trade_data_filtered.empty:
                    trade_data_arg = self.map_trade_data_columns(trade_data_filtered)
                else:
                    # Create empty DataFrame with correct columns
                    trade_data_arg = self.map_trade_data_columns(pd.DataFrame(columns=self.df_trade.columns))
                # hscode = str(row['HS CODE'])
                import_result = importrisk(rawmaterial=rawmaterial, year=year, country=importer_code, data=trade_data_arg)

                geopol_result = GeoPolRisk(
                    Numerator=import_result[0],
                    TotalTrade=import_result[1],
                    Price=import_result[2],
                    ProdQty=hhi_result[0],
                    hhi=hhi_result[1]
                )

                score = geopol_result[0]
                cf = geopol_result[1]
                wta = geopol_result[2]
                                
                expected_score = row['GeoPolRisk Score']
                expected_cf = row['CF']
                expected_wta = row['Import Risk (WTA)']

                print("\n")
                print(f"compare GeoPolRisk Score: calculatete by geopolrisk: {score} value from Excel-File: {expected_score} - for {rawmaterial} {year} {importer_code}")
                self.assertAlmostEqual(score, expected_score, places=3, msg=f"GeoPolRisk Score mismatch for {rawmaterial} {year} {importer_code}")
                print(f"compare CF: calculatete by geopolrisk: {cf} value from Excel-File: {expected_cf} - for {rawmaterial} {year} {importer_code}")
                self.assertAlmostEqual(cf, expected_cf, places=2, msg=f"CF mismatch for {rawmaterial} {year} {importer_code}")
                print(f"compare WTA Score: calculatete by geopolrisk: {wta} value from Excel-File: {expected_wta} - for {rawmaterial} {year} {importer_code}")
                self.assertAlmostEqual(wta, expected_wta, places=3, msg=f"WTA mismatch for {rawmaterial} {year} {importer_code}")

if __name__ == "__main__":
    unittest.main()
