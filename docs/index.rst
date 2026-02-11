.. geopolrisk-py documentation master file, created by
   sphinx-quickstart on Mon Jul  7 16:12:04 2025.
GeoPolRisk-py Documentation
===========================

The **Geopolitical Supply Risk (GeoPolRisk)** method assesses raw material criticality within Life Cycle Assessment (LCA), complementing traditional resource and environmental impact indicators. It is also applicable in comparative risk assessments.

However, calculating values for the GeoPolRisk method—such as **characterization factors** for the Geopolitical Supply Risk indicator and the **supply risk score** for comparative assessment—can be complex.

To simplify this, the **`geopolrisk-py`** library has been developed to operationalize the method. It streamlines calculations by processing data inputs such as raw material names, countries, and years. A key feature is its ability to serve as a **company-specific supply risk assessment tool**.

Citation
--------

.. code-block:: bibtex

   @software{geopolrisk-py,
     author    = {Anish Koyamparambath, Thomas Schraml, Christoph Helbig, Guido Sonnemann},
     title     = {geopolrisk-py: A Python-Based Library to Operationalize the Geopolitical Supply Risk Method for use in Life Cycle Assessment and Comparative Risk Assessment},
     version   = {2.0.0},
     doi       = {},
     url       = {https://github.com/akoyamp/geopolrisk-py},
     year      = {2026},
     publisher = {Zenodo},
     license   = {GPL-3.0}
   }

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   background
   usage
   methods
   company
   references
   testing
   contribution
   
.. toctree::
   :maxdepth: 1
   :caption: Notebooks

   notebooks/example.ipynb
Download the notebook: :download:`example notebook <notebooks/example.ipynb>`

