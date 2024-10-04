# --------------------------------------------------------------------------------------------------
# product.py
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
from ..variables import LANGUAGE

# CLASSES
from .code import Code
from ..variables import ObjectType

# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class Product:
    """A class for products."""
    def __init__(self, **kwargs) -> None:
        """This function initializes the product class."""
        self.code: object =         Code(kwargs.pop(next(iter(kwargs))), ObjectType.PRODUCT)
        self.name: str =            kwargs[f"Designation ({LANGUAGE})"]
        self.category: str =        kwargs[f"Category ({LANGUAGE})"]
        self.subcategory: str =     kwargs[f"Subcategory ({LANGUAGE})"]
        self.density: tuple =       (float(kwargs["Raw density"] if kwargs["Raw density"] else 0), str(kwargs["Unit"]))
        self.conductivity: float =  float(kwargs["Heat conductivity (W/mK)"] if kwargs["Heat conductivity (W/mK)"] else 0)
        self.diffusion: int =       int(kwargs["Water vapor diffusion"] if kwargs["Water vapor diffusion"] else 0)
        self.serviceLife: int =     int(kwargs["RSL"] if kwargs["RSL"] else 0)

    def __repr__(self) -> str:
        """This function overwrites the repr for the Product class."""
        return f"Product Object \"{self.code}\""
    
    def getIDTranslation(self, collection: dict) -> None:
        """This function maps the product IDs dynamically to their descriptions."""
        if self.code.category not in collection["categories"]: collection["categories"][self.code.category] = self.category
        if f"{self.code.category}_{self.code.subcategory}" not in collection["subcategories"]: collection["subcategories"][f"{self.code.category}_{self.code.subcategory}"] = self.subcategory
        collection["products"][str(self.code)] = self.name
        return None