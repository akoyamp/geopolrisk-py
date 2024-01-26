from .__init__ import instance, logging, execute_query, DBFolder
from .utils import *
from .gprsio import company, region
import comtradeapicall as ctac
import os
from pathlib import Path
expected_headers = [
    "RefYear",
    "ReporterCode",
    "ReporterDesc",
    "PartnerCode",
    "PartnerDesc",
    "CmdCode",
    "Qty",
    "QtyUnitAbbr",
    "Cifvalue",
]


class tradedata:
    def __init__(self):
        self.database = None
        self.tradedata = None
        self.price = None
        self.tradefolder = None
        self.tradefiles = None

    def setdatabase(self,
                    database: str = None,
                    Folder: str = None):
        if database is None:
            self.tradefiles = None
            raise Exception("Must set a database!")
        elif database in ["BACI", "COMTRADE", "Company", "Other"]:
            self.database = database
        else:
            self.tradefiles = None
            raise Exception("Invalid database!")
        if database in ["Company", "Other"]:
            if Folder is None:
                raise Exception(
                    "The path to the file containing trade data has not been declared."
                    " Provide the destination folder in raw format."
                    " ex 'tradedata.tradefolder' = 'C://FOLDER/FOLDER/"
                )
            else:
                matching_files = []
                file_list = os.listdir(self.tradefolder)
                # Log each file name
                for file_name in file_list:
                    logging.info(file_name)
                    if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
                        file_path = os.path.join(self.tradefolder, file_name)
                        try:
                            # Read the Excel file into a DataFrame
                            df = pd.read_excel(file_path)

                            # Check if the DataFrame contains the expected headers
                            if all(header in df.columns for header in expected_headers):
                                matching_files.append(file_name)
                        except Exception as e:
                            logging.debug(f"Error reading {file_name}: {e}")
                            matching_files = []
                if len(matching_files) > 0:
                    self.tradefiles = matching_files
                else:
                    self.tradefiles = None
        else:
            self.tradefiles = None

    def fetchdata(self):
        if self.tradefiles != None and len(self.tradefiles) > 0:
            tempdf = pd.DataFrame(columns=expected_headers)
            for i in self.tradefiles:
                file_path = os.path.join(self.tradefolder, i)
                df = pd.read_excel(file_path).drop_duplicates()
                df = df[expected_headers]
                # concatenate dataframes
                tempdf = pd.concat([tempdf, df], axis=0)
            tempdf = tempdf.drop_duplicates()
            column_mapping = {'RefYear': 'Year',
                               'ReporterCode': 'Reporter',
                               'PartnerCode': 'Partner',
                               'CmdCode': 'HSCODE',
                               'Qty': 'QTY',
                               'Cifvalue': 'VALUE'}
            tempdf = tempdf.rename(columns=column_mapping,
                                   inplace=True)
        else:
            self.tradedata = None
            raise Exception(
                "Cannot find the trade data, check the logs."
                " Set your trade path using tradefromfile functions."
            )
        self.tradedata = tempdf

    def fetchBACI(self):
        BACI_db = DBFolder + "/BACI.db"
        statement =  "SELECT name FROM sqlite_master WHERE type='table';"
        table_names = execute_query(statement, db_path=BACI_db)
        # Initialize an empty dictionary to store DataFrames
        data_dict = {}

        # Fetch data from each table and store it in a DataFrame
        for table in table_names:
            table_name = table[0]
            query = f"SELECT * FROM {table_name};"
            
            # Fetch data into a DataFrame
            df = pd.read_sql_query(query, conn)
            
            # Store the DataFrame in the dictionary with the table name as the key
            data_dict[table_name] = df

        # Close the database connection
        conn.close()

        pass

    def tradeaggregate(self,
                       eco_unit: list = None,
                       trade: pd.DataFrame = None):
        aggregated_trade = {}
        #check if the arguments are valid and not none
        if (
        eco_unit is not None and
        isinstance(eco_unit, list)):
            for i in eco_unit:
                if isinstance(i, region):
                    country = instance.regions_list[i]
                    filtered_trade = filter_dataframe(trade, "Reporter", country)
                    result = filtered_trade.groupby('Partner')['VALUE']['QTY'].sum().reset_index()
                else:
                    result = False
            aggregated_trade[i] = result
        else:
            raise Exception("Year cannot be None!")
        return aggregated_trade


    def callapirequestV2(self, period, Ctry, resource):
        ignore, ignore2, commoditycode, country = convertCodes(resource, Ctry)
        country = str(country)
        commoditycode = str(commoditycode)
        try:
            get = ctac.previewTarifflineData(
                typeCode="C",
                freqCode="A",
                clCode="HS",
                period=period,
                reporterCode=country,
                cmdCode=commoditycode,
                flowCode="M",
                partnerCode=None,
                partner2Code=None,
                customsCode=None,
                motCode=None,
                maxRecords=500,
                format_output="JSON",
                countOnly=None,
                includeDesc=True,
            )
        except Exception as e:
            logging.debug(f"Error while calling API! {e}")
            get = None
        try:
            if get is not None or not isinstance(get, None) or len(get) == 0:
                # Duplicates are summed up (Error with COMTRADE API)
                get["Qty"] = get.groupby(["partnerCode"])["qty"].transform(sum)
                get["CifValue"] = get.groupby(["partnerCode"])["cifvalue"].transform(
                    sum
                )
                get = get.drop_duplicates(subset="partnerCode", keep="first")
                try:
                    cifvalueToT = sum(get["CifValue"].to_list())
                    totalQ = sum(get["Qty"].to_list())
                    if totalQ == 0:
                        pricecif = 0
                    else:
                        pricecif = cifvalueToT / totalQ
                except Exception as e:
                    logging.debug(f"Error while extracting cifvalue! {e}")
                    pricecif = None
            else:
                logging.debug(f"Problem with the new API call! {get}")
                get, pricecif = None, None
        except Exception as e:
            logging.debug(f"Error while extracting and combining data! {e}")
            get, pricecif = None, None

        self.tradedata = get
        self.price = pricecif
    
    def tradestatistics(self):
        df = self.tradedata

        if self.tradedata is None:
            raise Exception("Trade data not found!")
        if all(header in self.tradedata.columns for header in expected_headers):
            condition = (df["PartnerCode"] == 0) | (df["PartnerDesc"] == "World")
            df = df[~condition]
            ResourceNames = []
            for i in df["CmdCode"].tolist():
                ResourceNames.append(instance.commodity.loc[instance.commodity["HSCODE"] == i, 'RESREFID'].values[0])
            df["ResourceID"] = ResourceNames
            totaltrade = (
                df.groupby(["RefYear", "PartnerDesc", "ResourceID"])["Qty"].sum()/1000000
            )
            #Create a column in df that calculates the contribution of Qty of each ResourceID per RefYear per PartnerDesc
            for i in ResourceNames.unique():
                df["QtyContribution"] = df["Qty"] / df.groupby(["RefYear", i, "PartnerDesc"])["Qty"].transform("sum")
            #QtyContribution = df["Qty"] / df.groupby(["RefYear", "ResourceID", "PartnerDesc"])["Qty"].transform("sum")
            file_path = self.tradefolder + "/TradeTotals.txt"
            #Convert the df to excel file to the path similar to the below 'file_path'
            
            df.to_excel(self.tradefolder + "/TradeTotals.xlsx")
            
            Intro = "Import totals of each commodity to a country at a give period.\n\n"
            with open(file_path, "w") as file:
                file.write(Intro)
                file.write(totaltrade.to_string())
        else:
            logging.debug("Verify error in the previous function calls!")
        
