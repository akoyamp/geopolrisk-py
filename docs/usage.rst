.. _Usage:

Usage
=====

**General Usage**
-----------------

With the method in the :ref:`main.py` module, ``gprs_calc``, it is possible to calculate all values of the GeoPolRisk method in one go.  
See the :ref:`Methods` section of the documentation for more details on the arguments.

The :ref:`utils.py` module also provides a helper function to list all raw materials available for assessment.  
``gprs_calc`` takes in three main inputs as lists: raw materials, years, and countries.

.. code-block:: python

   from geopolrisk.assessment.utils import default_rmlist
   rawmaterials_list = default_rmlist()

.. admonition:: Default Raw Materials

   The function ``default_rmlist`` returns the list of all raw materials available in the library for assessment.

.. code-block:: python

   from geopolrisk.assessment.main import gprs_calc

   year_list = [2019, 2020, 2021, 2022]  # Currently limited to 2022 (GeoPolRisk-py V2)
   country_list = ["China", "Germany", 842, 36]  # Countries can be given as names or ISO 3-digit codes

   gprs_calc(year_list, country_list, rawmaterials_list)

.. admonition:: About the Code

   A single aggregate function performs all calculations and exports the results as an Excel file.  
   Inputs include a list of years, countries, and raw materials. You may also optionally define regions via a dictionary.

   - Raw materials should be names like ``"Cobalt"``, ``"Lithium"``, etc.  
   - Countries can be passed as names like ``"Japan"``, or numeric ISO 3-digit codes like ``250``.

   The output Excel file is saved in the ``Documents/geopolrisk/output/`` folder of the user's system.
   Also, the results are stored in a SQLite3 database in the same directory as the Excel file.

   **Output columns:**

   - ``DBID``: An internal ID for SQL reference
   - ``Country [Economic Entity]``: Country name
   - ``Raw Material``: The name of the raw material
   - ``Year``: The year of assessment
   - ``GeoPolRisk Score``: The dimensionless supply risk score (see :ref:`Background` section)
   - ``GeoPolRisk Characterization Factor [eq. kg-Cu/kg]``: CF to use in LCA for the raw material
   - ``HHI``: Herfindahl-Hirschman Index of production concentration
   - ``Import Risk``: Weighted import share based on political stability (see :ref:`Background` section)
   - ``Price``: Average bilateral traded price of the raw material


**Regional Level Assessment**
-----------------------------

There are several ways to calculate values using the GeoPolRisk method, including at the regional level.  
The ``regions`` function in the ``utils.py`` module allows users to define custom regions using a dictionary.

You can use the ``gprs_calc`` function in the ``main.py`` module in the same way as described in the General Usage section, with the addition of the ``region_dict`` parameter.

.. code-block:: python

   myregiondict = {
       "West Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "Belgium", "Netherlands", "Luxembourg"]
   }

   rawmaterials_list = ["Nickel", "Cobalt", "Manganese"]
   year_list = [2019, 2020, 2021, 2022]
   country_list = ["West Europe", "China", "India"]

   from geopolrisk.assessment.main import gprs_calc
   gprs_calc(year_list, country_list, rawmaterials_list, region_dict=myregiondict)

.. admonition:: About the Code

   Similar to the general usage of ``gprs_calc``, this call generates an Excel output file and stored in the SQLite3 database.  
