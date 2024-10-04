"""
demolition.py
-------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the probability calculations for demolition rates
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------
from ..file_handling import export_json

# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
E = 2.71828


# --------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------
def get_weibull(
    k: int | float,
    lam: int,
    *,
    conditional: bool = False,
    ageRange: tuple = (1, 201),
    date: int = 2023
) -> dict:
    """This function calculates weibull functions."""
    output = {0: 0}
    for x in range(ageRange[0], ageRange[1]):
        year = date - x
        if conditional:
            w = (k / lam * (x / lam) ** (k - 1) * E ** -((x / lam) ** k)) / (
                E ** -(((date - year) / lam) ** k)
            )
        else:
            w = k / lam * (x / lam) ** (k - 1) * E ** -((x / lam) ** k)
        output[x] = w
    return output


def calc_future_demolition() -> None:
    """This function calculates the weibull distribution and exports it."""
    demo_rate = {
        "Residential": {
            2100: get_weibull(4, 130),
            1945: get_weibull(0.9, 220),
        },
        "Education (EDU)": {
            2100: get_weibull(3, 80),
            1945: get_weibull(0.9, 220),
        },
        "Health (HEA)": {
            2100: get_weibull(3, 80),
            1945: get_weibull(0.9, 220),
        },
        "Hotel and Restaurant (HOR)": {
            2100: get_weibull(3.5, 120),
            1945: get_weibull(0.9, 220),
        },
        "Office (OFF)": {
            2100: get_weibull(2.5, 90),
            1945: get_weibull(0.9, 220),
        },
        "Other non-residential building (OTH)": {
            2100: get_weibull(2, 105),
            1945: get_weibull(0.9, 220),
        },
        "Trade (TRA)": {
            2100: get_weibull(2.5, 80),
            1945: get_weibull(0.9, 220),
        },
    }
    export_json(demo_rate, title="weibull", location="statistics")
