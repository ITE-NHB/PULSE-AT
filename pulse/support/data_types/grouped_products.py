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
from .code import Code
from ..variables import ObjectType
# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class GroupedProducts:
    """A class for groupings of products."""
    def __init__(self, code: str, unit):
        """The initializer for the grouped products."""
        self.code: str =        code
        self.products: dict =   {}
        self.additions: dict =  {}
        self.unit: str =        unit

    def __iadd__(self,other):
        """This function overwrites the i adder (+=) method."""
        if other is None: return self
        if other == 0: return self
        if isinstance(other, tuple):
            code, val = other
            if isinstance(code, str):
                code = Code(code,kind=ObjectType.PRODUCT)
            if code.category not in self.products:
                self.products[code.category] = {}
            if code.subcategory not in self.products[code.category]:
                self.products[code.category][code.subcategory] = {}
            if code.designation not in self.products[code.category][code.subcategory]:
                self.products[code.category][code.subcategory][code.designation] = 0
            self.products[code.category][code.subcategory][code.designation] += val
            return self
        if isinstance(other, GroupedProducts):
            for kind, kindData in other.products.items():
                for group, groupData in kindData.items():
                    for nr, nrData in groupData.items():
                        self += (Code(f"{kind}_{group}{nr:02d}", ObjectType.PRODUCT), nrData)
            return self
        raise TypeError(f"Wrong type: {type(other)}")

    def __isub__(self,other):
        """This function overwrites the i subber (-=) method."""
        if other is None: return self
        if other == 0: return self
        if isinstance(other, tuple):
            code, val = other
            if isinstance(code, str):
                code = Code(code, ObjectType.PRODUCT)
            if code.category not in self.products:
                self.products[code.category] = {}
            if code.subcategory not in self.products[code.category]:
                self.products[code.category][code.subcategory] = {}
            if code.designation not in self.products[code.category][code.subcategory]:
                self.products[code.category][code.subcategory][code.designation] = 0
            self.products[code.category][code.subcategory][code.designation] -= val
            return self
        if isinstance(other, GroupedProducts):
            for kind, kindData in other.products.items():
                for group, groupData in kindData.items():
                    for nr, nrData in groupData.items():
                        self -= (Code(f"{kind}_{group}{nr:02d}", ObjectType.PRODUCT), nrData)
            return self
        raise TypeError(f"Wrong type: {type(other)}")

    def __mul__(self,other):
        """This function overwrites the mupltiplier (*) method."""
        temp = GroupedProducts(self.code, "t/b")
        if isinstance(other, int) or isinstance(other, float):
            for a in self.products:
                for b in self.products[a]:
                    for c, amount in self.products[a][b].items():
                        temp += (f'{a}_{b}{c:02d}', amount * other)
            return temp
        if isinstance(other, list):
            assert other != [0,0], f"{self.code} does not have a specified area for multiplication."
            assert len(other) == len(self.additions ), "ERROR: This should not happen"
            
            for multiplier, addition in zip(other,list(self.additions.values())[1:]):
                temp += addition * multiplier
            return temp
        raise TypeError(f"ERROR: Wrong type: {type(other)}. Can't multiply a grouped product object with this.")

    def __repr__(self) -> str:
        """This function overwrites the repr."""
        output = ''
        for a in self.products:
            for b in self.products[a]:
                for c in self.products[a][b]:
                    output = f'{output}{a}_{b}{c:02d}: {self.products[a][b][c]:10.3f} {self.unit}\n'
        for change in self.additions.values():
            output = f'{output}{str(change)}'
        return f'Grouped Products Object "{self.code}":\n{output}'
    
    def __getitem__(self,_code) -> object:
        """This function overwrites the getter."""
        return self.additions[_code]

    def __setitem__(self,_code, val) -> None:
        """This function overwrites the setter."""
        self.additions[_code] = val

    def addAddition(self, code: str) -> None:
        """"""
        self.additions[code] = GroupedProducts(f"{self.code} - {code}",self.unit)

    def getProducts(self, code) -> dict:
        assert isinstance(code, str)
        if len(code) == 2:
            output = {}
            if code not in self.products: return output
            for b in self.products[code]:
                for c in self.products[code][b]:
                    output[f"{code}_{b}{c:02d}"] =  round(self.products[code][b][c], 5)
            return output
        
        if len(code) == 4:
            output = {}
            if code[:2] not in self.products: return {code : 0}
            if int(code[3]) not in self.products[code[:2]]: return {code : 0}
            for c in self.products[code[:2]][int(code[3])]:
                output[f"{code[:2]}{code[3]}_{c:02d}"] =  round(self.products[code[:2]][int(code[3])][c], 5)
            return output

        if len(code) == 6:
            return ({code : self.products[code[:2]][int(code[3])][int(code[4:])]} if int(code[4:]) in self.products[code[:2]][int(code[3])] else {code : 0}) if int(code[3]) in self.products[code[:2]] else {code : 0}

        raise TypeError

    def dictify(self) -> dict:
        """"""
        output = {}
        for a in self.products:
            for b in self.products[a]:
                for c in self.products[a][b]:
                    output[f"{a}_{b}{c:02d}"] =  round(self.products[a][b][c], 5)
        return output

    def empty(self) -> bool:
        if self.products == {}:
            return True
        return False