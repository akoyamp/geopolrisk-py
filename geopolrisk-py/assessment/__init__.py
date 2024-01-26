import logging, os
from datetime import datetime
from pathlib import Path
import yaml


logging = logging
__all__ = ["core", "operations", "gcalc", "gprsplots", "utils", "tests", "main"]
__author__ = "Anish Koyamparambath <CyVi- University of Bordeaux>"
__status__ = "Beta"
__version__ = "3.0.1"
__data__ = "30 September 2023"

hard_dependencies = ("pandas", "logging", "urllib", "functools")
missing_dependencies = []
for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(f"{dependency}: {e}")

if missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies


"""
Load meta data from config.yaml file.
"""
try:
    with open("geopolrisk-py/assessment/config.yaml", "r") as config_file:
        config_data = yaml.safe_load(config_file)
        if config_data is not None:
            pass
        else:
            raise ValueError("Config file is empty or contains invalid data.")
except FileNotFoundError:
    print("Config file not found.")
except Exception as e:
    print(f"An error occurred: {e}")


if config_data:
    Folder = config_data["Main"]["Folder"]
    LogFile = config_data["Log"]["Filename"].format(datetime.now())
    LogLEVEL = config_data["Log"]["Level"]
    LogFormat = config_data["Log"]["Format"]
    LogMode = config_data["Log"]["Mode"]
else:
    print("Error loading the configuration data.")
    raise Exception("Error loading the configuration data.")

# Create directories
try:
    if not os.path.exists(os.path.join(Path.home(), Folder)):
        os.makedirs(os.path.join(Path.home(), Folder))

    if not os.path.exists(os.path.join(Path.home(), Folder + "/logs")):
        os.makedirs(os.path.join(Path.home(), Folder + "/logs"))

    if not os.path.exists(os.path.join(Path.home(), Folder + "/databases")):
        os.makedirs(os.path.join(Path.home(), Folder + "/databases"))

    if not os.path.exists(os.path.join(Path.home(), Folder + "/output")):
        os.makedirs(os.path.join(Path.home(), Folder + "/output"))
except Exception as e:
    print(f"Unable to create directories {e}")
    raise FileNotFoundError

logging.basicConfig(
    level=LogLEVEL,
    format=LogFormat,
    filename=os.path.join(Path.home(), Folder + "/logs") + "/" + LogFile,
    filemode=LogMode,
)
