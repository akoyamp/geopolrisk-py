# Databases folder

This folder contains the background data and user input templates required for the operational implementation of the GeoPolRisk method.

The contents of this folder are structured exclusively for use within the `geopolrisk-py` library and are not intended to function as standalone general-purpose databases.

## Folder contents

The folder may contain:

- Structured background databases required for the GeoPolRisk calculations (e.g., production data, trade data, governance indicators).
- The Excel input template used for company-specific supply risk assessments.

## Prepare the Excel File

The first time the package is run, an Excel file is automatically copied to a folder located at:

```

Documents/geopolrisk/databases

```

The typical path on a Windows system will look like:

```

C:\Users\your_username\Documents\geopolrisk\databases

```

The Excel file contains the following columns:

- **Metal**: Use the name of the metal or raw material that corresponds to the commodity. Please refer to the documentation for the correct nomenclature.
- **Country of Origin**: Use either the ISO country name or the ISO 3-digit code for the country from which the commodity is imported.
- **Quantity (kg)**: Quantity of the imported commodity in kilograms.
- **Value (USD)**: Value of the imported commodity in US dollars.
- **Year**: Reference year.
- **Additional Notes**: Any internal notes or comments (these are not used in the calculation).

The completed Excel file is used as input for company-specific GeoPolRisk calculations.

## Third-party data sources and licenses

The GeoPolRisk method relies on several external data sources for mining production, international trade, and governance indicators. These data sources are provided by third parties and are subject to their respective licenses and terms of use, as defined by the original data providers.

All databases distributed within this folder are structured specifically for the operational implementation of the GeoPolRisk method. They are provided solely for use within this methodological context and are not intended to serve as standalone general-purpose data repositories.

### World Mining Data (WMD)

Mining production statistics are based on *World Mining Data*, published by the Austrian Federal Ministry of Finance. The production data included in this package are derived from World Mining Data and have been processed and structured specifically for use within the GeoPolRisk methodology. They do not constitute or claim to represent the official World Mining Data publication.

Licensing and terms of use:
[World Mining Data – Austrian Federal Ministry of Finance](https://www.bmf.gv.at/en/topics/mining/mineral-resources-policy/wmd.html)

### BACI international trade database

International trade data are sourced from the BACI database developed by CEPII and derived from UN Comtrade data. BACI is distributed under the **Etalab Open License 2.0**, as specified by CEPII:

[BACI database – CEPII](https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37)

### Worldwide Governance Indicators (WGI)

Governance indicators are obtained from the Worldwide Governance Indicators project of the World Bank. These data are licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license:

[Worldwide Governance Indicators – World Bank](https://data360.worldbank.org/en/dataset/WB_WGI)
