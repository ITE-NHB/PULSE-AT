"""
importer.py
-----------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import csv
import json
import logging

# --------------------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------------------
FILE_PATH = "input"

# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def filled_list(x):
    """This function checks if a list is empty or filled."""
    return bool(sum(0 if a == "" else 1 for a in x))


def int_list(x, y):
    """This function turns a specified position of a list into an integer."""
    return int(list(x.keys())[y])


def import_json(*, title: str, location: str) -> dict:
    """This function imports dictionaries from JSON files."""
    logging.debug("Importing JSON file %s/%s.json", location, title)
    with open(f"{location}/{title}.json", "r", encoding='UTF-8') as file:
        data = json.load(file)
    return data


def import_csv(*, title: str, location: str = "") -> list[dict]:
    """This function imports dictionaries from CSV files."""
    logging.debug("Importing CSV file %s/%s.json", location, title)
    with open(f"{FILE_PATH}{location}/{title}", "r", encoding='UTF-8') as file:
        data = list(csv.DictReader(file))
    return data