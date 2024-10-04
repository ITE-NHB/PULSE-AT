# --------------------------------------------------------------------------------------------------
# code.py
#
# Author: Benedict Schwark 
# Supervision: Nicolas Alaux
# Other contributors: See README.md
# License: See LICENSE.md
#
# Description: This file deals with the data type code
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# VARIABLES
from ..variables import CONSTRUCTION_TYPE, STANDARD

# CLASSES
from ..variables import ObjectType


# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class Code:
    """A class for dealing with the codes for different classes."""

    def __init__(self, code: str, kind: ObjectType) -> None:
        """This function initiates the code class"""
        self.code: str = code
        if kind == ObjectType.PRODUCT:
            assert (
                len(code) == 6
            ), f'ERROR: Code creation for product "{code}" failed. Length has to be 6, was {len(code)}'
            self.category: str = code[:2]
            self.subcategory: int = int(code[3])
            self.designation: int = int(code[4:])
            return
        if kind == ObjectType.COMPONENT:
            assert (
                len(code) == 8
            ), f'ERROR: Code creation for component "{code}" failed. Length has to be 8, was {len(code)}'
            self.category: str = code[:3]
            self.nr: int = int(code[4:6])
            self.kind: str = code[7]
            return
        if kind == ObjectType.BUILDING:
            assert (
                len(code) == 19
            ), f'ERROR: Code creation for building "{code}" failed. Length has to be 19, was {len(code)}'
            self.country: str = code[:2]
            self.typology: str = code[3:6]
            self.years: tuple[int, int] = (int(code[7:11]), int(code[12:16]))
            self.yearRange: range = range(int(code[7:11]), int(code[12:16]) + 1)
            self.constructionType: str = CONSTRUCTION_TYPE[int(code[17])]
            self.energyStandard: str = STANDARD[int(code[18])]
            return
        raise (KeyError)

    def __repr__(self) -> str:
        """This function turns the code class into a machine readable representation, by returning its code in the form of a string"""
        return self.code

    def __eq__(self, other: str | object) -> bool:
        """This function returns true if the input string or code object is the same as the code object"""
        return str(self) == str(other)

    def __str__(self) -> str:
        return self.code
