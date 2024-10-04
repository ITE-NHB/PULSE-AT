
"""
lifecycleassessment.py

Authors: Benedict Schwark, Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file includes all things related to lca calculations
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
import logging
from enum import Enum

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

from ..file_handling import import_json
from ..variables import adapt_detail

from ..data_types import GroupedProducts
from ..variables import Detail, Impact

# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------
A1, A4, A5, B6, C2, C3 = ({} for _ in range(6))
REPORT = {"A1-A3": [], "A4": [], "A5": [], 'C2': []}

KW_MJ = 3.6
CURRENT_PROSPECTIVE = None


class LCAStage(Enum):
    """This class deals with LCA Stages."""
    A1 = 1
    A4 = 2
    A5 = 3
    B4 = 4
    B5_IN = 5
    B5_OUT = 6
    B6_1 = 7
    B6_2 = 8
    B6_8 = 9
    B6_COOLING = 10
    B6_HEATING = 11
    B7 = 12
    C2 = 13
    C3_C4 = 14


CONSTRUCTION = 0
DEMOLITION = 1


# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
def import_lca(prospective) -> None:
    """This function imports lca files."""
    logging.debug(
        "Importing LCA data. Old prospect: '%s' new prospect: '%s'",
        CURRENT_PROSPECTIVE,
        prospective
    )
    std = "SSP2-NDC"
    s = prospective if prospective else std
    global A1
    A1 = import_json(title=f"{s}_A1A3", location="data/lca")
    global A4
    A4 = import_json(title=f"{s}_A4", location="data/lca")
    global A5
    A5 = import_json(title=f"{s}_A5C1", location="data/lca")
    global B6
    B6 = import_json(title=f"{s}_B6B7B8", location="data/lca")
    global C2
    C2 = import_json(title=f"{s}_C2", location="data/lca")
    global C3
    C3 = import_json(title=f"{s}_C3C4", location="data/lca")


def calc_lca(
    data: tuple[dict,dict|None,dict|None,dict],
    detail: Detail,
    year: int = 2023,
    prospective: str | None = None,
    impact: Impact = Impact.GWP100,
) -> dict:
    """This function calculates the LCA."""
    year_ = str(year) if prospective else str(2023)

    products, recycling, energy, volume = data

    global CURRENT_PROSPECTIVE
    if CURRENT_PROSPECTIVE != prospective or not A1:
        import_lca(prospective=prospective)
    CURRENT_PROSPECTIVE = prospective

    return_ = {}
    if not recycling:
        return_["A1-A3"] = adapt_detail(
            recursive_lca(
                products["construction"], kind=LCAStage.A1, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["A4"] = adapt_detail(
            recursive_lca(
                products["construction"], kind=LCAStage.A4, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["A5"] = adapt_detail(
            recursive_lca(
                products["construction"], kind=LCAStage.A5, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
    else:
        return_["A1-A3"] = adapt_detail(
            recursive_lca(
                recycling["construction"], kind=LCAStage.A1, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["A4"] = adapt_detail(
            recursive_lca(
                recycling["construction"], kind=LCAStage.A4, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["A5"] = adapt_detail(
            recursive_lca(
                recycling["construction"], kind=LCAStage.A5, year=year_, impact=impact
            ),
            goal_detail=detail,
        )

    return_["A5 - Volume"] = volume_lca(
        volume["construction"], year, CONSTRUCTION, detail, impact=impact
    )
    return_["A5"] = merge_dicts(return_["A5"], return_["A5 - Volume"])
    del return_["A5 - Volume"]
    return_["B1"] = {}
    return_["B2"] = {}
    return_["B3"] = {}

    if not recycling:
        return_["B4"] = adapt_detail(
            recursive_lca(
                products["replacement"], kind=LCAStage.B4, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["B5 - In"] = adapt_detail(
            recursive_lca(
                products["refurbishment in"],
                kind=LCAStage.B5_IN,
                year=year_,
                impact=impact,
            ),
            goal_detail=detail,
        )
        return_["B5 - Out"] = adapt_detail(
            recursive_lca(
                products["refurbishment out"],
                kind=LCAStage.B5_OUT,
                year=year_,
                impact=impact,
            ),
            goal_detail=detail,
        )
    else:
        return_["B4"] = adapt_detail(
            recursive_lca(
                recycling["replacement in"], kind=LCAStage.B4, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["B5 - In"] = adapt_detail(
            recursive_lca(
                recycling["refurbishment in"],
                kind=LCAStage.B5_IN,
                year=year_,
                impact=impact,
            ),
            goal_detail=detail,
        )
        return_["B5 - Out"] = adapt_detail(
            recursive_lca(
                recycling["refurbishment out"],
                kind=LCAStage.B5_OUT,
                year=year_,
                impact=impact,
            ),
            goal_detail=detail,
        )

    return_["B5"] = merge_dicts(return_["B5 - In"], return_["B5 - Out"])
    del return_["B5 - In"]
    del return_["B5 - Out"]
    if energy:
        return_["B6.1"] = energy_lca(
            energy["electricity"],
            kind=LCAStage.B6_1,
            year=year_,
            detail=detail,
            impact=impact,
        )
        return_["B6.2 & B6.3"] = energy_lca(
            energy["electricity"],
            kind=LCAStage.B6_2,
            year=year_,
            detail=detail,
            impact=impact,
        )
        return_["B6 - Heat"] = energy_lca(
            energy["heating"],
            kind=LCAStage.B6_HEATING,
            year=year_,
            detail=detail,
            impact=impact,
        )
        return_["B6 - Cool"] = energy_lca(
            energy["cooling"],
            kind=LCAStage.B6_COOLING,
            year=year_,
            detail=detail,
            impact=impact,
        )
        return_["B7"] = energy_lca(
            energy["water"], kind=LCAStage.B7, year=year_, detail=detail, impact=impact
        )
    return_["C1"] = volume_lca(
        volume["demolition"], year_, DEMOLITION, detail, impact=impact
    )
    if not recycling:
        return_["C2"] = adapt_detail(
            recursive_lca(
                products["demolition"], kind=LCAStage.C2, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["C3-C4"] = adapt_detail(
            recursive_lca(
                products["demolition"], kind=LCAStage.C3_C4, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
    else:
        return_["C2"] = adapt_detail(
            recursive_lca(
                recycling["demolition"], kind=LCAStage.C2, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
        return_["C3-C4"] = adapt_detail(
            recursive_lca(
                recycling["demolition"], kind=LCAStage.C3_C4, year=year_, impact=impact
            ),
            goal_detail=detail,
        )
    temp_ = truncate_dictionary(return_)
    assert isinstance(temp_, dict)
    return temp_


def not_in(product: str, cat: dict, cat_d: str) -> bool:
    """This function checks if there is a certain product in a category"""
    if product in cat:
        return False
    if product not in REPORT[cat_d]:
        REPORT[cat_d].append(product)
        logging.warning("'%s' not available for '%s'", product, cat_d)
    return True

def check_lca_data(kind, product, year) -> bool:
    """This function checks if all the necessary data is initialized."""
    if kind in [LCAStage.A1, LCAStage.B4, LCAStage.B5_IN]:
        if not_in(product, A1[year], "A1-A3"):
            return False
    if kind in [LCAStage.A4, LCAStage.B4, LCAStage.B5_IN]:
        if not_in(product, A4[year], "A4"):
            return False
    if kind in [LCAStage.A1, LCAStage.A5, LCAStage.B4, LCAStage.B5_IN]:
        if not_in(product, A5[year], "A5"):
            return False
    if kind in [
        LCAStage.A5,
        LCAStage.B4,
        LCAStage.B5_IN,
        LCAStage.B5_OUT,
        LCAStage.C2,
        LCAStage.C3_C4,
    ]:
        if not_in(product, C2[year], "C2"):
            return False
    if kind in [
        LCAStage.A5,
        LCAStage.B4,
        LCAStage.B5_IN,
        LCAStage.B5_OUT,
        LCAStage.C2,
        LCAStage.C3_C4,
    ]:
        if not_in(product, C3[year], "C3"):
            return False
    return True

def calc_product_lca(
    product: str,
    quantity: float | int,
    year: str,
    kind: LCAStage,
    impact: Impact,
) -> float:
    """This function calculates the lca for on product"""
    return_ = 0

    if not check_lca_data(kind, product, year):
        return 0

    in_multiplier_ = 0
    out_multiplier_ = 0

    # CREATING A MULTIPLIER
    if kind in [LCAStage.A1, LCAStage.A4, LCAStage.B4, LCAStage.B5_IN]:
        in_multiplier_ = 1 + A5[year][product]
    if kind in [LCAStage.A5, LCAStage.B5_IN]:
        out_multiplier_ = A5[year][product]
    if kind in [LCAStage.B4]:
        out_multiplier_ = 1 + A5[year][product]
    if kind in [LCAStage.C2, LCAStage.C3_C4, LCAStage.B5_OUT]:
        out_multiplier_ = 1

    # ADDING THE IMPACT CATEGORIES
    if kind in [LCAStage.A1, LCAStage.B4, LCAStage.B5_IN]:
        return_ += A1[year][product][impact.value] * quantity * in_multiplier_
    if kind in [LCAStage.A4, LCAStage.B4, LCAStage.B5_IN]:
        return_ += A4[year][product][impact.value] * quantity * in_multiplier_
    if kind in [LCAStage.A5, LCAStage.B4, LCAStage.B5_IN, LCAStage.C2, LCAStage.B5_OUT]:
        return_ += C2[year][product][impact.value] * quantity * out_multiplier_
    if kind in [
        LCAStage.A5,
        LCAStage.B4,
        LCAStage.B5_IN,
        LCAStage.C3_C4,
        LCAStage.B5_OUT,
    ]:
        return_ += C3[year][product][impact.value] * quantity * out_multiplier_

    return return_


def recursive_lca(group: dict, kind: LCAStage, year: str, impact: Impact) -> dict:
    """This function recusively calculates the lca of a dict."""
    r = {}
    for key, data in group.items():
        if isinstance(data, dict):
            r[key] = recursive_lca(data, kind, year, impact)
        elif isinstance(data, (int, float)):
            r[key] = calc_product_lca(key, data, year, kind, impact)
        elif isinstance(data, GroupedProducts):
            r[key] = {}
            for product, amount in data.dictify().items():
                r[key][product] = calc_product_lca(product, amount, year, kind, impact)
        else:
            raise TypeError(f"Wrong type in recursiceLCA: {type(data)}")
    return r


def volume_lca(volume, year, kind: int, detail: Detail, impact: Impact) -> float | dict:
    """This function calculates the volume of a dict."""
    if kind == CONSTRUCTION:
        key_ = "Construction"
    elif kind == DEMOLITION:
        key_ = "Demolition"
    else:
        raise KeyError

    return_ = {}

    for country, country_data in volume.items():
        return_[country] = {}
        for typology, typo_data in country_data.items():
            return_[country][typology] = {
                key_: A5[str(year)][key_][impact.value] * typo_data
            }
    if detail == Detail.PRODUCT:
        return return_
    return adapt_detail(return_, detail)


def merge_dicts(dict1: float | int | dict, dict2: float | int | dict):
    """This function merges two dictionaries."""
    if (isinstance(dict1, (float, int)) and (
        isinstance(dict2, (float, int)))
    ):
        return dict1 + dict2
    if not dict1:
        return dict2
    if not isinstance(dict1, dict):
        raise TypeError()
    if not isinstance(dict2, dict):
        raise TypeError()
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def truncate_dictionary(data):
    """This function truncates a dictionary."""
    if isinstance(data, dict):
        return {
            k: truncate_dictionary(v)
            for k, v in data.items()
            if v and truncate_dictionary(v)
        }
    if isinstance(data, list):
        return [truncate_dictionary(v) for v in data if v and truncate_dictionary(v)]
    return data


def energy_lca(
    energy: dict,
    kind: LCAStage,
    year: int | str,
    detail: Detail,
    impact: Impact,
) -> dict:
    """This function calculates the lca of an energy dictionary."""
    return_ = {}

    for country, country_data in energy.items():
        return_[country] = {}
        for typology, typo_data in country_data.items():
            return_[country][typology] = {}
            if kind == LCAStage.B6_1:
                return_[country][typology] = {
                    "B6.1": B6[str(year)]["B6.1"][impact.value]
                    * typo_data["B6.1"]
                    * KW_MJ
                }
            if kind == LCAStage.B6_2:
                return_[country][typology] = {
                    "B6.2 & B6.3": B6[str(year)]["B6.2 & B6.3"][impact.value]
                    * typo_data["B6.2"]
                    * KW_MJ
                }
            if kind == LCAStage.B6_COOLING:
                return_[country][typology] = {
                    "Cooling": B6[str(year)]["Final Space Cooling"][impact.value]
                    * typo_data["cooling"]
                    * KW_MJ
                }
            if kind == LCAStage.B6_HEATING:
                return_[country][typology] = {
                    key_: B6[str(year)][key_][impact.value] * data_ * KW_MJ
                    for key_, data_ in typo_data.items()
                }
            if kind == LCAStage.B7:
                return_[country][typology] = {
                    "Water User": B6[str(year)]["Water Use"][impact.value]
                    * typo_data["water"]
                }
    if detail in (Detail.PRODUCT, Detail.COMPONENT):
        return return_
    temp_ = adapt_detail(return_, detail)
    assert isinstance(temp_,dict)
    return temp_
