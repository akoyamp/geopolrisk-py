Methods
=======

Methods: database.py
--------------------

This module provides a class for managing the database connection and executing SQL queries. It includes a method called ``execute_query``:

.. code-block:: python

   execute_query(query, db_path="", params=None, retries=5, delay=0.1)

Arguments:

- ``query`` (str): The SQL query to execute.
- ``db_path`` (str): The path to the database file.
- ``params`` (tuple): Optional parameters for the SQL query.
- ``retries`` (int): Number of times to retry the query in case of failure.
- ``delay`` (float): Delay in seconds between retries.

Returns:

- ``list``: A list of tuples containing the results of the query (only if the query is ``SELECT``).

This module also includes a database class that is instantiated within the module as ``databases``. The class extracts all the library databases from the ``geopolrisk/lib/`` directory and provides methods to access them.

The class creates folders in the user's Documents directory to store the databases and logs:

- Databases: ``Documents/geopolrisk/databases/``
- Outputs: ``Documents/geopolrisk/output/``
- Logs: ``Documents/geopolrisk/logs/``

The class variables include:

- ``production``: Contains the entire world mining database as a DataFrame.
- ``baci_trade``: BACI trade database as a single DataFrame, filtered for model-relevant commodities.
- ``wgi``: World Governance Indicator for Political Stability and Absence of Violence as a DataFrame.
- ``regionslist``: A dictionary storing any user-defined custom regions (see ``regions`` function in ``utils.py``).

This module also includes a logging setup for errors and debugging.


Methods: utils.py
-----------------

This module provides utility functions for the GeoPolRisk method, including:

- ``replace_func(x)``: Replaces specific values in a DataFrame column that contain NaN with 0.

**Function: cvtcountry**

.. code-block:: python

   cvtcountry(country, type="ISO")

Converts a country name or code to its ISO 3-digit format or ISO name.

Arguments:

- ``country`` (str or int): The value to convert.
- ``type`` (str): Either ``"ISO"`` for 3-digit format or ``"Name"`` for ISO name.

Returns:
- Converted country name or code.


**Function: getbacidata**

.. code-block:: python

   getbacidata(period: int, country: int, rawmaterial: str, data)

.. admonition:: About the method

   Retrieves BACI trade data for a given year, country, and raw material from the provided DataFrame.

Arguments:

- ``period`` (int): The year of interest.
- ``country`` (int): The ISO 3-digit code of the country.
- ``rawmaterial`` (str): The raw material to retrieve data for.
- ``data`` (DataFrame): The DataFrame containing BACI trade data.


**Function: aggregateTrade**

.. code-block:: python

   aggregateTrade(period: int, country: list, rawmaterial: str, data)

.. admonition:: About the method

   Aggregates BACI trade data for a list of countries, a specific raw material, and year.
   Returns values used to compute GeoPolRisk: numerator, quantity, and average price.

Arguments:

- ``period`` (int): The year of interest.
- ``country`` (list): List of ISO 3-digit country codes.
- ``rawmaterial`` (str): The raw material.
- ``data`` (DataFrame): The DataFrame containing BACI trade data.

Returns:

- ``SUMNUM`` (float): Numerator for GeoPolRisk calculation.
- ``SUMQTY`` (float): Total trade quantity.
- ``Price`` (float): Average traded price.


**Function: transformdata**

.. code-block:: python

   transformdata(file_name=None, excel_sheet_name=None, mode="prod")

.. admonition:: About the method

   Transforms company trade data into the required format. Input must follow the template in ``geopolrisk/lib/`` or a similar structure.

Arguments:

- ``file_name`` (str): Full path or filename of the Excel file.
- ``excel_sheet_name`` (str): The Excel sheet name.
- ``mode`` (str): Use ``"test"`` to load from the test path.

Returns:

- ``DataFrame``: Cleaned and structured trade data.


**Function: getProd**

.. code-block:: python

   getProd(rawmaterial)

.. admonition:: About the method

   Retrieves production data for a specific raw material from the database.

Arguments:

- ``rawmaterial`` (str): The raw material to retrieve data for.

Returns:

- ``DataFrame``: Production data.


**Function: regions**

.. code-block:: python

   regions(*args)

.. admonition:: About the method

   Allows the user to define custom regions. Should be called early in the workflow to ensure proper use throughout.

Arguments:

- ``*args``: A dictionary of region names (keys) and list of countries (values).

.. admonition:: Example usage

   ``NAFTA`` includes Canada, Mexico, and the USA. ``RER`` corresponds to ecoinvent's European region using ISO codes.

.. code-block:: python

   regions_dict = {
       "NAFTA": ["Canada", "Mexico", "USA"],
       "RER": [
           20, 8, 40, 70, 58, 100, 112, 757, 891, 203, 280, 208, 233, 724,
           246, 251, 826, 292, 300, 191, 348, 372, 352, 380, 440, 442, 428,
           498, 499, 807, 470, 528, 579, 616, 620, 642, 688, 643, 752, 705,
           703, 674, 804
       ]
   }

Other functions such as ``Mapping()`` and ``mapped_baci()`` are used to group multiple HS codes into single raw materials. See the references section for details.

.. note::
   The ``mapped_baci()`` function returns a DataFrame containing the mapped raw materials, countries, years, and aggregated trade values.

Methods: core.py
-----------------

This module contains the core functionality for calculating the GeoPolRisk method.

**Function: HHI**

.. code-block:: python

   HHI(rawmaterial: str, year: int, country: Union[str, int])

.. admonition:: About the method

   Calculates the HHI for a given raw material, year, and country.  
   The HHI is a measure of the concentration of production for a specific raw material in a given country and year.  
   See the 'background' section for more details.

Arguments:

- ``rawmaterial`` (str): The raw material to calculate the HHI for.
- ``year`` (int): The year of interest.
- ``country`` (Union[str, int]): The ISO 3-digit code or name of the country.

Returns:

- ``ProdQty`` (float): The production quantity of the raw material.
- ``hhi`` (float): The HHI value normalized between 0 (no concentration) and 1 (maximum concentration).


**Function: importrisk**

.. code-block:: python

   importrisk(rawmaterial: str, year: int, country: str, data)

.. admonition:: About the method

   Calculates the import risk for a given raw material, year, and country using mapped BACI trade data.

Arguments:

- ``rawmaterial`` (str): The raw material to evaluate.
- ``year`` (int): The year of interest.
- ``country`` (str): The ISO 3-digit code of the country.
- ``data`` (DataFrame): The mapped BACI trade data.

Returns:

- ``Numerator`` (float): The numerator of the import risk calculation.
- ``TotalTrade`` (float): Total traded quantity.
- ``Price`` (float): Average traded price.


**Function: importrisk_company**

.. code-block:: python

   importrisk_company(rawmaterial: str, year: int, file_name=None, excel_sheet_name=None, mode="prod")

.. admonition:: About the method

   Calculates the import risk for a given raw material and year using company-specific trade data.

Arguments:

- ``rawmaterial`` (str): The raw material to evaluate.
- ``year`` (int): The year of interest.
- ``file_name`` (str): Full path or name of the Excel file.
- ``excel_sheet_name`` (str): Name of the Excel sheet.
- ``mode`` (str): Optional. Set to ``"test"`` to use test input location.

Returns:

- ``Numerator`` (float): The numerator of the import risk calculation.
- ``TotalTrade`` (float): Total traded quantity.
- ``Price`` (float): Average traded price.


**Function: GeoPolRisk**

.. code-block:: python

   GeoPolRisk(Numerator, TotalTrade, Price, ProdQty, hhi)

.. admonition:: About the method

   Calculates the GeoPolRisk score and CF based on import risk, production quantity, and HHI.

Arguments:

- ``Numerator`` (float): Numerator from the import risk calculation.
- ``TotalTrade`` (float): Total trade quantity.
- ``Price`` (float): Average traded price.
- ``ProdQty`` (float): Production quantity.
- ``hhi`` (float): Herfindahl-Hirschman Index value.

Returns:

- ``Score`` (float): GeoPolRisk score normalized between 0 (no risk) and 1 (maximum risk).
- ``CF`` (float): Characterization factor for the 'Geopolitical Supply Risk' indicator. Computed as the score × price, normalized by copper.
- ``WTA`` (float): Weighted trade average. Represents import risk, the second component of GeoPolRisk.

Methods: main.py
-----------------

**Function: gprs_calc**

.. code-block:: python

   gprs_calc(period: list, country: list, rawmaterial: list, region_dict={})

.. admonition:: About the method

   A one-stop method to calculate the GeoPolRisk score and CFs for a list of raw materials, countries, and years. This function also allows users to define custom regions by providing a dictionary.

Arguments:

- ``period`` (list): List of years to calculate GeoPolRisk for.
- ``country`` (list): List of ISO 3-digit country codes.
- ``rawmaterial`` (list): List of raw materials to evaluate.
- ``region_dict`` (dict): Optional. A dictionary of custom regions. Keys are region names, values are lists of ISO 3-digit country codes. See the ``regions`` function in ``utils.py`` for more details.

Returns:

- ``DataFrame``: A DataFrame containing the GeoPolRisk scores and CFs for each raw material, country, and year.  
  The DataFrame includes columns for raw material, country, year, GeoPolRisk score, CF, and weighted trade average (WTA).  
  See the references section for details on the DataFrame structure.
