# Tools folder

This folder contains development and data preparation utilities that support the continued operationalization and extension of the `geopolrisk-py` package.

The material in this directory is intended for repository maintenance, database preparation, and future workflow extensions. It is not part of the end-user Python API, but it provides the supporting assets needed to build, refresh, and operationalize background resources used by the library.

## Purpose

The `tools` folder is maintained to support actions that go beyond the packaged library workflow, especially where raw external datasets need to be transformed into structured resources that can be consumed by `geopolrisk-py`.

Typical uses include:

- preparing and validating source datasets;
- converting raw files into SQLite databases used by the package;
- storing intermediate outputs generated during database preparation;
- supporting future operational extensions of the GeoPolRisk workflow.

## Current contents

At present, the main utility in this folder is the notebook `rawdata2db.ipynb`.

This notebook is designed to read the raw source files used by the method, including:

- World Mining Data files;
- BACI trade data files;
- Worldwide Governance Indicators (WGI) Excel files.

It converts these inputs into structured SQLite database files that can be integrated into the `geopolrisk` library data layer.

Additional subfolders are used to keep raw inputs, generated outputs, and legacy material that may still be useful for traceability or future maintenance.

## Scope and maintenance

Utilities in this folder may evolve independently from the public package interface. They are primarily intended for maintainers and advanced contributors who need to refresh background datasets, inspect conversion logic, or operationalize new supporting workflows around the package.
