"""
construction.py
---------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# FUNCTIONS
from ..variables import adapt_detail, remove_empty

# CLASSES
from ..variables import Detail

# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------
NR_RENO_OPTIONS = 4


# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
def calc_demolitions(stock: dict, year: int, detail: Detail) -> dict | list:
    """This function demolishes the necessary buildings."""
    temp_ = remove_empty(
        adapt_detail(
            {
                country: {
                    code: b.development[year].calcDemolition(year)
                    for code, b in countryData.items()
                }
                for country, countryData in stock.items()
            },
            detail,
        )
    )
    assert isinstance(temp_, dict)
    return temp_
