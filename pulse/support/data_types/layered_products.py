"""
layered_products.py
-------------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the data type code
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
import logging

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Global Variables
# --------------------------------------------------------------------------------------------------
REPORT = []


# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class LayeredProducts:
    """This is a class to deal with layered elements"""

    def __init__(self, *arg, component, layered):
        """This function is the initializer of the LayeredProduct class"""
        self.layered = layered
        self.component: object = component
        self.codes: list = (
            [code for code in arg[0]] if type(arg[0]) is list else [arg[0]]
        )
        self.products: list = []
        self.thickness: list = (
            [(float(thick), "cm" if layered else "nr") for thick in arg[1]]
            if type(arg[1]) is list
            else [(float(arg[1]), "cm")]
        )
        self.percentage: list = (
            [(float(perc) * 100, "%") for perc in arg[2]]
            if type(arg[2]) is list
            else [(float(arg[2]) * 100, "%")]
        )
        self.replaceable: list = [True if r == "TRUE" else False for r in arg[3]]
        assert not (
            round(sum([p[0] for p in self.percentage]), 0) % 100
        ), f"Layered elements for {self.component} are wrong! Add to: {sum([p[0] for p in self.percentage])}"

    def __repr__(self) -> str:
        """This function overwrites the repr for the LayeredProduct class."""
        fullPercentage = 0
        output = "Layered Element\n" if self.layered else "Non-layered Element\n"
        for code, thick, perc in zip(self.codes, self.thickness, self.percentage):
            fullPercentage += perc[0]
            output = (
                f"{output}{code}: {thick[0]:5.2f} cm - {int(perc[0]):3}%"
                if self.layered
                else f"{output}{code}: {thick[0]:5.2f}"
            )
            if round(fullPercentage, 4) == 100:
                output = f"{output}\n"
                fullPercentage = 0
            else:
                output = f"{output} - "
        return output

    def __getitem__(self, pos: int) -> list:
        """This function overwrites the getter for the LayeredProducts class."""
        assert 0 <= pos <= len(self.codes) - 1, f"ERROR: {pos}"
        if self.products:
            return
        return

    def __iter__(self):
        """This function overwrites the iter."""
        if self.products and len(self.products) == len(self.codes):
            for i in range(0, len(self.products)):
                yield [
                    self.codes[i],
                    self.products[i],
                    self.thickness[i],
                    self.percentage[i],
                    self.replaceable[i],
                ]
        else:
            for i in range(0, len(self.codes)):
                yield [
                    self.codes[i],
                    self.thickness[i],
                    self.percentage[i],
                    self.replaceable[i],
                ]

    def link_products(self, products: dict) -> None:
        """This function links the LayeredProducts object to the Products object."""
        for code in self.codes:
            if code in products:
                self.products.append(products[code])
            else:
                logging.warning("Code %s is not in products", code)
        return None

    def get_r_values(self) -> dict:
        """This function returns a list of R-Values"""
        output, totalPerc, tempCode, tempConduct, densities = {}, [], "", [], []
        for code, product, thickness, percentage in zip(
            self.codes, self.products, self.thickness, self.percentage
        ):
            if not product.conductivity:
                if product.code not in REPORT:
                    REPORT.append(product.code)
                    logging.warning(f"{product.code} does not have a conductivity")
                continue

            if not tempCode:
                tempCode = f"{code}"
            else:
                tempCode = f"{tempCode}-{code}"

            tempConduct.append((product.conductivity, percentage[0]))
            totalPerc.append(percentage[0])
            densities.append(product.density[0])
            if round(sum(totalPerc)) != 100:
                continue
            output[tempCode] = [0, thickness[0], densities, totalPerc]
            for conductivity in tempConduct:
                output[tempCode][0] += (
                    (thickness[0] / 100) / conductivity[0] * (conductivity[1] / 100)
                )
            totalPerc, tempCode, tempConduct, densities = [], "", [], []
        return output

    def __len__(self) -> int:
        return len(self.codes)
