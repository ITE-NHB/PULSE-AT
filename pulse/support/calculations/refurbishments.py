"""
refurbishment.py
----------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
import numpy as np
import logging

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# VARIABLES
from ..variables import TYPOLOGIES

# FUNCTIONS
from ..variables import remove_empty, adapt_detail
from ..file_handling import import_json

# CLASSES
from ..variables import Detail

# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------
REFURBISHMENT = (0.009, 0.005, 0.001)

REFURBISHMENT1 = np.array([0.009, 0.005, 0.001])

REFURBISHMENT_STATISTIC = None
NR_RENO_OPTIONS = 4


# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
def calc_refurbishments(stock: dict, scenario: dict, year: int, detail: Detail):
    """This function calculates the refurbishments."""

    return_ = {}

    global REFURBISHMENT_STATISTIC
    if not REFURBISHMENT_STATISTIC:
        REFURBISHMENT_STATISTIC = import_json(title="renovation", location="statistics")

    for country, countryData in stock.items():
        if country not in return_:
            return_[country] = {}

        for typology in TYPOLOGIES["Residential"]:
            relevant = list(filter(lambda a: typology in a, countryData.keys()))
            total = sum(
                [
                    sum(s.number.total.values())
                    for name, s in countryData.items()
                    if name in relevant
                ]
            )
            renovation_ = (
                (
                    REFURBISHMENT[0]
                    if scenario["refurbish"][0] is None
                    else scenario["refurbish"][0]
                ),
                (
                    REFURBISHMENT[1]
                    if scenario["refurbish"][1] is None
                    else scenario["refurbish"][1]
                ),
                (
                    REFURBISHMENT[2]
                    if scenario["refurbish"][2] is None
                    else scenario["refurbish"][2]
                ),
            )
            #logging.info("Starting Refurbishment with %f %f %f", renovation_[0],renovation_[1],renovation_[2])

            light, medium, deep = [ren * total for ren in renovation_]
            for r in relevant:
                multiplier = 0
                if r[7:11] not in ["2001", "2010"]:
                    multiplier = REFURBISHMENT_STATISTIC[typology][r[7:11]]
                l, m, d = (
                    int(light * multiplier + 0.5),
                    int(medium * multiplier + 0.5),
                    int(deep * multiplier + 0.5),
                )
                return_[country][r], overflow = (
                    countryData[r].development[year].calcRefurbishment(l, m, d)
                )
                """
                
                if any(overflow):
                    print(countryData[r].development[year].number)
                    print(overflow, typology)
                    input()
                
                """

        for typology in TYPOLOGIES["Non-residential"]:
            relevant = list(filter(lambda a: typology in a, countryData.keys()))
            total = sum(
                [
                    sum(s.number.total.values())
                    for name, s in countryData.items()
                    if name in relevant
                ]
            )
            light, medium, deep = [ren * total for ren in REFURBISHMENT]
            for r in relevant:
                multiplier = 0
                if r[7:11] not in ["2000", "2011"]:
                    multiplier = (
                        REFURBISHMENT_STATISTIC[typology][r[7:11]]
                        if typology != "OTH"
                        else REFURBISHMENT_STATISTIC["TRA"][r[7:11]]
                    )
                l, m, d = (
                    int(light * multiplier + 0.5),
                    int(medium * multiplier + 0.5),
                    int(deep * multiplier + 0.5),
                )
                return_[country][r], overflow = (
                    countryData[r].development[year].calcRefurbishment(l, m, d)
                )

    return remove_empty(adapt_detail(return_, detail))

