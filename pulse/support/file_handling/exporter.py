"""
exporter.py
-----------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This fule deals with all exports of file types.
"""

# --------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------
import json
import csv
import logging

# --------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------
FILE_PATH = "output"


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def export_json(data: dict, *, title: str, location: str) -> None:
    """This function exports dictionaries into JSON files."""
    logging.debug("Exporting dict -> JSON, '%s'", title)
    json_object = json.dumps(data, indent=4)
    with open(f"{location}/{title}.json", "w", encoding="UTF-8") as file:
        file.write(json_object)


def export_csv(data: list[list], *, title: str, location: str) -> None:
    """This function exports lists to CSV files."""
    logging.debug("Exporting list -> CSV, '%s'", title)
    with open(
        f"{location}/{title.replace(':','_')}.csv", "w", newline="", encoding="UTF-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile)
        for d in data:
            csv_writer.writerow(d)


def export_csv_from_dict(
    data: dict[str, list], header: list | None, *, title: str, location: str, mode: int = 0
) -> None:
    """This function exports dictionaries into CSV files."""
    logging.debug("Exporting dict -> CSV, '%s'", title)
    if mode == 1:
        if header is None:
            header = sorted(list(get_unique_second_level_keys(data)))
    
        output_ = []
        output_.append([""] + header)
        for key, point in data.items():
            output_.append([key] + [point[h] if h in point else 0 for h in header])


    if mode == 0:
        output_ = []
        assert header
        output_.append([''] + header)
        for key, point in data.items():
            output_.append([key] + point)



    with open(
        f"{location}/{title.replace(':','_')}.csv", "w", newline="", encoding="UTF-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile)
        for d in output_:
            csv_writer.writerow(d)


def get_unique_second_level_keys(nested_dict):
    unique_keys = set()
    for first_level_key in nested_dict:
        second_level_dict = nested_dict[first_level_key]
        if isinstance(second_level_dict, dict):
            for second_level_key in second_level_dict:
                unique_keys.add(second_level_key)
    return unique_keys