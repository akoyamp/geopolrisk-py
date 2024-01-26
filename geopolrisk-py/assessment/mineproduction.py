from .__init__ import instance, logging, execute_query
from .utils import *

# Dictionary containing all the dataframes of the tables in the database
production = instance.production


class productiondata:
    def __init__(self):
        self.prod = None
        self.HHI = None
        self.prodQty = None

    # Function to fetch the dataframe of the resource
    def get_prod_df(self, resource_id):
        # Fetcth the particular dataframe from the dictionary
        self.prod = production[resource_id].fillna(0)
        # Extract the list of countries from the dataframe
        self.countries = self.prod["Country"].tolist()
        # Extract the column names from the dataframe
        columns = self.prod.columns.to_list()
        v2R = ["Country", "ISO"]
        # List of years in the database for the particular resource
        Prod_Year = list(filter(lambda x: x not in v2R, columns))
        # Converting the values to integers
        self.year = [int(i) for i in Prod_Year]

    @vfy_arg(int)
    def get_hhi(self, year):
        # Verify if the resource dataframe is available
        if self.prod is None:
            logging.debug("Resource dataframe missing! Call prod df")
            raise Exception(
                "Resource dataframe not available!\
                             Call get_prod_df first"
            )
        # Verify if the input year is available for the particular resource
        if year not in self.year:
            logging.debug("Input year not available in database! {}".format(year))
            raise Exception("Year not found!")

        # Get the production quantity values for the particular year
        try:
            ListV = self.prod[str(year)].tolist()
            # Verify if there was an error in removing values in the previous function
            if len(self.countries) != len(ListV):
                logging.debug("Error while processing column data")
                raise Exception("Error in processing column data")
        except Exception as e:
            logging.debug(f"Error while getting production data values {e}")

        # Calculate the HHI for the particular year
        try:
            temp = replace_values(ListV, "^", 0)
            temp = [float(i) for i in temp]
            DeNom = sum(temp)
            Nom = sum([j[0] * j[1] for j in zip(temp, temp)])
            try:
                self.HHI = round(Nom / (DeNom * DeNom), 3)
            except Exception as e:
                self.HHI = 0
        except:
            logging.debug("Error calculating the HHI for {}".format(year))

    def get_prodQuantity(self, CNTRY, year):
        # Verify if the resource dataframe is available
        if self.prod is None:
            logging.debug("Resource dataframe missing! Call prod df")
            raise Exception(
                "Resource dataframe not available!\
                             Call get_prod_df first"
            )

        # Function to fetch production quantity
        def totalprodqty(country):
            prodQty = None
            # Verifying if country mines the particular resource
            if country not in self.countries:
                prodQty = 0
            else:
                try:
                    # If the country exist, extract the index
                    index = self.countries.index(country)
                    try:
                        ListV = self.prod[str(year)].tolist()
                        # Verify if there was an error in removing values in the previous function
                        if len(self.countries) != len(ListV):
                            logging.debug("Error while processing column data")
                            raise Exception("Error in processing column data")
                    except Exception as e:
                        logging.debug(f"Error while getting production data values {e}")
                    # Get the production quantity of the resource in that country for that year
                    prodQty = ListV[index]
                except Exception as e:
                    logging.debug("Error in fetching production quantity {}".format(e))
            return prodQty

        # Check if the input is List, if yes process it
        if isinstance(CNTRY, list):
            prodQty = []
            for i in CNTRY:
                Qty = totalprodqty(i)
                if Qty is None:
                    logging.debug(
                        "Error in fetching data!\
                                  {} return None".format(
                            i
                        )
                    )
                    raise Exception("Error in calculating production quantity!")
                else:
                    prodQty.append(Qty)
            self.prodQty = sum(prodQty)
        elif isinstance(CNTRY, str):
            self.prodQty = totalprodqty(CNTRY)
        else:
            logging.debug(f"Production Quantity error! unknown key {CNTRY}")
            raise Exception("Input must be a string! Unknown format!")

    def getallprod(self, resource, country, year):
        if (
            isinstance(resource, str)
            and isinstance(year, int)
            and isinstance(country, list)
            or isinstance(country, str)
        ):
            self.get_prod_df(resource)
            self.get_hhi(year)
            self.get_prodQuantity(country, year)
            Qty = self.prodQty
            HHI = self.HHI
        else:
            logging.debug("Invalid inputs!")
            raise Exception("Invalid argument type!")
        return (HHI, Qty)
