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
date: 18 July 2025
bibliography: paper.bib
aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
aas-journal: The Journal of Open Source Software.
---

# Summary

The Geopolitical Supply Risk (GeoPolRisk) method assesses raw material criticality in Life Cycle Assessment (LCA), complementing traditional resource and environmental impact indicators. It is also applied for comparative risk assessment. However, calculating values for the GeoPolRisk method, such as characterization factors for the Geopolitical Supply Risk indicator and the supply risk score for comparative assessment, can be complex. To address this, the `geopolrisk-py` library has been developed to operationalize the method, simplifying the calculation process. This library processes data inputs like raw material names, countries, and years, making it more accessible. A notable feature is its ability to serve as a company-specific supply risk assessment tool. Future development will include integrating an uncertainty model and additional modules for complete compatibility with Brightway 2.5, further enhancing functionality and usability.

# The GeoPolRisk Method

The GeoPolRisk method is an import-based indicator [@Gemechu2015] developed to integrate the criticality of raw materials into the Area of Protection ‘natural resources’, as proposed by [@Sonnemann2015]. It is designed to evaluate the supply risk of importing raw materials from a trade (country, trade block, region, group of countries, or company/organization) perspective during a specific period. Since its inception, the method has evolved to incorporate multiple components of resource criticality [@Cimprich2019].

The core of the method is the GeoPolRisk Score, which reflects the probability of supply disruption due to geopolitical factors for a given raw material “A” and economic unit “c” during a specific year. As shown in Equation 1, this score is composed of two main components: (i) the global production concentration, represented by the Herfindahl-Hirschman Index (HHI) $HHI_A$, and (ii) the import dependence of the economic unit or also refered to as "import risk", which accounts for how much of the raw material is imported from politically unstable sources.

Equation 1:

$$
GeoPolRisk_{Ac} = HHI_A \cdot \sum_i \left( \frac{g_i \cdot f_{Aic}}{p_{Ac} + F_{Ac}} \right)
$$

Here, $g_i$ is the political (in-)stability of exporter $i$, $f_{Aic}$ is the amount of raw material $A$ imported by $c$ from $i$, $p_{Ac}$ is the domestic production, and $F_{Ac}$ is the total imports.

To integrate this method into life cycle impact assessment by associating the GeoPolRisk score with mass of the raw material, a factor is developed by multiplying the score with the market price of the material, yielding the GeoPolRisk Midpoint [@Santillan-Saldivar2022] in Equation 2. This value represents the potential value of raw material at imminent risk per kilogram of raw material consumed.

Equation 2:

$$
GeoPolRisk\_Midpoint_{Ac} = HHI_A \cdot \sum_i \left( \frac{g_i \cdot f_{Aic}}{p_{Ac} + F_{Ac}} \right) \cdot p'
$$

To enable comparison between materials and product systems, the midpoint factor is normalized using copper as a reference. The value for copper is calculated as an average of all the countries and for 5 years. This yields the Geopolitical Supply Risk Potential (GSP) [@Koyamparambath2024], as shown in Equation 3. The GSP has units of kg$_{\text{Cu-eq}}$/kg$_A$ and is refered to as the characterization factor (CF) for the Geopolitical Supply Risk indicator.

Equation 3:

$$
GSP_{Act} = \frac{GeoPolRisk\_Midpoint_{Act}}{GeoPolRisk\_Midpoint_{\text{Copper}}}
$$

# Statement of Need

The GeoPolRisk method has been recommended by initiatives such as the Global Guidance for Life Cycle Impact Assessment Indicators and Methods, hosted by the United Nations Environmental Program [@Berger2020], and by the ORIENTING project [@Hackenhaar2022], a European project that critically reviewed methods for integrating Criticality Assessment with the life cycle approach as part of efforts to operationalize Life Cycle Sustainability Assessment. The method is also recognized by the International Round Table on Materials Criticality [@Schrijvers2020] as a relevant approach for evaluating short-term supply disruptions of raw materials in a geopolitical context.

Despite its benefits, broader applications of the GeoPolRisk method, especially for multiple raw materials or in generating CFs are limited due to the complexity of its calculation [@Santillan-Saldivar2021]. The ORIENTING project and Santillán-Saldivar et al. have both emphasized the need for automated tools to improve its usability [@Bachmann2021] [@Hackenhaar2022]. By using this library, CFs for 46 raw materials across 38 OECD countries have been generated [@Koyamparambath2024]. Integration with LCA software such as Brightway [@Mutel2017], a widely used open-source Python platform, can further streamline practical implementation. Such integration also facilitates alignment with intermediate flows [@Bachmann2021] [@Mancini2016] and enables supply risk evaluation across the supply chain [@Helbig2016] [@Koyamparambath2024] [@Siddhantakar2023].

Beyond life cycle applications, the GeoPolRisk Score can be used as a comparative risk assessment tool by companies and organizations [@Koyamparambath2021]. With an automated tool, users can input their specific supply mix to generate tailored risk scores. This supports scenario analysis and benchmarking of geopolitical supply risk against national or sectoral averages.

# Features of the `geopolrisk-py` Library

The _geopolrisk-py_ library is organized into four modules: `database.py`, `core.py`, `main.py`, and `utils.py`, each with specific roles to facilitate the calculation of the GeoPolRisk method.

1. **database.py**: This module is responsible for loading all the essential background data required for the library’s operations. The necessary data includes mining production data (from world mining data) [@FMRA2023], trade data (from BACI for past years) [@cepii_baci_2024], and governance indicators (from the World Bank) [@WorldBank2024]. These datasets are stored in a SQLite3 database, which is updated annually and available in the repository. Upon installation, the library sets up a folder in the Document folder in the user's home directory with three subfolders:

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

This library was developed in collaboration with the Ecological Resource Technology group at the University of Bayreuth. We especially thank Riccarda Hieke for her extensive support in testing the package and providing valuable feedback. The PhD thesis of the first author at the University of Bordeaux provided the opportunity to develop the initial version of the library under the TripleLink project, funded by EIT Raw Materials and supported by the EIT, a body of the European Union. The library’s development was inspired by the work of Noor-ur-Rahman Shaikh during his master's thesis at the University of Waterloo. We gratefully acknowledge his significant contributions, as well as those of Jair Santillán-Saldivar and Steven B. Young, who played key roles in its development.

# Author contributions

Anish Koyamparambath: Writing - original draft, writing - review & editing, methodology, data curation, software, validation  
Thomas Schraml: Software, validation  
Christoph Helbig: Methodology, writing - review & editing  
Guido Sonnemann: Conceptualization, writing – review & editing, supervision
