# --------------------------------------------------------------------------------------------------
# component.py
#
# Author: Benedict Schwark 
# Supervision: Nicolas Alaux
# Other contributors: See README.md
# License: See LICENSE.md
#
# Description: This file deals with the data type code
# --------------------------------------------------------------------------------------------------

from ..variables import Detail

ALL = (slice(0,0,0), slice(None,None,None))

def recursiveGetter(data: dict, keys: list) -> dict | int | float:
    if len(keys) > 1:
        if keys[0] in ALL:  return {k : recursiveGetter(d, keys[1:]) for k, d in data.items()}
        return recursiveGetter(data[keys[0]], keys[1:])
    if keys[0] in ALL: return data
    return data[keys[0]]

class OutputMatrix:
    def __init__(self, detail: Detail = Detail.GROUPED):
        """This class deals with the multi dimendional output files."""
        assert detail.value >= Detail.GROUPED.value

        self.detail = detail
        self.countries =    [] if detail.value >= Detail.COUNTRY.value else None
        self.typology =     [] if detail.value >= Detail.TYPOLOGY.value else None
        self.components =   [] if detail.value >= Detail.COMPONENT.value else None
        self.products =     [] if detail.value >= Detail.PRODUCT.value else None

        self.data =         {}

    def __getitem__(self, keys) -> any:
        assert len(keys) == self.detail.value - 1
        return recursiveGetter(self.data, keys)

    def __setitem__(self, keys, value) -> None:
        assert len(keys) == self.detail.value - 1
        if self.countries != None and keys[0] not in self.data:
            self.countries.append(keys[0])
            self.data[keys[0]] = {} if self.detail.value > Detail.COUNTRY.value else 0
        if self.typology != None and keys[1] not in self.data[keys[0]]:
            self.typology.append(keys[1])
            self.data[keys[0]][keys[1]] = {} if self.detail.value > Detail.TYPOLOGY.value else 0
        if self.components != None and keys[2] not in self.data[keys[0]][keys[1]]:
            self.components.append(keys[2])
            self.data[keys[0]][keys[1]][keys[2]] = {} if self.detail.value > Detail.COMPONENT.value else 0
        if self.products != None and keys[3] not in self.data[keys[0]][keys[1]][keys[2]]:
            self.products.append(keys[3])
            self.data[keys[0]][keys[1]][keys[2]][keys[3]] = 0
        
        if self.detail == Detail.GROUPED:   self.data = value
        if self.detail == Detail.COUNTRY:   self.data[keys[0]] = value
        if self.detail == Detail.TYPOLOGY:  self.data[keys[0]][keys[1]] = value
        if self.detail == Detail.COMPONENT: self.data[keys[0]][keys[1]][keys[2]] = value
        if self.detail == Detail.PRODUCT:   self.data[keys[0]][keys[1]][keys[2]][keys[3]] = value
        return