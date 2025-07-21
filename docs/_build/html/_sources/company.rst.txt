Company-specific risk assessment
====================================

Prepare the Excel File
----------------------

The first time the package is run, an Excel file is automatically copied to a folder located at:

``Documents/geopolrisk/databases``

The typical path on a Windows system will look like:

``C:\Users\your_username\Documents\geopolrisk\databases``

The Excel file contains the following columns:

- **Metal**: Use the name of the metal or raw material that corresponds to the commodity. Please refer to the :ref:`References` section for the correct nomenclature.
- **Country of Origin**: Use either the ISO country name or the ISO 3-digit code for the country from which the commodity is imported.
- **Quantity (kg)**: Quantity of the imported commodity in kilograms.
- **Value (USD)**: Value of the imported commodity in US dollars.
- **Year**: Reference year.
- **Additional Notes**: Any internal notes or comments (these are not used in the calculation).

There is no master function for calculating the GeoPolRisk values based on company-level trade data. The calculation must be performed step-by-step.

Import the Functions
--------------------

.. code-block:: python

   from geopolrisk.assessment.core import HHI, importrisk_company, GeoPolRisk

First, use the `HHI` function to calculate the concentration of production for a given metal and year.

.. code-block:: python

   ProductionQuantity, hhi = HHI("Nickel", 2022, "Company")

The function takes the following parameters:

- ``RawMaterial``: The raw material name (e.g., ``"Nickel"``). This must match the nomenclature used in the Excel file.
- ``Year``: The reference year (e.g., ``2022``).
- ``Country``: Use the string ``"Company"`` to indicate company-level assessment instead of a country.

Next, use the ``importrisk_company`` function to retrieve the company's import risk for the specified raw material and year.

.. code-block:: python

   Num_Company, TotalTrade_Company, Price_Company = importrisk_company("Nickel", 2022)

Then calculate the GeoPolRisk values:

.. code-block:: python

   Values_Company = GeoPolRisk(
       Num_Company,
       TotalTrade_Company,
       Price_Company,
       ProductionQuantity,
       hhi
   )

Create the Output DataFrame
---------------------------

Use the ``createresultsdf`` utility to structure the results in a pandas DataFrame:

.. code-block:: python

   from geopolrisk.assessment.utils import createresultsdf

   df = createresultsdf()
   df["DBID"] = ["Company"]
   df["Country [Economic Entity]"] = ["Company"]
   df["Raw Material"] = ["Nickel"]
   df["Year"] = ["2022"]
   df["GeoPolRisk Score"] = [Values_Company[0]]
   df["GeoPolRisk Characterization Factor [eq. Kg-Cu/Kg]"] = [Values_Company[1]]
   df["HHI"] = [hhi]
   df["Import Risk"] = [Values_Company[2]]
   df["Price"] = [Price_Company]
