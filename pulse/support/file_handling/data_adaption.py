"""
data_adaption.py
----------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

This file takes care of a collection of functions for the use of the grapher
"""

CUTOFF = 0.1
from pulse.support.variables import Detail, adapt_detail


def handle_data(data: dict, handle: list) -> dict:
    """This function handles the handler."""
    if isinstance(handle, list):
        return {h: [year[nr] for year in data.values()] for nr, h in enumerate(handle)}


def find_top(data, number, years, selection, country="AT"):
    """This function finds the top of a data set"""
    temp_ = {}
    for typo_ in data[2023]["heating"]["AT"]:
        temp_[typo_] = sum(
            sum(
                (
                    sum(list(data[year][sel][country][typo_].values()))
                    for sel in selection
                )
            )
            for year in years
        )

    return list(
        dict(
            sorted(temp_.items(), key=lambda item: item[1], reverse=True)[:number]
        ).keys()
    )


def title_for_export(title: str) -> str:
    """This function creates an export compatible title.\n
    It turns all capitalized letters to lower case,
    replaces ', ' with '_',
    ' ' with '_', 
    '_-_' with '-',
    '.' with '_' and
    ':' with '_'
    and removes 
    '$',
    '^',
    '(' and
    ')'
    """
    return (
        title.lower()
        .replace(", ", "-")
        .replace(" ", "-")
        .replace("---", "-")
        .replace("$", "")
        .replace("^", "")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(":", "-")
        .replace("--","-")
    )


def dict_merge(*dicts) -> dict:
    """This function merges a number of dictionaries."""
    return_ = {}
    for d in dicts:
        for key, value in d.items():
            if (
                key in return_
                and isinstance(return_[key], dict)
                and isinstance(value, dict)
            ):
                return_[key] = dict_merge(return_[key], value)
            else:
                return_[key] = value
    return return_


def cummulate(data: dict, depth: int):
    """This function cummulates dictionaries to a specified depth"""
    if not depth:
        return data
    return cummulate(dict_merge(*list(data.values())), depth - 1)


def invert(data: dict | list | int | float) -> dict | list | int | float:
    """This function inverts a given number, dictionary or list."""
    if isinstance(data, int):
        return -data
    if isinstance(data, float):
        return -data
    if isinstance(data, list):
        return [invert(t_) for t_ in data]
    if isinstance(data, dict):
        return {k_: invert(t_) for k_, t_ in data.items()}


def group_products(
    data: dict | None, x: list, detail: int = 2
) -> tuple[dict | None, dict | None]:
    """This functions groups products based on their code"""
    if data == None:
        return None, None
    if detail == 0:
        c_ = 2
    elif detail == 1:
        c_ = 4
    elif detail == 2:
        c_ = 6
    else:
        raise TypeError

    convertedData = {}
    outputData = {}

    if isinstance(data[list(data.keys())[0]][list(data[list(data.keys())[0]].keys())[0]], (float, int)):
        adaptedData = data
    else:
        adaptedData = {
            year: adapt_detail(yData, Detail.GROUPED) for year, yData in data.items()
        }

    for nr, (year, yearData) in enumerate(adaptedData.items()):
        
        for product, quantity in (yearData.dictify() if not isinstance(yearData, dict) else yearData).items():
            product_ = product[:c_]
            if product_ not in outputData:
                outputData[product_] = [0 for _ in adaptedData]
            outputData[product_][nr] += quantity

    total = sum([sum(d) for d in outputData.values()])

    convertedData = {k: outputData[k] for k in sorted(outputData.keys())}

    if detail == 2:
        __convertedData = {}
        for key, cData in convertedData.items():
            if sum(cData) >= total * CUTOFF:
                __convertedData[key] = cData
            else:
                if key[:4] not in __convertedData:
                    __convertedData[key[:4]] = [0 for _ in x]
                __convertedData[key[:4]] = [
                    a + b for a, b in zip(__convertedData[key[:4]], cData)
                ]
        convertedData = {k: __convertedData[k] for k in sorted(__convertedData.keys())}

    if detail == 1 or detail == 2:
        __convertedData = {}
        for key, cData in convertedData.items():
            if sum(cData) >= total * CUTOFF:
                __convertedData[key] = cData
            else:
                if key[:2] not in __convertedData:
                    __convertedData[key[:2]] = [0 for _ in x]
                __convertedData[key[:2]] = [
                    a + b for a, b in zip(__convertedData[key[:2]], cData)
                ]
        convertedData = {k: __convertedData[k] for k in sorted(__convertedData.keys())}
    return convertedData, outputData
