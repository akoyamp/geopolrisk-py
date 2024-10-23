---
title: "geopolrisk-py: A Python-Based Library to Operationalize the Geopolitical Supply Risk Method for use in Life Cycle Assessment and Comparative Risk Assessment"
tags:
  - Criticality
  - LCA
  - Import
  - Raw material
  - Market concentration
  - Abiotic Resources
authors:
  - name: Anish Koyamparambath
    orcid: 0000-0003-0839-0552
    corresponding: true
    affiliation: 1
  - name: Thomas Schraml
    affiliation: 2
  - name: Christoph Helbig
    orcid: 0000-0001-6709-373X
    affiliation: 2
  - name: Guido Sonnemann
    orcid: 0000-0003-2581-1910
    affiliation: 1

affiliations:
  - name: Université de Bordeaux, CNRS, Bordeaux INP, ISM, UMR 5255, 33400 Talence, France
    index: 1
  - name: Ecological Resource Technology, University of Bayreuth, Universitaetsstr. 30, 95447 Bayreuth, Germany
    index: 2
date: 21 October 2024
bibliography: paper.bib
aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
aas-journal: The Journal of Open Source Software.
---

# Summary

The Geopolitical Supply Risk (GeoPolRisk) method assesses raw material criticality in Life Cycle Assessment, complementing traditional resource and environmental impact indicators. It is also applied for comparative risk assessment. However, calculating values for the GeoPolRisk method, such as characterization factors for the Geopolitical Supply Risk indicator and the supply risk score for comparative assessment, can be complex. To address this, the `geopolrisk-py` library has been developed to operationalize the method, simplifying the calculation process. This library processes data inputs like raw material names, countries, and years, making it more accessible. A notable feature is its ability to serve as a company-specific supply risk assessment tool. Future development will include integrating an uncertainty model and additional modules for complete compatibility with Brightway 2.5, further enhancing functionality and usability.

# The GeoPolRisk Method

The GeoPolRisk method is an import-based indicator [@Gemechu2015] to integrate the criticality of raw materials into the Area of Protection ‘natural resources’, as proposed by [@Sonnemann2015]. It is designed to evaluate the supply risk of importing raw material from a trade (country, trade block, region, group of countries, or company/organization) perspective during a specific period. Since its inception, the method has evolved, incorporating several components of resource criticality [@Cimprich2019]. HHIA is the Herfindahl-Hirschman index for raw material “A” calculated as the sum of the squared production shares of all the countries producing raw material “A”. The GeoPolRisk method weights the import (“$f_Aic$”) of raw material A to economic unit “c” from “i” with the political (in-)stability indicator of the exporting country (“$g_i$”). “$F_Ac$” is the total imports to the entity in assessment, and _pAc_ is the domestic production of raw material A in entity c. $p'$ represents the yearly average market price of the raw material in US dollars per kilogram of raw material. The _GeoPolRisk MidpointAc,_ as presented in **Equation 1**_,_ has units as US dollars per kilogram of raw material “A” consumed (USD/kgA) [@Santillan-Saldivar2022]. The values for the Geopolitical Supply Risk Potential (GSP) are obtained by dividing $GeoPolRisk midpoint_Ac$ with the average GeoPolRisk midpoint of copper for the countries over 5 years (2017 to 2020) as shown in **Equation 2**. where ‘A’ represents the raw material, ‘c’ represents an economic unit, ‘t’ refers to the time period (year) [@Koyamparambath2024]. The _Geopolitical Supply Risk Potential_ has units of kg_Cu-eq per $kg_A$.
(1) $GeoPolRisk Midpoint CF_Ac= HHI_A*∑_i((g_i*f_Aic)/( p_Ac+F_Ac )) * p'$ 

(2) $Geopolitical Supply Risk Potential (GSP)=  GeoPolRisk midpoint_Act/GeoPolRisk midpoint _copper $

# Statement of Need

The method consists of three main components: (1) the evaluation of the concentration of global mine production using the normalized Herfindahl-Hirschman index [@Rhoades1993TheHI], (2) the weighting of a raw material’s import share to an economic unit by the political stability score of its origin, and (3) the yearly average traded price of the raw material. The first two components provide a supply risk score, which can be used for comparative risk assessment, while the third component combined with the other two, introduces a characterization factor, GSP, for Life Cycle Assessment to evaluate the supply risk of abiotic resources from an “outside-in” perspective [@Koyamparambath2024] [@Santillan-Saldivar2022]. The GeoPolRisk method is suggested by initiatives such as Global Guidance for Life Cycle Impact Assessment Indicators and Methods, a task force hosted by the United Nations Environmental Program [@Berger2020] and is recommended by the ORIENTING project [@Hackenhaar2022]. It is also recognized by the International Round Table on Materials Criticality [@Schrijvers2020].

Despite its benefits, broader applications of the GeoPolRisk method, especially for multiple raw materials or in generating characterization factors, are limited due to the complexity of its calculation [@Santillan-Saldivar2021]. The ORIENTING project has highlighted this complexity in its reports [@Bachmann2021] [@Hackenhaar2022], and Santillán-Saldivar et al. noted that an automated calculation tool could significantly enhance the method's practical applicability [@Santillan-Saldivar2021]. By using this library, the characterization factors for 46 raw materials in 38 OECD countries have been generated [@Koyamparambath2024]. Integrating this library into LCA tools like Brightway [@Mutel2017], a widely used open-source Python-based LCA software, could further streamline the implementation of the GeoPolRisk method into LCA. Such integration could address current limitations by aligning the methodology with intermediate flows [@Bachmann2021] [@Mancini2016] and enabling the calculation of supply risk CFs along the supply chain [@Helbig2016] [@Koyamparambath2024] [@Siddhantakar2023].

Beyond LCA applications, the GeoPolRisk method can be used as a comparative risk assessment tool for companies and organizations [@Koyamparambath2021]. With an automated calculation tool, users can input their specific supply mix to calculate tailored supply risk scores. This feature can benefit companies seeking to analyze different supply risk scenarios based on their unique supply chains and compare their risk with national averages.

# Features of the `geopolrisk-py` Library

The *geopolrisk-py* library is organized into four modules: `database.py`, `core.py`, `main.py`, and `utils.py`, each with specific roles to facilitate the calculation of the GeoPolRisk method.

1. **database.py**: This module is responsible for loading all the essential background data required for the library’s operations. The necessary data includes mining production data (from world mining data) [@FMRA2023], trade data (from BACI for past years) [@cepii_baci_2024], and governance indicators (from the World Bank) [@WorldBank2024]. These datasets are stored in a SQLite3 database, which is updated annually and available in the repository. Upon installation, the library sets up a folder in the Document folder in the user's home directory with three subfolders: 
   - **databases**: Users should place the downloaded background database here.
   - **output**: This folder stores the SQLite3 database and Excel output files generated after calculations.
   - **logs**: For debugging errors encountered during the process.

2. **core.py**: This module contains functions that compute each component of the GeoPolRisk method, following the structure of the formula (**Equation 1**). The functions accept specific inputs like raw material names, countries, and years. To simplify input, the library matches raw materials to their Harmonized System (HS) codes, which are commonly used in trade. Similarly, it maps country names to their three-digit ISO codes, both stored in the background database. This helps standardize inputs, making it easier for users to perform calculations. Additionally, the `utils.py` functions assist in transforming names into the required HS and ISO codes for internal processing.

3. **utils.py**: This module supports data transformation, ensuring compatibility between user input and database requirements. It handles the conversion between names (strings) and codes (HS and ISO), aligning user inputs with the functions in `core.py`. For example, if a user defines a new region or group of countries, `utils.py` functions can aggregate trade and production data accordingly. The module also provides the `transformdata` function, allowing users to load company-specific trade data in an Excel format. This function extracts HS codes and ISO codes from the background database and reformats the trade data to the structure required for calculations.

4. **main.py**: The central module of the library, `main.py`, simplifies the use of the GeoPolRisk method through the `gprs_calc` function. Users can input a `list` of raw materials, countries, and years to compute GeoPolRisk values. The `gprs_calc` function calls relevant functions from `core.py` to calculate the supply risk score (using the first two components of the GeoPolRisk formula) and the characterization factors for Life Cycle Assessment (using all three components). Results are stored in an Excel file and a SQLite3 database, which are then exported to the "outputs" folder for easy access.

### Unique Features of the *geopolrisk-py* Library

The *`geopolrisk-py`* library offers several features to enhance its functionality:
- **Custom Region Creation**: Users can define regions or groups of countries not available in the background database. This allows for trade aggregation and region-specific supply risk analysis, a capability supported by `utils.py` and `core.py` functions.
- **Company-Specific Risk Assessment**: A standout feature is the ability to calculate supply risk based on company-specific trade data. Using a predefined Excel template available in the repository, users can input their trade data, which the library then processes using `transformdata` and other relevant functions. For example, `importrisk_company` in `core.py` calculates the second component of the GeoPolRisk method (weighted import risk), tailored to the company's unique trade mix. This feature enables companies to model different supply risk scenarios based on their specific supply chains and compare them to national averages.

#  Future Work
Uncertainties in the GeoPolRisk method stem from various sources, such as the quality of the data used and the methodology of calculation. The library will be further enhanced by incorporating a module for calculating the uncertainty of the GeoPolRisk values , consistent with best practices in LCA [@Ciroth2016]. Another area of ongoing development is the integration of the library with LCA tools like Brightway [@Mutel2017]. A new module is being designed to leverage Brightway's features and create a two-way interface. This interface will enable users to calculate specific supply risks along the value chain using the GeoPolRisk method, based on their LCA models in Brightway.

# Acknowledgments
This library was developed in collaboration with the Ecological Resource Technology group at the University of Bayreuth. The PhD thesis of the first author at the University of Bordeaux provided the opportunity to develop the initial version of the library under the TripleLink project, funded by EIT Raw Materials and supported by the EIT, a body of the European Union. The library’s development was inspired by the work of Noor-ur-Rahman Shaikh during his master's thesis at the University of Waterloo. We gratefully acknowledge his significant contributions, as well as those of Jair Santillán-Saldivar and Steven B. Young, who played key roles in its development.

# Author contributions
Anish Koyamparambath: Writing -original draft, writing - review & editing, methodology, data curation, software, validation  
Thomas Schraml: Software, validation  
Christoph Helbig: Methodology, writing - review & editing  
Guido Sonnemann: Conceptualization, writing – review & editing, supervision
