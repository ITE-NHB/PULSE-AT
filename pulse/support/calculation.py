"""
calculation.py

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
import logging
import sys

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------
from .data_types import StockItem
from .variables import Detail, Impact
from .calculations.total import total_buildings, calc_volume
from .calculations.demolitions import calc_demolitions
from .calculations.construction import calc_constructions
from .calculations.refurbishments import calc_refurbishments
from .calculations.replacements import calc_heating_replacement
from .calculations.products import calc_products
from .calculations.recycling import calcDemoRecycling, calcConstructionRecycling
from .calculations.energy import (
    calc_heating,
    calc_cooling,
    calc_water,
    calc_electricity,
)
from .calculations.life_cycle_assessment import calc_lca
from .data_types.scenario import Scenario

# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
USE = 1
TYPE_ERROR_MESSAGE = "Wrong type in function {}. Is {} but should be {}!"

# --------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------


def calc_all_numbers(
    stock: dict, scenario: Scenario, detail: Detail
) -> tuple[dict, dict]:
    """This function computes all the number related calculations."""
    logging.info("Calculation of the numbers for scenario '%s'", scenario.name)
    return_num, return_vol = {}, {}
    for year in scenario.years:
        return_num[year] = {}
        return_vol[year] = {}
        for country in stock.values():
            for building in country.values():
                building.newYear(year)
        return_num[year]["total"] = total_buildings(stock, year, detail=detail)
        return_num[year]["demolition"] = calc_demolitions(stock, year, detail=detail)
        return_num[year]["refurbishment"] = calc_refurbishments(
            stock, scenario.getYear(year), year, detail=detail
        )
        return_num[year]["construction"] = calc_constructions(
            stock, scenario.getYear(year), year, detail=detail
        )
        return_num[year]["heating system"] = calc_heating_replacement(
            stock, scenario.getYear(year), year, detail=detail
        )
        return_vol[year]["construction"], return_vol[year]["demolition"] = calc_volume(
            return_num[year]["construction"],
            return_num[year]["demolition"],
            stock,
            detail=detail,
        )
    return return_num, return_vol


def calc_all_products(
    stock: dict,
    scenario: Scenario,
    nums: dict,
    products: dict,
    detail: Detail,
) -> dict:
    """This function computes all product calculations"""
    logging.info(
        "Calculation of the products for scenario '%s' with detail level %s",
        scenario.name,
        str(detail),
    )

    return_pro = {}
    for year in scenario.years:
        return_pro[year] = calc_products(
            stock,
            nums[year],
            products=products,
            scenario=scenario.getYear(year),
            year=year,
            detail=detail,
        )
    return return_pro


def calc_all_recycled(products: dict, scenario: Scenario, detail: Detail) -> dict:
    """This function computes all recycling related calculations."""
    return_ = {}
    for year in scenario.years:
        temp_ = {}
        return_[year] = {}
        temp_["demolition"], return_[year]["demolition"] = calcDemoRecycling(
            products[year]["demolition"], scenario=scenario.getYear(year), detail=detail
        )
        temp_["refurbishment out"], return_[year]["refurbishment out"] = (
            calcDemoRecycling(
                products[year]["refurbishment out"],
                scenario=scenario.getYear(year),
                detail=detail,
            )
        )
        temp_["replacement out"], return_[year]["replacement out"] = calcDemoRecycling(
            products[year]["replacement"],
            scenario=scenario.getYear(year),
            detail=detail,
        )

        return_[year]["construction"] = calcConstructionRecycling(
            products[year]["construction"], temp_["demolition"], detail=detail
        )
        return_[year]["refurbishment in"] = calcConstructionRecycling(
            products[year]["refurbishment in"],
            temp_["refurbishment out"],
            detail=detail,
        )
        return_[year]["replacement in"] = calcConstructionRecycling(
            products[year]["replacement"], temp_["replacement out"], detail=detail
        )

    return return_


def calc_all_energy(stock: dict, scenario: Scenario, detail: Detail) -> dict:
    """This function computes all calculations related to the energy demand."""
    logging.info(
        "Calculation of the energy demand for scenario '%s' with detail %s",
        scenario.name,
        detail,
    )
    return_ene = {}
    for year in scenario.years:
        return_ene[year] = {}
        return_ene[year]["heating"] = calc_heating(
            stock, year, scenario.getYear(year), detail=detail
        )
        return_ene[year]["cooling"] = calc_cooling(
            stock, year, scenario.getYear(year), detail=detail
        )
        return_ene[year]["water"] = calc_water(
            stock, year, scenario.getYear(year), detail=detail
        )
        return_ene[year]["electricity"] = calc_electricity(
            stock, year, scenario.getYear(year), detail=detail
        )
    return return_ene


def calc_all_lca(
    scenario: Scenario,
    products: dict,
    computed_data: tuple[dict | None, dict | None, dict],
    detail: Detail,
    impact: Impact,
) -> dict:
    """This function computes all calculations in relation to the lca."""
    logging.info(
        "Calculation of the lca for scenario '%s' with detail %s", scenario.name, detail
    )

    recycling, energy, volume = computed_data

    return_lca = {}
    for year in scenario.years:
        return_lca[year] = calc_lca(
            data=(
                products[year],
                recycling[year] if recycling else None,
                energy[year] if energy else None,
                volume[year],
            ),
            detail=detail,
            year=year,
            prospective=scenario.prospective,
            impact=impact,
        )

    return return_lca


def calculation(
    objects: tuple[dict, dict],
    scenario: Scenario,
    result,
    detail,
    impact,
):
    """This function groups all calculations"""

    products, buildings = objects

    try:
        stock = {}
        for building, building_data in buildings.items():
            if building_data.country not in stock:
                stock[building_data.country] = {}
            stock[building_data.country][building] = StockItem(
                building_data,
                building_data.use,
                building_data.years,
                building_data.number,
            )

        if detail["numbers"] == Detail.NO_CALC:
            raise NameError("There is no output specified... calculation aborted")

        result["numbers"], result["volume"] = calc_all_numbers(
            stock=stock, scenario=scenario, detail=detail["numbers"]
        )

        if detail["products"] != Detail.NO_CALC:
            result["products"] = calc_all_products(
                stock=stock,
                scenario=scenario,
                nums=result["numbers"],
                products=products,
                detail=detail["products"],
            )

        if detail["recycling"] != Detail.NO_CALC:
            result["recycling"] = calc_all_recycled(
                products=result["products"],
                scenario=scenario,
                detail=detail["recycling"],
            )

        if detail["energy"] != Detail.NO_CALC:
            result["energy"] = calc_all_energy(
                stock=stock, scenario=scenario, detail=detail["energy"]
            )

        if detail["lca"] != Detail.NO_CALC:
            result["lca"] = calc_all_lca(
                scenario=scenario,
                products=result["products"],
                computed_data=(
                    result["recycling"] if "recycling" in result else None,
                    result["energy"] if "energy" in result else None,
                    result["volume"],
                ),
                detail=detail["lca"],
                impact=impact,
            )

    except KeyboardInterrupt:
        result["valid"] = False
        logging.critical(
            "Got interrupted during runtime. Programm terminated ungracefully!"
        )
        sys.exit()
