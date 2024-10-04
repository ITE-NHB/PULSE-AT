"""
energy.py
---------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file is regarding all the energy calculations
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# VARIABLES
from ..variables import NO_B8

# FUNCTIONS
from ..variables import adapt_detail, get_share_of_used

# CLASSES
from ..variables import Detail

# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
EFFICIENCY = [
    {
        "gas central heating, standard boiler": 0.8,
        "gas central heating, condensing boiler": 0.8,
        "gas central heating, condensing boiler, with solar thermal": 0.8,
        "wood central heating": 0.72,
        "pellets central heating, with solar thermal": 0.72,
        "oil central heating, standard boiler": 0.76,
        "oil central heating, condensing boiler": 0.76,
        "single stoves oil": 0.76,
        "district heating": 0.91,
        "pellets central heating": 0.72,
        "electric direct heating, with solar thermal": 1,
        "electric direct heating": 1,
        "heat pump": 3.0,
    },
    {
        "district heating": 0.92,
        "gas central heating, standard boiler": 0.93,
        "gas central heating, condensing boiler": 0.93,
        "gas central heating, condensing boiler, with solar thermal": 0.93,
        "oil central heating, standard boiler": 0.90,
        "oil central heating, condensing boiler": 0.90,
        "single stoves oil": 0.90,
        "wood central heating": 0.75,
        "pellets central heating": 0.75,
        "pellets central heating, with solar thermal": 0.75,
        "electric direct heating, with solar thermal": 1,
        "electric direct heating": 1,
        "heat pump": 3.3,
    },
]

ALL = 0
USE = 1


# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
def calc_heating(
    stock: dict, year: int, scenario: dict, *, detail: Detail
) -> float | dict:
    """This function calculates the heating demand."""

    return_ = {}

    for country, country_data in stock.items():
        return_[country] = {}
        for typology_, stock_item in country_data.items():
            return_[country][typology_] = {}
            distribution_ = combine(
                stock_item.development[year].number.listify(),
                stock_item.development[year].number.listify_hss(),
            )
            share_of_used = get_share_of_used(
                stock_item.building.shared_of_used,
                scenario["use of empty"],
                stock_item.building.use,
                stock_item.building.code,
            )

            for renolvl, _distribution_ in enumerate(distribution_):
                house_heating_demand = (
                    (
                        stock_item.building.heating_demand[renolvl]
                        + stock_item.building.heating_demand[4]
                    )
                    * (
                        1
                        + (
                            scenario["NFA"]["heated"]
                            if scenario["NFA"]["heated"]
                            else 0
                        )
                    )
                    * stock_item.building.floor_area["Net Heated"]
                )
                for old_, hss_ in enumerate(
                    stock_item.building.hs.getHeatingsystems(_distribution_)
                ):
                    for heating_system, amount_ in hss_.items():
                        if heating_system not in return_[country][typology_]:
                            return_[country][typology_][heating_system] = 0
                        return_[country][typology_][heating_system] += (
                            amount_
                            * house_heating_demand
                            / EFFICIENCY[0 if old_ < 1 else 1][heating_system]
                            * share_of_used
                        )
    return adapt_detail(return_, detail)


def calc_cooling(
    stock: dict, year: int, scenario: dict, *, detail: Detail
) -> float | dict:
    """This function calcultes the cooling demand."""
    return_ = {}
    for country, country_data in stock.items():
        if country in return_:
            raise TypeError("What the heck")
        return_[country] = {}
        for typology_, stock_item in country_data.items():
            return_[country][typology_] = {}
            number_ = sum(stock_item.development[year].number.total.values())
            share_of_used = get_share_of_used(
                stock_item.building.shared_of_used,
                scenario["use of empty"],
                stock_item.building.use,
                stock_item.building.code,
            )
            house_cooling_demand = (
                stock_item.building.cooling_consumption
                * (1 + (scenario["NFA"]["cooled"] if scenario["NFA"]["cooled"] else 0))
                * stock_item.building.floor_area["Net Cooled"]
            )
            return_[country][typology_] = {
                "cooling": house_cooling_demand * share_of_used * number_
            }
    return adapt_detail(return_, detail)


def calc_water(
    stock: dict, year: int, scenario: dict, *, detail: Detail
) -> float | dict:
    """This function calcultes the cooling demand."""
    return_ = {}
    for country, country_data in stock.items():
        return_[country] = {}
        for typology_, stock_item in country_data.items():
            number_ = sum(stock_item.development[year].number.total.values())
            share_of_used = get_share_of_used(
                stock_item.building.shared_of_used,
                scenario["use of empty"],
                stock_item.building.use,
                stock_item.building.code,
            )
            house_water_demand = stock_item.building.water_use
            return_[country][typology_] = {
                "water": house_water_demand * share_of_used * number_
            }
    return adapt_detail(return_, detail)


def calc_electricity(
    stock: dict, year: int, scenario: dict, *, detail: Detail
) -> float | dict:
    """This function calcultes the cooling demand."""
    assert isinstance(stock, dict)
    assert isinstance(year, int)
    assert isinstance(scenario, dict)
    assert isinstance(detail, Detail)

    return_ = {}
    for country, country_data in stock.items():
        return_[country] = {}
        for typology_, stock_item in country_data.items():
            return_[country][typology_] = {}
            building_ = stock_item.building
            share_of_used = get_share_of_used(
                building_.shared_of_used,
                scenario["use of empty"],
                building_.use,
                building_.code,
            )
            house_elec_demand = building_.electric_consumption
            heated_area_ = (
                1 + (scenario["NFA"]["heated"] if scenario["NFA"]["heated"] else 0)
            ) * building_.floor_area["Net Heated"]
            for electricity_, amount_ in house_elec_demand.items():
                if electricity_ == "B8" and NO_B8:
                    continue
                return_[country][typology_][electricity_] = (
                    amount_
                    * share_of_used
                    * (heated_area_ if electricity_ != "B8" else 1)
                    * stock_item.get_total(year)
                )

    return adapt_detail(return_, detail)


def combine(a: list, b: list) -> list[list]:
    """This function combines two lists of the same sum into a matrix.
    The Matrix is distributed left to right.\n
    Example:
    a = [100, 10, 10, 100]
    b
    """
    assert sum(a) == sum(b), "The two lists have to have the same sum"
    a_pos, b_pos = 0, 0
    return_ = [[0 for _ in b] for _ in a]
    while any(a) and any(b):
        if a[a_pos] > b[b_pos]:
            a[a_pos] -= b[b_pos]
            return_[a_pos][b_pos] += b[b_pos]
            b[b_pos] = 0
            b_pos += 1
        elif a[a_pos] < b[b_pos]:
            b[b_pos] -= a[a_pos]
            return_[a_pos][b_pos] += a[a_pos]
            a[a_pos] = 0
            a_pos += 1
        elif a[a_pos] == b[b_pos]:
            return_[a_pos][b_pos] += a[a_pos]
            a[a_pos] = 0
            b[b_pos] = 0
            a_pos += 1
            b_pos += 1
        else:
            raise KeyError
    return return_
