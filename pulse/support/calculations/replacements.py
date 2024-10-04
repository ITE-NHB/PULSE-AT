"""
replacements.py

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
import logging

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------
from ..data_types import GroupedProducts
from ..variables import Detail, adapt_detail, remove_empty, prime

MULTIPLIER = 0.17
LIFETIMES = None
HSS_OPTIONS = 3
# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
def calc_one_replacement(
    possibleProducts: GroupedProducts, lifetimes: dict, age: int
) -> GroupedProducts | None:
    """This function calculates the replaced products of one Grouped Products object for one age."""
    assert (
        type(age) is int or type(age) is float
    ), f"ERROR during calculation of repair: age must be a number. Is {type(age)}"
    if type(age) is float:
        logging.warning(
            "The age during repair calculation is a float and not an integer!"
        )
        age = int(age)

    if prime(age):
        return None

    return_ = GroupedProducts("Repair Products", "t")

    for product, amount in possibleProducts.dictify().items():
        assert (
            product in lifetimes
        ), f"ERROR during calculation of repair: product must have a lifetime!"
        if not lifetimes[product]:
            logging.warning(f"{product} lifetime is 0")
            continue
        if age and lifetimes[product] and not age % lifetimes[product]:

            return_ += (product, amount * MULTIPLIER)

    if sum(return_.dictify().values()) == 0:
        return None
    return return_


def clean(input_: dict | GroupedProducts) -> dict:
    if type(input_) is dict:
        output_ = {}
        for key, data in input_.items():
            clean_ = clean(data)
            if clean_:
                output_[key] = clean_
        return output_
    if type(input_) is GroupedProducts:
        output_ = {}
        for product, amount in input_.dictify().items():
            output_[product] = amount
        return output_
    raise TypeError


def calc_year_replacement(stock: dict, year: int, products: dict, detail: Detail) -> dict:
    """This function calculates the replaced products in one year."""
    output_ = {}

    global LIFETIMES
    if not LIFETIMES:
        LIFETIMES = {key: product.serviceLife for key, product in products.items()}

    if detail == Detail.GROUPED:
        raise TypeError("Not Supported")
    if detail == Detail.TYPOLOGY:
        raise TypeError("Not Supported")
    if detail == Detail.COMPONENT:
        for typology, stockItem in stock.items():
            if typology not in output_:
                output_[typology] = {}
            for year_, amount_ in stockItem.development[year].number.total.items():
                for component in stock[typology].building.components:
                    if component[0] not in output_[typology]:
                        output_[typology][component[0]] = GroupedProducts("temp:", "t")
                    if not component[2]:
                        continue
                    if type(component[4]) is not list:
                        temp_ = calc_one_replacement(
                            component[2].replaceable, LIFETIMES, year - int(year_)
                        )
                        if temp_ != None:
                            output_[typology][component[0]] += temp_ * amount_
        return clean(output_)

    raise TypeError("Not Supported")

def calc_heating_replacement(
    stock: dict, scenario: dict, year: int, detail: Detail
) -> dict | list:
    """This function calculates the replacement demand of the heating systems."""
    return_ = {}

    for country, countryData in stock.items():
        if country not in return_:
            return_[country] = {}
        temp_ = {}
        for key, item in countryData.items():
            temp_[key] = item.development[year].calcHSS(year, scenario)
        for typology_, data_ in temp_.items():
            return_[country][typology_] = [0, 0, 0]
            for amount_ in data_.values():
                # Replacements of old heating systems with old heating systems
                return_[country][typology_][0] += amount_[0]
                # Replacements of old heating systems with new heating systems
                return_[country][typology_][1] += amount_[1]
                # Replacements of new heating systems with new heating systems
                return_[country][typology_][2] += amount_[2]

    return remove_empty(adapt_detail(return_, detail))
