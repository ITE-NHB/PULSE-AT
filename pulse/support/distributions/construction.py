"""
construction.py
---------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description:  This file deals with the distribution of historic buildings based on population
              development
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------
from ..file_handling.importer import import_json
from ..file_handling import export_json

# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
REFERENCE = 20_000_000


# --------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------
def fill_gaps(population_development: dict) -> dict:
    """Fills in the gaps in an incomplete dictionary of population development based on average
    values."""
    output = {}
    counter = int(list(population_development.keys())[0])
    for year, population in population_development.items():
        while int(year) >= counter:
            if int(year) == counter:
                output[counter] = population
            else:
                key = list(output.keys())[-1]
                output[counter] = int(
                    output[key]
                    + (population - output[key]) / (int(year) - counter + 1)
                    + 0.5
                )
            counter += 1
    return output


def get_population_change(population_development: dict) -> dict:
    """Creates a dictionary of population changes incomparison to the previous year."""
    output = {}
    old_population = list(population_development.values())[0]
    for num, (year, population) in enumerate(population_development.items()):
        if num == 0:
            continue
        output[year] = population - old_population
        old_population = population
    return output


def clean(population_changes: dict) -> dict:
    """This function removes the negative values in the list, since this part of the LCA is not
    accounting for demolition. It is assumed, that a very small amount of buildings are being
    build, despite the population shrinking in a given year."""
    output = {}
    for year, population in population_changes.items():
        if population > 0:
            output[year] = population
        else:
            output[year] = int(round(REFERENCE / (population * (-1)), 0))
    return output


def get_age_range(population_changes: dict, ranges: dict) -> dict:
    """This function creates a number of percentages based on population increase and specified
    ranges."""
    total = sum(population_changes.values())
    output = {}
    for type_, numbers in ranges.items():
        output[type_] = {}
        for pos in numbers:
            output[type_][pos[0]] = {}
            total = 0
            for year in range(pos[0], pos[1] + 1):
                total += population_changes[year]
            for year in range(pos[0], pos[1] + 1):
                output[type_][pos[0]][year] = population_changes[year] / total
    return output


def calc_historic_construction(country: str = "AT") -> None:
    """This function calculates the historic statistics."""
    ages = {
        "Residential": [
            (1850, 1918),
            (1919, 1944),
            (1945, 1960),
            (1961, 1980),
            (1981, 1990),
            (1991, 2000),
            (2001, 2009),
            (2010, 2022),
        ],
        "Non-residential": [
            (1850, 1944),
            (1945, 1969),
            (1970, 1979),
            (1980, 1989),
            (1990, 1999),
            (2000, 2010),
            (2011, 2022),
        ],
    }
    population_development = import_json(
        title=country, location="statistics/population"
    )
    yearly_chances = get_age_range(
        clean(get_population_change(fill_gaps(population_development))), ages
    )
    export_json(yearly_chances, title="constructionStatistic", location="statistics")
