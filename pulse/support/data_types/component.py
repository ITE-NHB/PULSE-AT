"""
component.py
------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the data type component. Its main purpose is the introduction
of the Component class.
"""
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# VARIABLES
from ..variables import LANGUAGE

# CLASSES
from .code import Code
from .layered_products import LayeredProducts
from .grouped_products import GroupedProducts
from ..variables import ObjectType


# --------------------------------------------------------------------------------------------------
# Variables
# --------------------------------------------------------------------------------------------------

R_VALUES = {
    "AW-v": (0.17, 1),
    "AW": (0.26, 1),
    "BW": (0.13, 0.8),
    "DS": (0.20, 1),
    "FD-v": (0.20, 1),
    "FD": (0.14, 1),
    "EB": (0.17, 0.5),
    "AD": (0.20, 0.9),
    "KD": (0.34, 0.5),
}


# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class Component:
    """A class for components. Each component will get one instance of this class."""

    def __init__(self, **kwargs) -> None:
        """This function initializes the product class. It is initialized with the kwargs."""
        self.code: Code = Code(kwargs.pop(next(iter(kwargs))), ObjectType.COMPONENT)
        self.name: str = kwargs[f"Name ({LANGUAGE})"]
        self.ventilated: bool = (
            "ventilation" in self.name and not "no rear ventilation" in self.name
        )
        self.pitched: bool = "pitched" in self.name
        self.kind: str = kwargs["Type"]
        self.orientation: str = kwargs["Orientation"]
        self.products: LayeredProducts = LayeredProducts(
            kwargs["Product ID"],
            kwargs["Thickness for layered (cm), unit for non-layered"],
            kwargs["Percentage"],
            kwargs["Replaceable"],
            component=self.code,
            layered=True if self.kind == "Layered" else False,
        )
        self.grouped_products: GroupedProducts | None = None
        self.replaceable_products: GroupedProducts | None = None
        self.refurbishment_products: GroupedProducts | None = None

    def __repr__(self) -> str:
        """This function overwrites the repr for the Component class."""
        return f'Component Object "{self.code}"'

    def get_used_products(self, usedProducts: list) -> None:
        """This function extracts the products used in a given component and adds them to the used
        products list."""
        for product in self.products:
            if product[0] not in usedProducts:
                usedProducts.append(product[0])

    def link_products(self, allProducts: dict) -> None:
        """This function links the product objects to the component."""
        self.products.link_products(allProducts)

    def get_u_type(self, uType, ventilated, pitched):
        """This function adapts the uType (which is used to specify the RSI and RSE values) based
        on wether a component is ventilated and or pitched."""
        if ventilated:
            return f"{uType}-v"
        if pitched:
            return "DS"  # = Dach Schräge
        return uType

    def sort_layers_by_insulation_value(
        self, rValueDict: dict[str, list[float | list[float]]]
    ) -> list[tuple[str, float, list[float]]]:
        """This function sorts the r value list by the second value and reformats it so it is
        usable for the u value calculation."""
        return sorted(
            [(val[0], key, val[1], val[2], val[3]) for key, val in rValueDict.items()],
            reverse=True,
        )

    def get_additions(
        self, codes: str, value: float, density: list, percentage: list
    ) -> list[tuple[str, float]]:
        """This function formats additions in a way that they can be added to the GroupedProducts
        Object. ("Product ID", Product Quantity)"""
        if len(percentage) == 1:
            return [(codes, value * density[0] / 1000)]
        return [
            (code, value * dens / 1000 * perc / 100)
            for code, dens, perc in zip(codes.split("-"), density, percentage)
        ]

    def adapt_unit(self, unit: str, multiplier: int | float) -> str:
        """This function adapts the units for the product to component conversion.
        kg -> t (/1000) for all units and m2/t -> u/t for doors."""
        unit = unit.replace("kg", "t")
        if multiplier == 1:
            return unit

        if unit == "t/u":
            return unit
        unit = unit.replace("m2", "u")
        return unit

    def calc_layered_products(self, requirements, components) -> None:
        """This function calculates the products for a given layered component and stores it using a
        GroupedProduct object"""
        self.grouped_products = GroupedProducts(f"{self.code}", "t/m2")
        self.replaceable_products = GroupedProducts(f"{self.code}", "t/m2")
        self.refurbishment_products = GroupedProducts(f"{self.code}", "t/m2")

        removable = True
        for _, product in enumerate(self.products):
            assert isinstance(self.grouped_products, GroupedProducts)
            if isinstance(product[1], tuple):
                continue
            self.grouped_products += (
                product[1].code,
                product[1].density[0]
                / 1000
                * product[2][0]
                / 100
                * product[3][0]
                / 100,
            )
            if product[4]:
                assert isinstance(self.replaceable_products, GroupedProducts)
                self.replaceable_products += (
                    product[1].code,
                    product[1].density[0]
                    / 1000
                    * product[2][0]
                    / 100
                    * product[3][0]
                    / 100,
                )
            if str(self.code)[0] == "A" and removable:
                if not product[4]:
                    removable = False
                    continue
                assert isinstance(self.refurbishment_products, GroupedProducts)
                self.refurbishment_products += (
                    product[1].code,
                    product[1].density[0]
                    / 1000
                    * product[2][0]
                    / 100
                    * product[3][0]
                    / 100,
                )

        if str(self.code) not in requirements:
            return
        uTypes, uValues = requirements.pop(str(self.code))
        rValues = self.products.get_r_values()
        for uType in uTypes:
            rsi_ = R_VALUES[self.get_u_type(uType, self.ventilated, self.pitched)][0]
            u_ = 1 / ((sum([r[0] for r in rValues.values()])) + rsi_)
            uValues.sort()
            for value in uValues:
                if not isinstance(value, tuple):
                    difference = (1 / (u_)) - (1 / value)
                else:
                    difference = (1 / (u_)) - (1 / value[1])
                    if difference > 0:
                        pass  # For debugging
                if difference <= 0:
                    continue
                sortedLayers = self.sort_layers_by_insulation_value(rValues)
                self.grouped_products.addAddition(f"test")
                self.grouped_products.addAddition(
                    f"U-Value: {value if not isinstance(value, tuple) else value[1]}"
                )
                for layer in sortedLayers:
                    assert layer and len(layer) == 5
                    r_, comp_, thick_, density_, percentage_ = layer
                    if difference < r_:
                        for addition in self.get_additions(
                            comp_,
                            -((thick_ / 100) * (difference / r_)),
                            density_,
                            percentage_,
                        ):
                            self.grouped_products[
                                f"U-Value: {value if not isinstance(value, tuple) else value[1]}"
                            ] += addition
                            if str(self.code)[0] == "R":
                                pass
                        break
                    else:
                        difference -= r_
                        for addition in self.get_additions(
                            comp_, -(thick_ / 100), density_, percentage_
                        ):
                            self.grouped_products[
                                f"U-Value: {value if not isinstance(value, tuple) else value[1]}"
                            ] += addition

    def calc_non_layered_products(self):
        """This function calculates the products for a given non-layered component and stores it 
        using a GroupedProduct object"""
        match self.code.category:
            case "Win" | "PEL" | "GAS" | "OIL" | "DIH" | "HEP" | "ELE":
                self.grouped_products = GroupedProducts(f"{self.code}", "t/m2")
                self.replaceable_products = GroupedProducts(f"{self.code}", "t/m2")
                self.refurbishment_products = GroupedProducts(f"{self.code}", "t/m2")
                for product in self.products:
                    self.grouped_products += (
                        product[1].code,
                        product[1].density[0]
                        / 1000
                        * product[2][0]
                        * product[3][0]
                        / 100,
                    )
                    self.replaceable_products += (
                        product[1].code,
                        product[1].density[0]
                        / 1000
                        * product[2][0]
                        * product[3][0]
                        / 100,
                    )
                    self.refurbishment_products += (
                        product[1].code,
                        product[1].density[0]
                        / 1000
                        * product[2][0]
                        * product[3][0]
                        / 100,
                    )
            case "Doo" | "SAN" | "ELI":
                self.grouped_products = GroupedProducts(f"{self.code}", "variable")
                self.replaceable_products = GroupedProducts(f"{self.code}", "variable")
                self.refurbishment_products = GroupedProducts(f"{self.code}", "t/m2")
                for product in self.products:
                    self.grouped_products.addAddition(f"{product[0]}")
                    self.replaceable_products.addAddition(f"{product[0]}")
                    self.refurbishment_products.addAddition(f"{product[0]}")
                    self.grouped_products[f"{product[0]}"] += (
                        product[1].code,
                        product[1].density[0]
                        / 1000
                        * product[2][0]
                        * product[3][0]
                        / 100,
                    )  # Double Check
                    self.replaceable_products[f"{product[0]}"] += (
                        product[1].code,
                        product[1].density[0]
                        / 1000
                        * product[2][0]
                        * product[3][0]
                        / 100,
                    )
                    # removes SAN and ELI from refurbishment
                    if self.code.category in ('SAN','ELI'): continue
                    self.refurbishment_products[f"{product[0]}"] += (
                        product[1].code,
                        product[1].density[0]
                        / 1000
                        * product[2][0]
                        * product[3][0]
                        / 100,
                    )
            case _:
                raise TypeError(self.code.category)

    def calc_products(self, requirements: dict, components) -> None:
        """This function calculates the products for a given component and stores it using a
        GroupedProduct object."""
        if self.kind == "Layered":
            return self.calc_layered_products(
                requirements=requirements, components=components
            )
        if self.kind == "Non-layered":
            return self.calc_non_layered_products()
        raise TypeError
