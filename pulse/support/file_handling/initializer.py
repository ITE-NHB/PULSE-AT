"""
importer.py

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the import of various different file types and data structures.
"""

# --------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------
import logging

from pulse.support.file_handling.importer import import_csv, int_list

# --------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------

# VARIABLES
from ..variables import PRODUCT_IDs

# CLASSES
from ..data_types import Product, Component, Building, Scenario

# --------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------

def de_list(to_shorten: list, r):
    """This function takes a list and pulls out the first object if it is the only object in the
    list."""
    if r == " U-value default (W/m2K) ":
        return to_shorten
    return to_shorten[0] if not any(to_shorten[1:]) else to_shorten


def col_group(data: list):
    """This function groups the unsorted dictionary from the import together based on columns."""
    output = []
    for row in data:
        if not row.get(next(iter(row))):
            output[-1] = {
                key: obj + [dataPoint]
                for ((key, obj), dataPoint) in zip(output[-1].items(), row.values())
            }
        else:
            if output:
                output[-1] = {r: de_list(d, r) for r, d in output[-1].items()}
            output.append({r: [d] for r, d in row.items()})
    output[-1] = {r: de_list(d, r) for r, d in output[-1].items()}
    return output


def row_group(data: list):
    """This function groups the unsorted dictionary from the import together based on rows.
    It is only used for Scenarios and partially hardcoded."""
    output = []
    current_scenario = None
    for row in data:
        model = row.pop(next(iter(row)))
        if model == "END":
            break
        assert model == "TUG", "The model has to be TU Graz"
        if row.get(next(iter(row))) != current_scenario:
            current_scenario = row.get(next(iter(row)))
            output.append(
                {
                    "Scenario": row["Scenario"],
                    "Region": row["Region"],
                    "Years": range(int_list(row, 4), int_list(row, -1) + 1),
                    "Variable": {},
                }
            )
        output[-1]["Variable"][row["Variable"]] = {
            "Data": list(row.values())[4:],
            "Unit": row["Unit"],
        }
    return output


def create_objects(
    data: list[dict], kind: str, version: str = "Pulse"
) -> dict:
    """This function creates objects based on a set of data dictionaries and the specifier
    which one it shoud be (Products,Components,Buildings,Stock or Scenarios)."""
    logging.debug("Creating the '%s' objects in the version '%s'", kind, version)
    match kind:
        case "Products":
            return {
                item.get(next(iter(data[0]))): Product(**item)
                for item in data
                if item.get(next(iter(data[0])))
            }
        case "Components":
            return {
                item.get(next(iter(data[0]))): Component(**item)
                for item in col_group(data)
            }
        case "Buildings":
            return {
                item.get(next(iter(data[0]))): Building(**item)
                for item in col_group(data)
            } 
        case "Scenarios":
            return {
                item.get(next(iter(data[0]))): Scenario(**item)
                for item in row_group(data)
            }
        case _:
            raise KeyError(
                f"The key {kind} is not a valid option for object creation!"
            )


def add_alt_components(components: list[str], requirements: list[str]) -> list[str]:
    """This function adds potential alternate components to crossreference with the actual
    components later."""
    for requirement in requirements:
        components = components + [f"{comp[:-1]}{requirement}" for comp in components]
    return components


def remove_unused_from_dict(full_dict: dict, selection: list) -> tuple[dict, int]:
    """This function takes a dictionary and removes the instances of the dictionary that are
    not in the selection list. It also returns the amount of removed elements."""
    return {key: data for key, data in full_dict.items() if key in selection}, len(
        full_dict
    ) - len({key: data for key, data in full_dict.items() if key in selection})


def remove_unused(data, alt_requirements, u_requirements) -> tuple[int, int]:
    """This function is an optional removal of all unused products and components."""
    assert (
        len(data) == 4
    ), f"Invalid length of data - should be 4 is {len(data)}"
    (
        used_products,
        used_components,
    ) = (
        [],
        [],
    )
    for scenario in data[3].values():
        scenario.getAltRequirements(**alt_requirements)
    for building in data[2].values():
        building.get_used_components(used_components)
        building.get_u_requirements(u_requirements)

    used_components = add_alt_components(used_components, alt_requirements["components"])

    data[1], c_reduction = remove_unused_from_dict(data[1], used_components)
    for component in data[1].values():
        component.get_used_products(used_products)
    data[0], p_reduction = remove_unused_from_dict(data[0], used_products)
    return c_reduction, p_reduction


def import_data(detail: dict, **kwargs):
    """This function imports data from the four data sources"""
    data = [
        create_objects(import_csv(title=arg), kind) for kind, arg in kwargs.items()
    ] 

    alt_requirements = {"basement": [False], "components": []}

    u_requirements = {}
    c_reduction, p_reduction = remove_unused(data, alt_requirements, u_requirements)

    logging.info("%d products removed from the calculation",p_reduction)
    logging.info("%d components removed from the calculation",c_reduction)

    products, components, buildings, scenarios = data

    for product in products.values():
        product.getIDTranslation(PRODUCT_IDs)

    for component in components.values():
        component.link_products(products)
        component.calc_products(u_requirements, components)

    for building in buildings.values():
        building.link_components(components)
        building.calc_products(alt_requirements, components, detail["products"])

    return products, components, buildings, scenarios
