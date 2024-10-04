"""
total.py
--------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------------------
# Local Imports
# --------------------------------------------------------------------------------------------------

# FUNCTIONS
from ..variables import Detail, adapt_detail, remove_empty

# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------
NR_RENO_OPTIONS = 4


# --------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------
def total_buildings(stock: dict, year: int, detail: Detail):
    """This function returns the number of buildings for each typology or grouped."""
    return {
            country: {
                key: s.development[year].number.listify()
                for key, s in countryData.items()
            }
            for country, countryData in stock.items()
        }


def calc_volume(construction: dict, demolition: dict, stock: dict, detail: Detail):
    """This function calculates the build and demolished volume."""
    if detail == Detail.NO_CALC:
        return None, None
    return_cons = {}
    return_demo = {}
    for country, country_stock in stock.items():
        return_cons[country] = {}
        return_demo[country] = {}

        for key_, building_ in country_stock.items():
            return_cons[country][key_] = (
                (
                    (
                        construction[country][key_] * building_.building.volume
                        if key_ in construction[country]
                        else 0
                    )
                    if country in construction
                    else 0
                )
                if construction
                else 0
            )
            return_demo[country][key_] = (
                (
                    (
                        sum(demolition[country][key_]) * building_.building.volume
                        if key_ in demolition[country]
                        else 0
                    )
                    if country in demolition
                    else 0
                )
                if demolition
                else 0
            )
    return remove_empty(adapt_detail(return_cons, detail)), remove_empty(
        adapt_detail(return_demo, detail)
    )
