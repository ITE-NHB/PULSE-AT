"""
construction.py
---------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with all the constructions
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
import logging

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# VARIABLES
from ..variables import TYPOLOGIES

# FUNCTIONS
from ..variables import (
    adapt_detail,
    remove_empty,
    get_share_of_used,
    distribute_fully,
)

# CLASSES
from ..data_types import StockItem
from ..variables import Use, Detail

# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------
NEW_CONSTRUCTION_STATISTIC_RES = {}
NEW_CONSTRUCTION_STATISTIC_NR = {}

INITIAL_SM = 0
INITIAL_POP = 0
NON_RESIDENTIAL_ADJUST = 0.5

# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------


def adapt_stat(ref: dict, new: dict) -> dict:
    """This function adapts statistics to a changed input."""
    # Parameter checking start
    assert round(sum(ref.values()), 5) == 1, "The reference values need to add to 1!"

    empty = True
    for key, val in new.items():
        assert isinstance(key, int) or (
            isinstance(key, str) and key in ["SFH", "TEH", "MFH", "ABL"]
        ), f"Keys has to be integer, is {type(key)}"
        assert (
            key in ref
        ), f"Keys do not match: ref: {list(ref.keys())}, new: {list(new.keys())}"
        if val is not None:
            empty = False
    if empty:
        return ref

    assert (
        sum(new.values()) <= 1
    ), f"The new dictionary cannot have a sum higher than 1. It is: {sum(new.values())}"
    # Parameter checking end

    if len(new) == len(ref):
        return new

    up, down, return_ = 1, 1, {}
    for key, a in ref.items():
        if key in new:
            up -= a
            down -= new[key]
            return_[key] = new[key]
        else:
            return_[key] = 0

    for key, a in ref.items():
        if not ref[key]:
            continue
        if return_[key]:
            continue
        return_[key] = round(a / up * down, 5)
    assert (
        round(sum(return_.values()), 4) == 1
    ), "This Error should not happen - The return values don't add to 1!"
    return return_


def multi_stat(ref: dict, multi: dict) -> dict:
    """This function multiplies statistics to a changed input."""
    empty = True
    for key, val in multi.items():
        assert (
            key in ref
        ), f"Keys do not match: ref: {list(ref.keys())}, new: {list(multi.keys())}"
        if val is not None:
            empty = False
    if empty:
        return ref

    return_ = {}
    for key, a in ref.items():
        return_[key] = a * (1 + multi[key]) if key in multi and multi[key] else a
    return return_


def solve_statistic(ref: dict, new: dict, kind: Use) -> dict:
    """This function solves the impact of scenario specifications."""
    h1_ = {k: d[0] for k, d in ref.items()}
    h2_ = {k: d[0] for k, d in new.items()}
    if kind == Use.RESIDENTIAL:
        return_ = {key: [data] for key, data in adapt_stat(h1_, h2_).items()}
    elif kind == Use.NON_RESIDENTIAL:
        return_ = {key: [data] for key, data in multi_stat(h1_, h2_).items()}
    else:
        raise TypeError
    for key in ref:
        return_[key].append(
            {
                t: adapt_stat(data1, data2)
                for (t, data1), data2 in zip(ref[key][1].items(), new[key][1].values())
            }
        )
    return return_


def calc_initial_pop(stock: dict) -> int:
    """This function calculates the initial population of the stock."""
    return_ = int(
        sum(
            (
                s.building.residents
                * s.building.shared_of_used[0]
                * s.number.get_total()
                if s.building.residents
                else 0
            )
            for s in stock["AT"].values()
        )
        + 0.5
    )
    # return_ = 9_010_982
    logging.info(
        "INITIAL_POP not initialized. Calculation results in %d (Reference: %d)",
        return_,
        9_010_982,
    )
    return return_


def calc_initial_sm(stock: dict) -> float:
    """This function calculates the initial squaremeters in the stock."""
    return_ = (
        sum(
            (
                s.building.floor_area["Net Heated"]
                * s.number.get_total()
                * s.building.shared_of_used[0]
                if s.building.residents
                else 0
            )
            for s in stock["AT"].values()
        )
        / INITIAL_POP
    )
    # return_ = 45.3
    logging.info(
        "INITIAL_SM not initialized. Calculation results in %d (Reference: 45.3)",
        return_,
    )
    return return_


def calc_constructions(
    stock: dict, scenario: dict, year: int, detail: Detail
) -> dict | int:
    """This function calculates the construction for a given year"""
    # return_ = OutputMatrix(detail)
    return_ = {}
    global INITIAL_POP
    if not INITIAL_POP:
        INITIAL_POP = calc_initial_pop(stock)

    global INITIAL_SM
    if not INITIAL_SM:
        INITIAL_SM = calc_initial_sm(stock)

    for country, countryData in stock.items():
        if country not in return_:
            return_[country] = {}

        calc_construction_statistic(Use.RESIDENTIAL, countryData, scenario)
        calc_construction_statistic(Use.NON_RESIDENTIAL, countryData, scenario)

        pop_capacity = sum(get_capacity(countryData, year, scenario))
        pop_demand = int(
            scenario["population"] / INITIAL_SM * scenario["floorArea"] + 0.5
        )
        new_pop = pop_demand - pop_capacity if pop_demand - pop_capacity >= 0 else 0
        pop_distr = distribute_fully(
            new_pop,
            {
                t: NEW_CONSTRUCTION_STATISTIC_RES[t][0]
                for t in TYPOLOGIES["Residential"]
            },
        )
        TEMP_CONSTRUCTION_STATISTIC_RES = solve_statistic(
            NEW_CONSTRUCTION_STATISTIC_RES,
            scenario["new Constr 1"],
            kind=Use.RESIDENTIAL,
        )

        for typology in TYPOLOGIES["Residential"]:
            if not new_pop:
                continue
            number1 = distribute_fully(
                pop_distr[typology],
                TEMP_CONSTRUCTION_STATISTIC_RES[typology][1]["construction"],
            )
            for constr in TEMP_CONSTRUCTION_STATISTIC_RES[typology][1]["construction"]:
                number2 = distribute_fully(
                    number1[constr],
                    TEMP_CONSTRUCTION_STATISTIC_RES[typology][1]["energy"],
                )
                for energy in TEMP_CONSTRUCTION_STATISTIC_RES[typology][1]["energy"]:
                    r = f"AT-{typology}-2010-2022-{constr}{energy}"
                    return_[country][r] = (
                        countryData[r]
                        .development[year]
                        .calcConstruction(
                            year, number=number2[energy], pop=True, scenario=scenario
                        )
                    )

        TEMP_CONSTRUCTION_STATISTIC_NR = solve_statistic(
            NEW_CONSTRUCTION_STATISTIC_NR,
            scenario["new Constr 2"],
            kind=Use.NON_RESIDENTIAL,
        )

        for typology in TYPOLOGIES["Non-residential"]:
            demand_sm = int(
                TEMP_CONSTRUCTION_STATISTIC_NR[typology][0]
                * scenario["population"]
                * (
                    1
                    + ((scenario["floorArea"] / INITIAL_SM) - 1)
                    * NON_RESIDENTIAL_ADJUST
                )
                + 0.5
            )
            supply_sm = int(
                sum(
                    [
                        a if typology in k else 0
                        for k, a in getNumber(
                            countryData,
                            selection=[0, 1],
                            sm=True,
                            year=year,
                            scenario=scenario,
                        ).items()
                    ]
                )
                + 0.5
            )

            number1 = distribute_fully(
                max(demand_sm - supply_sm, 0),
                TEMP_CONSTRUCTION_STATISTIC_NR[typology][1]["construction"],
            )
            for constr in TEMP_CONSTRUCTION_STATISTIC_NR[typology][1]["construction"]:
                number2 = distribute_fully(
                    number1[constr],
                    TEMP_CONSTRUCTION_STATISTIC_NR[typology][1]["energy"],
                )
                for energy in TEMP_CONSTRUCTION_STATISTIC_NR[typology][1]["energy"]:
                    r = f"AT-{typology}-2011-2022-{constr}{energy}"
                    return_[country][r] = (
                        countryData[r]
                        .development[year]
                        .calcConstruction(
                            year, number=number2[energy], sm=True, scenario=scenario
                        )
                    )

    return remove_empty(adapt_detail(return_, detail))


def calc_construction_statistic(kind: Use, stock: dict, scenario: dict) -> None:
    """This function calculates the construction statistic that is used to
    predict the future development."""
    if kind == Use.RESIDENTIAL:
        global NEW_CONSTRUCTION_STATISTIC_RES
        if NEW_CONSTRUCTION_STATISTIC_RES:
            return None

        options = get_capacity(stock, None, scenario)
        NEW_CONSTRUCTION_STATISTIC_RES = {}
        temp = {}

        assert isinstance(options, dict)
        for key, amount in options.items():
            if int(key[7:11]) <= 2001:
                continue
            if key[3:6] not in temp:
                temp[key[3:6]] = [0, {}]
            temp[key[3:6]][0] += amount

        total = sum(n[0] for n in temp.values())

        for key, data in temp.items():

            NEW_CONSTRUCTION_STATISTIC_RES[key] = [0, {}]
            NEW_CONSTRUCTION_STATISTIC_RES[key][0] = data[0] / total if total else 0
            assert isinstance(options, dict)
            relevant = list(filter(lambda a: key in a, options.keys()))
            if not NEW_CONSTRUCTION_STATISTIC_RES[key][1]:
                NEW_CONSTRUCTION_STATISTIC_RES[key][1] = {
                    "energy": {},
                    "construction": {},
                }
            for r in relevant:
                if int(r[7:11]) <= 2001:
                    continue
                if (
                    int(r[17])
                    not in NEW_CONSTRUCTION_STATISTIC_RES[key][1]["construction"]
                ):
                    NEW_CONSTRUCTION_STATISTIC_RES[key][1]["construction"][
                        int(r[17])
                    ] = 0
                if int(r[18]) not in NEW_CONSTRUCTION_STATISTIC_RES[key][1]["energy"]:
                    NEW_CONSTRUCTION_STATISTIC_RES[key][1]["energy"][int(r[18])] = 0
                NEW_CONSTRUCTION_STATISTIC_RES[key][1]["construction"][
                    int(r[17])
                ] += options[r]
                NEW_CONSTRUCTION_STATISTIC_RES[key][1]["energy"][int(r[18])] += options[
                    r
                ]

            total2 = sum(NEW_CONSTRUCTION_STATISTIC_RES[key][1]["energy"].values())

            for e in NEW_CONSTRUCTION_STATISTIC_RES[key][1]["energy"]:
                NEW_CONSTRUCTION_STATISTIC_RES[key][1]["energy"][int(e)] = (
                    NEW_CONSTRUCTION_STATISTIC_RES[key][1]["energy"][e] / total2
                    if total2
                    else 0
                )

            for e in NEW_CONSTRUCTION_STATISTIC_RES[key][1]["construction"]:
                NEW_CONSTRUCTION_STATISTIC_RES[key][1]["construction"][int(e)] = (
                    NEW_CONSTRUCTION_STATISTIC_RES[key][1]["construction"][e] / total2
                    if total2
                    else 0
                )
        return

    if kind == Use.NON_RESIDENTIAL:

        global NEW_CONSTRUCTION_STATISTIC_NR
        if NEW_CONSTRUCTION_STATISTIC_NR:
            return None

        NEW_CONSTRUCTION_STATISTIC_NR = {
            k: a / INITIAL_POP
            for k, a in getNumber(
                stock, detail=False, selection=[0, 1], sm=True, scenario=scenario
            ).items()
        }

        NEW_CONSTRUCTION_STATISTIC_NR = {
            k: [data] for k, data in NEW_CONSTRUCTION_STATISTIC_NR.items()
        }

        options = getNumber(
            stock, detail=True, selection=[0, 1], sm=True, scenario=scenario
        )

        for key in NEW_CONSTRUCTION_STATISTIC_NR:
            NEW_CONSTRUCTION_STATISTIC_NR[key].append(
                {"energy": {}, "construction": {}}
            )
            relevant = list(filter(lambda a: key in a, stock.keys()))
            for r in relevant:
                if int(r[7:11]) <= 2001:
                    continue
                if int(r[18]) not in NEW_CONSTRUCTION_STATISTIC_NR[key][1]["energy"]:
                    NEW_CONSTRUCTION_STATISTIC_NR[key][1]["energy"][int(r[18])] = 0
                if (
                    int(r[17])
                    not in NEW_CONSTRUCTION_STATISTIC_NR[key][1]["construction"]
                ):
                    NEW_CONSTRUCTION_STATISTIC_NR[key][1]["construction"][
                        int(r[17])
                    ] = 0
                NEW_CONSTRUCTION_STATISTIC_NR[key][1]["construction"][
                    int(r[17])
                ] += options[r]
                NEW_CONSTRUCTION_STATISTIC_NR[key][1]["energy"][int(r[18])] += options[
                    r
                ]

            NEW_CONSTRUCTION_STATISTIC_NR[key][1]["energy"] = {
                k: a / sum(NEW_CONSTRUCTION_STATISTIC_NR[key][1]["energy"].values())
                for k, a in NEW_CONSTRUCTION_STATISTIC_NR[key][1]["energy"].items()
            }
            NEW_CONSTRUCTION_STATISTIC_NR[key][1]["construction"] = {
                k: a
                / sum(NEW_CONSTRUCTION_STATISTIC_NR[key][1]["construction"].values())
                for k, a in NEW_CONSTRUCTION_STATISTIC_NR[key][1][
                    "construction"
                ].items()
            }
        return


def get_capacity(stock: dict[str, StockItem], year: int | None, scenario: dict):
    """This function returns the capacity of the building stock. If year is not specified
    it returns the initial capacity"""
    if year is None:
        return_ = {}
        for item in stock.values():
            if item.building.use != "Residential":
                continue
            multiplier = get_share_of_used(
                item.building.shared_of_used,
                scenario["use of empty"],
                item.building.use,
                item.building.code,
            )
            return_[str(item.building.code)] = int(
                item.building.residents * sum(item.number.total.values()) * multiplier
                + 0.5
            )
        return return_
    return_ = []
    for item in stock.values():
        if item.building.use != "Residential":
            continue
        multiplier = get_share_of_used(
            item.building.shared_of_used,
            scenario["use of empty"],
            item.building.use,
            item.building.code,
        )
        return_.append(
            int(
                item.development[year].building.residents
                * sum(item.development[year].number.total.values())
                * multiplier
                + 0.5
            )
        )
    return return_


def getNumber(
    stock: dict[str, StockItem],
    *,
    detail: bool = True,
    year: int = 0,
    selection=[1, 1],
    sm=False,
    scenario: dict,
) -> dict:
    """This function returns the number of buildings."""
    output = {}

    for key, data in stock.items():
        if selection[0] and key[3:6] not in TYPOLOGIES["Residential"]:
            continue
        if selection[1] and key[3:6] not in TYPOLOGIES["Non-residential"]:
            continue

        key_ = key
        if not detail:
            key_ = key[3:6]
        if key_ not in output:
            output[key_] = 0

        multiplier = get_share_of_used(
            data.building.shared_of_used,
            scenario["use of empty"],
            data.building.use,
            data.building.code,
        )

        if year:
            output[key_] += (
                sum(data.development[year].number.total.values())
                if not sm
                else sum(data.development[year].number.total.values())
                * data.building.floor_area["Net Heated"]
                * multiplier
            )
        else:
            output[key_] += (
                sum(data.number.total.values())
                if not sm
                else sum(data.number.total.values())
                * data.building.floor_area["Net Heated"]
                * multiplier
            )
    return output
