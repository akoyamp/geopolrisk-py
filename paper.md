---
title: "geopolrisk-py: A Python-Based Library to Operationalize the Geopolitical Supply Risk Method for use in Life Cycle Assessment and Comparative Risk Assessment"
tags:
  - Criticality
  - LCA
  - Imports
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
date: 18 July 2025
bibliography: paper.bib
aas-doi: 10.3847/xxxxx
aas-journal: The Journal of Open Source Software.
---

# Summary

The Geopolitical Supply Risk (GeoPolRisk) method estimates the likelihood that supplies of a given raw material may be disrupted due to political instability in producing countries and high concentration of global production. It is used in life cycle assessment (LCA) and in comparative risk assessments to complement environmental indicators with a supply-risk perspective. In practice, applying the method can be technically demanding, as it requires combining trade data, production statistics, governance indicators, and price information to compute supply-risk scores and characterization factors. The `geopolrisk-py` library operationalizes the GeoPolRisk method by automating these calculations in a transparent and reproducible manner. It takes structured inputs such as raw material names, countries or economic units, and reference years, and produces  supply-risk scores and characterization factors (CF)s for LCA. The library is intended for life cycle assessment practitioners, materials analysts, and risk analysts in industry and the public sector, and supports applications ranging from national and regional assessments to company-specific supply risk analyses. Future developments include the integration of uncertainty analysis and tighter coupling with the Brightway 2.5 framework to further enhance functionality and usability.


# The GeoPolRisk Method
The GeoPolRisk method was developed as an import-based indicator [@Gemechu2015] to integrate the supply risk of raw materials into LCA, proposed by [@Sonnemann2015]. It is designed to evaluate the supply risk from the perspective of an economic unit (country, trade block, region, group of countries, or company/organization) during a specific period. Since its inception, the method has evolved to incorporate multiple components of resource criticality [@SantillanSaldivar2022].

The core of the method is the GeoPolRisk Score, which theoretically represents the probability of supply disruption due to geopolitical factors for a given raw material “A” and economic unit “c” during a specific year. As shown in Equation 1, this score is composed of two main components: (i) the global production concentration, represented by the Herfindahl-Hirschman Index (HHI) [@Rhoades1993] $HHI_A$, and (ii) the import dependence of the economic unit or also referred to as "import risk", which accounts for how much of the raw material is imported from politically unstable sources.

Equation 1:

$$
GeoPolRisk_{Ac} = HHI_A \cdot \sum_i \left( \frac{g_i \cdot f_{Aic}}{p_{Ac} + F_{Ac}} \right)
$$

Here, $g_i$ is the political (in-)stability of exporter $i$, $f_{Aic}$ is the amount of raw material $A$ imported by $c$ from $i$, $p_{Ac}$ is the domestic production, and $F_{Ac}$ is the total imports.

To integrate this method into life cycle impact assessment by associating the GeoPolRisk score with mass of the raw material, a factor is developed by multiplying the score with the market price of the material, yielding the GeoPolRisk Midpoint [@SantillanSaldivar2022](Equation 2). This value represents the potential value of raw material at imminent risk per kilogram of raw material consumed.

Equation 2:

$$
\text{GeoPolRisk\_Midpoint}_{Ac} = HHI_A \cdot \sum_i \left( \frac{g_i \cdot f_{Aic}}{p_{Ac} + F_{Ac}} \right) \cdot \bar{p}
$$

$\bar{p}$ is the price of the raw material. To enable comparison between materials and product systems, the midpoint factor is normalized using copper as a reference. The value for copper is calculated as an average of all the countries and for 5 years. This yields the Geopolitical Supply Risk Potential (GSP) [@Koyamparambath2024], as shown in Equation 3. The GSP has units of kg Cu-eq/kg$_A$ and is referred to as the CF for the Geopolitical Supply Risk indicator.

Equation 3:

$$
\text{GSP}_{\text{Act}} = \frac{\text{GeoPolRisk\_Midpoint}_{\text{Act}}}{\text{GeoPolRisk\_Midpoint}_{\text{Copper}}}
$$

# Statement of Need

The GeoPolRisk method has been recommended by several international initiatives concerned with the integration of criticality aspects into life cycle assessment. These include the Global Guidance for Life Cycle Impact Assessment Indicators and Methods, coordinated by the United Nations Environment Programme [@Berger2020], and the ORIENTING project [@Hackenhaar2022], a European research initiative that critically reviewed methods for integrating Criticality Assessment within a life cycle sustainability assessment framework. The method is also recognized by the International Round Table on Materials Criticality [@Schrijvers2020] as a relevant approach for evaluating short-term supply disruptions of raw materials in a geopolitical context.

Despite its recognized relevance, the broader application of the GeoPolRisk method—particularly for assessments covering multiple raw materials or for the systematic generation of CFs has remained limited due to the complexity of its calculations [@SantillanSaldivar2021a]. Both the ORIENTING project and Santillán-Saldivar et al. have highlighted the need for automated and user-friendly tools to improve the practical usability of the method [@Bachmann2021].

In practice, applications of the GeoPolRisk method have largely relied on spreadsheet-based implementations [@SantillanSaldivar2021b] or custom scripts developed for individual studies. Such approaches typically involve substantial manual data handling, are difficult to reproduce across studies, and offer limited support for systematic updates, scenario analysis, or company-specific assessments. The `geopolrisk-py` library addresses these limitations by providing an open-source, fully automated implementation of the GeoPolRisk method, incorporating standardized data mappings, built-in background datasets, and reproducible computational workflows. This enables consistent calculation of GeoPolRisk scores and CFs across multiple materials, regions, and organizational contexts. Using this library, CFs have been generated for 46 raw materials across 38 OECD countries [@Koyamparambath2024].

The software is designed to integrate seamlessly with Python-based LCA tools such as Brightway [@Mutel2017], thereby facilitating practical implementation within established LCA workflows. Such integration supports alignment with intermediate flows and enables the evaluation of supply risks along value chains [@Helbig2016]. An application of the library to regionalized flows further demonstrated its scalability and suitability for large-scale assessments [@Sacchi2025].

Beyond life cycle assessment, the GeoPolRisk score can also be applied as a comparative risk assessment tool by companies and organizations [@Koyamparambath2021]. Through automation, users can input their own supply mixes to derive tailored risk scores, supporting scenario analysis and benchmarking of geopolitical supply risks against national or sectoral reference values.

# Features of the `geopolrisk-py` Library

The _geopolrisk-py_ library is organized into four modules: `database.py`, `core.py`, `main.py`, and `utils.py`, each with specific roles to facilitate the calculation of the GeoPolRisk method.

1. **database.py**: This module is responsible for loading all the essential background data required for the library’s operations. The necessary data includes mining production data (from world mining data) [@FMRA2023], trade data (from BACI for past years) [@Cepii2024], and governance indicators (from the World Bank) [@WorldBank2024]. These datasets are stored in a SQLite3 database, which is updated annually and available in the repository. Upon installation, the library sets up a folder in the Document folder in the user's home directory with three subfolder:

   - **databases**: - Contains the input template (company_data.xlsx), which users can populate for company-level risk assessments.
   - **output**: This folder stores the SQLite3 database and Excel output files generated after calculations.
   - **logs**: For debugging errors encountered during the process.

2. **core.py**: This module implements the main computational logic of the GeoPolRisk method. It calculates each component of the method, including HHI, import risk, and the resulting GeoPolRisk score and the CFs. These calculations rely on background data that links raw material and country names to standardized identifiers. The module is responsible for executing the equations that define the method, using pre-processed and structured inputs provided by the supporting modules.

3. **utils.py**: This module handles the data preparation required for GeoPolRisk calculations. It maps defined raw material and country names to Harmonized System codes and ISO 3-digit codes, ensuring compatibility with the underlying database. It also aligns raw material production data with corresponding commodity trade data, which may include multiple overlapping HS codes, and aggregates them into a consolidated dataset. In effect, `utils.py` performs all the backend transformation and standardization needed to bridge data with the model’s requirements. It supports core.py by ensuring that inputs are clean, consistent, and ready for computation.

4. **main.py**: This module provides a one-stop interface that integrates the entire workflow. It allows users to define a list of raw materials, years, and economic units, and then manages the process of calling the appropriate functions from core.py, using data handled by utils.py. The outputs including the components of the GeoPolRisk method (HHI, import risk & price) along with the values (GeoPolRisk score & CF) are saved in both Excel and SQLite formats in an organized folder structure. This module is designed to simplify the application of the method for larger-scale or repeated assessments.

### Unique Features of the _geopolrisk-py_ Library

The _`geopolrisk-py`_ library offers several features to enhance its functionality:

- **Custom region creation**: Users can define regions or groups of countries that are not available in the background database. This allows for aggregation of trade data and region-specific supply risk analysis. The functionality is supported by backend routines that map and combine production and trade data as needed.

- **Company-specific risk assessment**: A key feature of the library is the ability to evaluate supply risk based on company-specific trade flows. By using a predefined Excel template included in the repository, users can input their own import data. The library then processes and reformats the data, linking it to the corresponding raw material and country codes. This enables users to calculate supply risk scores that reflect their actual supply chains and to explore different scenarios by comparing company-specific results to national or regional benchmarks.

# Future Work

Uncertainties in the GeoPolRisk method stem from various sources, such as the quality of the data used and the methodology of calculation. The library will be further enhanced by incorporating a module for calculating the uncertainty of the GeoPolRisk values , consistent with best practices in LCA [@Ciroth2016]. Another area of ongoing development is the integration of the library with LCA tools like Brightway [@Mutel2017]. A new module is being designed to leverage Brightway's features and create a two-way interface. This interface will enable users to calculate specific supply risks along the value chain using the GeoPolRisk method, based on their LCA models in Brightway.

# Acknowledgments

This library was developed in collaboration with the Ecological Resource Technology group at the University of Bayreuth. We especially thank Riccarda Hieke for her extensive support in testing the package and for providing valuable feedback. The initial development of the library was carried out within the PhD research of the first author at the University of Bordeaux, under the TripleLink project funded by EIT Raw Materials and supported by the EIT, a body of the European Union. Subsequent development was continued within the HiQ-LCA project, also funded by EIT Raw Materials. The library was further inspired by the master’s thesis work of Noor-ur-Rahman Shaikh at the University of Waterloo. We gratefully acknowledge his significant contributions, as well as those of Jair Santillán-Saldivar and Steven B. Young, who played key roles in the development and refinement of the methodology.

# Author contributions

Anish Koyamparambath: Writing - original draft, writing - review & editing, methodology, data curation, software, validation
Thomas Schraml: Software, validation
Christoph Helbig: Methodology, writing - review & editing
Guido Sonnemann: Conceptualization, writing – review & editing, supervision

# References