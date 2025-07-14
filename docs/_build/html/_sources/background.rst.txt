.. _Background:

Background
==========

The GeoPolRisk Method
---------------------

The GeoPolRisk method was developed to quantify the supply risk of raw materials within a product to a country, region, or group of countries. It was proposed to complement Life Cycle Assessment (LCA) in the form of a midpoint characterization factor (CF) for Life Cycle Sustainability Assessment (LCSA).

The method quantifies supply risk as a function of the global production concentration of the raw material and the trade partner’s import shares weighted by their political instability. The production concentration is evaluated with the normalized Herfindahl-Hirschman Index (HHI) (from 0 to 1) for raw material extraction or processing, and the political instability is estimated using the Worldwide Governance Indicators.

Since its inception, the method has evolved, incorporating several dimensions of resource criticality.

History of GeoPolRisk Method at a Glance
----------------------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Publication
     - Contribution
   * - Sonnemann et al. (2015) [13]_
     - - Initial proposal for integration of raw material criticality into the LCSA framework.
       - Identification of supply risk as a potential indicator to address resource accessibility in LCA.
   * - Gemechu et al. (2015) [4]_
     - - Definition of the geopolitical supply risk indicator (GeoPolRisk) to integrate raw material criticality within LCSA.
       - First application of the method to a set of 14 resources from the perspective of 7 economies.
   * - Gemechu et al. (2016) [5]_
     - - Application of the GeoPolRisk method to the previous 14 studied resources in the inventory of electric vehicles.
       - Comparison between the contribution of the analyzed resources to supply risk and other environmental impacts from an LCA perspective.
   * - Helbig et al. (2016) [6]_
     - - Introduction of domestic production as a risk mitigating factor in the calculation of the geopolitical supply risk.
       - Application of the method to multiple stages in the petrochemical supply chain of polyacrylonitrile-based carbon fibers.
   * - Cimprich et al. (2017a) [1]_
     - - Introduction of substitutability indicators as a risk mitigating factor in the calculation of geopolitical supply risk.
       - Application of the method to selected resources in the inventory of electric vehicles and dental X-ray machines.
   * - Cimprich et al. (2017b) [2]_
     - - Definition of a characterization model for the application of the GeoPolRisk method as a complement to environmental LCA.
       - Application to the inventory of conventional and electric vehicles.
   * - Cimprich et al. (2019) [3]_
     - - Review and comparison of methods for product-level supply risk assessment.
       - Identification of methodological gaps in the impact pathway based on geopolitical supply risk.
   * - Santillán-Saldivar et al. (2020) [10]_
     - - Definition of the GeoPolEndpoint method to measure socio-economic impacts at the endpoint level associated with the use of critical raw materials.
       - Application of the GeoPolEndpoint method to four relevant resources in the inventory of lithium-ion batteries from the perspective of the country members of the OECD.
   * - Santillán-Saldivar et al. (2021) [11]_
     - - Introduction of recycling as a risk mitigating factor in the calculation of the geopolitical supply risk indicator.
       - Application to 13 resources or groups of resources under different recycling scenarios from the perspective of the European Union.
   * - Koyamparambath et al. (2022) [7]_
     - - Using the GeoPolRisk method for comparative risk assessment.
       - Application to the case of raw materials used in batteries and fossil fuels for 6 different economic units from 2000–2018.
   * - Santillán-Saldivar et al. (2022) [12]_
     - - Redefinition of the characterization model to measure the supply risk potential based on the geopolitical supply risk indicator as a complement to environmental LCA.
       - Integration of a truly mass-based midpoint indicator in line with the previously published endpoint impact pathways associated with geopolitical supply risk.
   * - Koyamparambath et al. (2024) [9]_
     - - Operationalizing the characterization model with spatially and temporally differentiated characterization factors for 42 raw materials.
       - Application to the case of photovoltaic laminate demonstrating the complementarity of the GeoPolRisk method with LCA indicators.

The Values of the GeoPolRisk Method
-----------------------------------

A country, region, trade block, or company is represented as an economic unit. The formula for determining the probability of supply risk attributed to geopolitical factors, commonly referred to as the "GeoPolRisk Score," for a specific material "A" is outlined in Equation 1, taking into account the perspective of the economic unit "c" during a given year. The formula can be interpreted as a composite of two contributing factors: the global production concentration and the import dependency of the metal or mineral.

**Equation 1: Equation to calculate the GeoPolRisk Score**

.. math::

   \text{GeoPolRisk}_{Ac} = \text{HHI}_A \times \sum_i \left( \frac{g_i \cdot f_{Aic}}{p_{Ac} + F_{Ac}} \right)

Where:
- :math:`\text{HHI}_A` = Herfindahl-Hirschman Index for commodity A  
- :math:`g_i` = Geopolitical (in)stability of economic unit *i*  
- :math:`f_{Aic}` = Imports of commodity A from country *i* to economic unit *c*  
- :math:`F_{Ac}` = Total imports of commodity A to economic unit *c*  
- :math:`p_{Ac}` = Domestic production of commodity A in economic unit *c*  

The subsequent study introduced a substitutability indicator as a vulnerability to supply risk factor to the GeoPolRisk method. Domestic recycling of resources was also identified as a risk mitigation factor and was included in the method by reduction and redistribution of the import share.

To integrate the method into LCSA, a connection to the functional unit is necessary. A characterization model of the GeoPolRisk method based on the defined cause-effect mechanism was developed to complement environmental LCA. A new characterization model and a modified midpoint indicator were developed to address the identified methodological gaps. The complete equation for the GeoPolRisk midpoint CF of a resource “A” from the perspective of a country “c” in a given year is shown in Equation 2:

**Equation 2: The midpoint characterization factor for the GeoPolRisk method**

.. math::

   \text{GeoPolRisk}_{Ac} = \text{HHI}_A \times \sum_i \left( \frac{g_i \cdot f_{Aic}}{p_{Ac} + F_{Ac}} \right) \cdot \bar{p}

:math:`\text{HHI}_A` is the Herfindahl-Hirschman Index for resource A, calculated as the sum of the squared production shares of all the countries producing resource A. The GeoPolRisk method weights the import (:math:`f_{Aic}`) of resource A to country *c* from *i* with the political (in)stability indicator of the exporting country (:math:`g_i`). :math:`F_{Ac}` is the total imports to the entity in assessment, and :math:`p_{Ac}` is the domestic production of resource A in entity *c*.

The CF is called **Geopolitical Supply Risk Potential (GSP)** and is used to evaluate the **Geopolitical Supply Risk (GSR)** of raw materials consumed in a product/product system. The values for the GSP are obtained by dividing the GeoPolRisk midpoint for a given raw material by the respective GeoPolRisk midpoint of copper for the same economic unit and time period, as shown in Equation 3. Here, "A" represents the raw material, "c" represents an economic unit, and "t" refers to the time period (year). At the midpoint level, the indicator seeks to quantify “the risk of relative potential accessibility issues for a product system related to short-term geopolitical and socio-economic aspects.” As an import-based indicator, using the characterization model, the CFs represent the supply risk of a raw material equivalent to the supply risk of importing one kilogram of copper to an economic unit at a given time period. This provides a way to compare the GSR for different processes or product systems using a common reference.

**Equation 3: The GeoPolRisk characterization model to calculate the Geopolitical Supply Risk Potential**

.. math::

   \text{GSP}_{Act} = \frac{\text{GeoPolRisk midpoint}_{Act}}{\text{GeoPolRisk midpoint (Copper)}_{ct}}

The characterization model uses trade data from a comprehensive disaggregated database for bilateral trade flows known as the Database for International Trade Analysis (BACI). The traded price is calculated using the “free on board value,” a mechanism commonly used in international trade that considers the cost, insurance, and freight of a product being transported from the seller to the buyer. Global mine production data were obtained from the *World Mining Data - 2021* report published by the Austrian Federal Ministry of Finance.


.. image:: _static/characterization_model.png
   :alt: Characterization model of the GeoPolRisk method
   :align: center
   :width: 100%

Application of the Method
-------------------------

Mapping the CFs of the GeoPolRisk method to LCI elementary flows presents a challenge primarily arising from the inherent nature of supply risk associated with the traded commodity. Within the context of LCA, the traded commodity refers to the intermediate flow obtained from a mining activity. LCA characterizes the impacts associated with elementary flows, encompassing inputs and outputs. Consequently, applying CFs directly to intermediate flows becomes impractical, as they cannot be automatically traced unless unit processes are considered.

To address this limitation, we assume that, in mining activities in ecoinvent, the elementary input flow of the mineral extracted from the ground is in the same range as the intermediate output flow of the mineral being produced. This assumption is true for most of the mining activities in ecoinvent, except for activities where mineral processing waste is high and mining activities where elementary flows are allocated to co-products having different economic values. This assumption enables the application of CFs to elementary rather than intermediate flows, rendering the GeoPolRisk method feasible in this context.

The GeoPolRisk method takes on the perspective of an economic unit and time period while calculating the CFs for raw materials. Ideally, the geographic location of the elementary flow where the activity occurs is utilized to apply the corresponding CF and calculate the GSR of the product system. However, within the ecoinvent processes, activities involve a combination of flows originating from various geographical locations, and to address this challenge, a potential solution is to assume that all activities occur within a specific geographic location, except for mining activities, and apply the specific CFs to all elementary flows.

Nevertheless, the supply risk associated with the primary product is inherently linked to the location of its manufacturing. This is because there’s an assumption that the supply risk linked to intermediate products is at least equal to, if not greater than, the supply risk of the raw materials required for producing the intermediate product in the same location where the primary product is made.


Glossary of Terms
-----------------

.. list-table:: Key Terms in the GeoPolRisk Method
   :header-rows: 1
   :widths: 25 75

   * - Abbreviation
     - Meaning
   * - GeoPolRisk
     - Geopolitically related supply risk method
   * - GeoPolRisk Score
     - A non-dimensional supply risk value useful for comparative risk assessment
   * - GSP
     - Geopolitical Supply Risk Potential – the characterization factor used in Life Cycle Assessment, expressed as kg Cu-eq. per kg
   * - GSR
     - Geopolitical Supply Risk – the midpoint impact calculated using the GSP
   * - HHI
     - Herfindahl-Hirschman Index – indicator for concentration of production of a raw material (normalized to the range 0–1)
   * - LCA
     - Life Cycle Assessment – methodology to assess environmental impacts associated with all the stages of a product's life
   * - LCSA
     - Life Cycle Sustainability Assessment – integrated framework combining LCA, life cycle costing, and social LCA


.. note::

   The contents of this page are based on published work by Koyamparambath A. (2023) [8]_ and Koyamparambath et al. (2024) [9]_.


References
----------

.. [1] Cimprich A., Karim K.S., Young S.B. (2017a). Extending the geopolitical supply risk method: Material “substitutability” indicators applied to electric vehicles and dental X-ray equipment. *International Journal of Life Cycle Assessment*, 23(10), 2024–2042.

.. [2] Cimprich A., Young S.B., Helbig C., Gemechu E.D., Thorenz A., Tuma A., Sonnemann G. (2017b). Extension of geopolitical supply risk methodology: characterization model applied to conventional and electric vehicles. *Journal of Cleaner Production*, 162, 754–763.

.. [3] Cimprich A., Bach V., Helbig C., Thorenz A., Schrijvers D., Sonnemann G., Young S.B., Sonderegger T., Berger M. (2019). Raw material criticality assessment as a complement to environmental life cycle assessment: examining methods for product-level supply risk assessment. *Journal of Industrial Ecology*, 23, 1226–1236.

.. [4] Gemechu E.D., Helbig C., Sonnemann G., Thorenz A., Tuma A. (2015). Import-based Indicator for the geopolitical supply risk of raw materials in life cycle sustainability assessments. *Journal of Industrial Ecology*, 20(1), 154–165.

.. [5] Gemechu E.D., Sonnemann G., Young S.B. (2016). Geopolitical-related supply risk assessment as a complement to environmental impact assessment: the case of electric vehicles. *International Journal of Life Cycle Assessment*. https://doi.org/10.1007/s11367-015-0917-4G

.. [6] Helbig C., Gemechu E.D., Pillain B., Young S.B., Thorenz A., Tuma A., Sonnemann G. (2016). Extending the geopolitical supply risk indicator: application of life cycle sustainability assessment to the petrochemical supply chain of polyacrylonitrile-based carbon fibers. *Journal of Cleaner Production*, 137, 1170–1178.

.. [7] Koyamparambath A., Santillán-Saldivar J., McLellan B., Sonnemann G. (2022). Supply risk evolution of raw materials for batteries and fossil fuels for selected OECD countries (2000–2018). *Resources Policy*, 75, 102465.

.. [8] Koyamparambath A. (2023). *Mise en oeuvre et élargissement d'une méthode d'évaluation de la criticité du cycle de vie à l'aide de techniques informatiques* (Doctoral dissertation, University of Bordeaux).

.. [9] Koyamparambath A., Loubet P., Young S.B., Sonnemann G. (2024). Spatially and temporally differentiated characterization factors for supply risk of abiotic resources in life cycle assessment. *Resources, Conservation and Recycling*, 209, 107801. https://doi.org/10.1016/j.resconrec.2024.107801.

.. [10] Santillán-Saldivar J., Gaugler T., Helbig C., Rathgeber A., Sonnemann G., Thorenz A., Tuma A. (2020). Design of an endpoint indicator for mineral resource supply risks in life cycle sustainability assessment: The case of Li-ion batteries. *Journal of Industrial Ecology*, 2020, 1–12. https://doi.org/10.1111/jiec.13094

.. [11] Santillán-Saldivar J., Cimprich A., Shaikh N., Laratte B., Young S.B., Sonnemann G. (2021). How recycling mitigates supply risks of critical raw materials: extension of the geopolitical supply risk methodology applied to information and communication technologies in the European Union. *Resources, Conservation and Recycling*, 164, 2021. https://doi.org/10.1016/j.resconrec.2020.105108

.. [12] Santillán-Saldivar J., Gemechu E., Muller S., Villeneuve J., Young S.B., Sonnemann G. (2022). An improved resource midpoint characterization method for supply risk of resources: integrated assessment of Li-ion batteries. *International Journal of Life Cycle Assessment*, 27, 457–468. https://doi.org/10.1007/s11367-022-02027-y

.. [13] Sonnemann G., Gemechu E.D., Adibi N., De Bruille V., Bulle C. (2015). From a critical review to a conceptual framework for integrating the criticality of resources into Life Cycle Sustainability Assessment. *Journal of Cleaner Production*. https://doi.org/10.1016/j.jclepro.2015.01.082