# Import necessary modules and functions from other files
from .__init__ import instance, logging
from typing import Iterable, Optional
import os, json
from utils import *


class Meta:
    def __init__(self, meta_data: str):
        self.data = self.Load_Yaml(meta_data)
        if self.data is not None:
            self._initialize_attributes()
        else:
            raise UnboundLocalError

    def _initialize_attributes(self):
        self.Tables = self.data.get("Tables", [])
        self.regions_list = self.data.get("regionslist", {})
        self.Output = self.data.get("Output", "")
        self.Database = self.data.get("Database", "")
        self.BACI = self.data.get("BACI", "")
        self.BACIcodes = self.data.get("BACIcodes", {})
        self.COMTRADEcodes = self.data.get("COMTRADEcodes", {})

    def _load_mining_data(self):
        # Verify that the file exists else input the correct file path
        db = os.path.join(self.dbFolder, self.Database)
        if not os.path.isfile(db):
            folder_path = input("The file doesn't exist. Please enter a folder path: ")
        # Check if the database exists and fetch the required tables
        try:
            result = execute_query(
                "SELECT name FROM sqlite_master WHERE type='table';", db_path=db
            )
            table_names = [row[0] for row in result]
        except Exception as e:
            print(f"Unable to verify if the database contains the required tables {e}")
            raise FileNotFoundError

        # check if all the tables in the list are present in the database
        missingTables = []
        for table_name in Tables:
            if table_name not in table_names:
                missingTables.append(table_name)
            else:
                pass

        # If there are missing tables, raise an error
        if len(missingTables) > 0:
            print(
                f"The following tables are missing from the database: {missingTables}"
            )
        else:
            pass

        # Function to extract the tables into a dictionary
        def extract_tables_to_df(db_path, table_names):
            # Create a dictionary to store the extracted tables
            tables = {}

            # Connect to the database
            conn = sqlite3.connect(db_path)

            # Loop through the table names and extract each table as a DataFrame
            for table_name in table_names:
                query = f"SELECT * FROM {table_name}"
                table_df = pd.read_sql_query(query, conn)

                # Add the table DataFrame to the tables dictionary with the table name as the key
                tables[table_name] = table_df

            # Close the database connection
            conn.close()

            # Return the tables dictionary
            return tables

        # Extract the tables into a dictionary
        try:
            tables = extract_tables_to_df(db, Tables)
        except Exception as e:
            print(f"Could not extract the tables {e}")

        production = tables
        reporter = tables["Country_ISO"]
        price = tables["Price"]
        commodity = tables["commodityHS"]
        wgi = tables["WGI"]
        regionslist = regions_list


# Define a class called 'company'
class company:
    def __init__(self, name):
        self.name = name


# Define a class called 'region'
class region:
    def __init__(self, name: list = None):
        self.name = name

    @classmethod
    def set_region(self, inst):
        # Validate region names against a DataFrame 'instance.reporter'
        for value in inst.name:
            if (
                isinstance(value, str)
                and value not in instance.reporter["Country"].tolist()
            ):
                raise Exception("Invalid country in region! Please verify the inputs.")
            else:
                instance.regionslist[inst] = inst.name
                return True


# Define a class called 'Data'
class Data:
    def __init__(
        self,
        year: list = None,
        resource: list = None,
        eco_unit: list = None,
        recycling_rate: list = None,
        sub_index: list = None,
        data: Optional[Iterable[dict]] = None,
        project_name: Optional[str] = None,
    ):
        # Initialize data attributes
        self.data = data if data is not None else {}
        self.inputs = {
            "year": year,
            "resource": resource,
            "eco_unit": eco_unit,
            "recycling_rate": recycling_rate,
            "sub_index": sub_index,
            "hs_code": [],
            "iso": [],
        }
        self.results = {
            "hhi": [],
            "wta": [],
            "scenario": [],
            "geopolrisk": [],
            "geopolrisk_BCS": [],
            "geopolrisk_WCS": [],
            "price": [],
            "CF": [],
            "log_ref": [],
        }
        self.project_name = project_name
        self.datafolder = None
        self.datafiles = []
        # Define valid data types for each input
        self.valid_data_types = {
            "year": int,
            "resource": str,
            "eco_unit": (company, region, str),
            "recycling_rate": float,
            "sub_index": (float, type(None)),
        }

    # Retrieve the Harmonized System (HS) code from the commodity table
    def get_hs(self, resource):
        """Get the Harmonized System (HS) code from the commodity table."""
        return instance.commodity.loc[
            instance.commodity["RESREFID"] == resource, "HSCODE"
        ].tolist()[0]

    # Retrieve the resource name from the commodity table
    def get_resource(self, hs_code):
        """Get the resource name from the commodity table."""
        return instance.commodity.loc[
            instance.commodity["HSCODE"] == hs_code, "RESREFID"
        ].tolist()[0]

    # Retrieve the ISO code from the country table
    def get_ISO(self, country):
        """Get the ISO code from the country table."""
        return instance.reporter.loc[
            instance.reporter["Country"] == country, "ISO"
        ].tolist()[0]

    # Retrieve the country name from the country table
    def get_Country(self, ISO):
        """Get the country name from the country table."""
        return instance.reporter.loc[
            instance.reporter["ISO"] == ISO, "Country"
        ].tolist()[0]

    # Process input data and perform validation
    def process_inputs(self):
        if self.data and self.project_name:
            inputs = self.data.get(self.project_name, {})
            self.inputs = inputs if len(inputs) != 0 else self.inputs
            for key, value in inputs.items():
                if not isinstance(value, list):
                    logging.debug(f"Invalid input '{key}' type! Please provide a list.")
                    raise Exception("Invalid input type! Please provide a list.")

                valid_data_type = self.valid_data_types.get(key.lower())
                if valid_data_type is None:
                    logging.debug(f"Unknown input '{key}'! Please check the input key.")
                    raise Exception("Unknown input! Please check the input key.")

                for element in value:
                    if not isinstance(element, valid_data_type):
                        logging.debug(
                            f"Invalid input '{key}' value! Please verify the inputs."
                        )
                        raise Exception(
                            "Invalid input value! Please verify the inputs."
                        )
                else:
                    # All elements in the list are of the correct data type
                    if key == "eco_unit":
                        if not all(
                            element in instance.regionslist.keys() for element in value
                        ):
                            logging.debug(
                                "Invalid 'eco_unit' values! Please verify the inputs."
                            )
                    elif key == "year":
                        if not all(2002 <= element <= 2021 for element in value):
                            logging.debug(
                                "Invalid 'year' values! Please verify the inputs."
                            )
                    elif key == "resource":
                        commodity_column = instance.commodity["RESREFID"]
                        if not all(
                            element in commodity_column.tolist() for element in value
                        ):
                            logging.debug(
                                "Invalid 'resource' values! Please verify the inputs."
                            )
            for i in self.data[self.project_name]["resource"]:
                # if hs_code not in key of self.project_name then add it
                if "hs_code" not in self.data[self.project_name].keys():
                    self.data[self.project_name]["hs_code"] = []
                try:
                    self.data[self.project_name]["hs_code"].append(self.get_hs(i))
                except:
                    logging.debug(
                        "Invalid 'resource' values! Please verify the inputs."
                    )
                    raise Exception(
                        "Invalid 'resource' values! Please verify the inputs."
                    )
            for i in self.data[self.project_name]["eco_unit"]:
                if "iso" not in self.data[self.project_name].keys():
                    self.data[self.project_name]["iso"] = []
                if not isinstance(i, company) and not isinstance(i, region):
                    try:
                        self.data[self.project_name]["iso"].append(self.get_ISO(i))
                    except:
                        logging.debug(
                            "Invalid 'eco_unit' values! Please verify the inputs."
                        )
                        raise Exception(
                            "Invalid 'eco_unit' values! Please verify the inputs."
                        )
                else:
                    logging.debug(
                        "Invalid 'eco_unit' values! Please verify the inputs."
                    )
                    raise Exception(
                        "Invalid 'eco_unit' values! Please verify the inputs."
                    )

    def setfolder(self, datapath=None):
        if self.datafolder is None:
            try:
                home_dir = os.path.expanduser("~")
                self.datafolder = os.path.join(home_dir, datapath)
            except Exception as e:
                logging.debug(e)
                raise Exception(
                    "The path to the folder containing data files has not been declared."
                    " Provide the destination folder in raw format."
                    " ex 'datahandler.datafolder' = 'C://FOLDER/FOLDER/"
                )

    def fetch_prjdatafiles(self):
        matching_files = []
        file_list = os.listdir(self.datafolder)
        for file_name in file_list:
            # Log each file name
            logging.info(file_name)
            if file_name.endswith(".json"):
                file_path = os.path.join(self.datafolder, file_name)
                try:
                    # Read and parse the JSON file
                    with open(file_path, "r") as json_file:
                        json_data = json.load(json_file)

                    # Check if the JSON data has the expected format (modify as needed)
                    if "project_name" in json_data and "data" in json_data:
                        matching_files.append(
                            {"file_name": file_name, "json_data": json_data}
                        )
                except Exception as e:
                    logging.debug(f"Error processing {file_name}: {e}")
                    matching_files = []
            else:
                logging.debug(f"File {file_name} is not a JSON file.")
                matching_files = []
        return matching_files

    def write(self):
        Data = {}
        Data[self.project_name] = self.inputs.update(self.results)
        if self.datafolder != None:
            raise Exception("The database folder is not defined yet!")
        filename = self.datafolder + "records.json"
        if os.path.isfile(filename):
            # If the JSON file exists, read its contents
            with open(filename, "r") as json_file:
                existing_data = json.load(json_file)

            # Ensure that the existing data is a dictionary
            if not isinstance(existing_data, dict):
                raise Exception(
                    "Existing JSON data is not in the expected format (dictionary)."
                )

            # Append the new data to the existing dictionary
            existing_data.update(Data)

            # Write the updated data back to the file
            with open(filename, "w") as json_file:
                json.dump(existing_data, json_file, indent=4)
        else:
            # If the JSON file doesn't exist, create a new one with the provided data
            with open(filename, "w") as json_file:
                json.dump(self.data, json_file, indent=4)
