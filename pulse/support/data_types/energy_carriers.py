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
from ..variables import distribute_fully

# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class EnergyCarriers:
    """A class for groupings of products."""
    def __init__(self, current, comp_current, share_current, exchange, comp_exchange, share_exchange):
        """This..."""
        self.current = [[a,b,float(c)] for a,b,c in zip(current, comp_current, share_current) if a != '']
        self.currentD = {a:float(c) for a,c in zip(current, share_current) if a != ''}
        self.currentMap = {a:b for a,b in zip(current, comp_current) if a != ''}

        self.exchange = [[a,b,float(c)] for a,b,c in zip(exchange, comp_exchange, share_exchange) if a != '']
        self.exchangeD = {a:float(c) for a,c in zip(exchange, share_exchange) if a != ''}
        self.exchangeMap = {a:b for a,b in zip(exchange, comp_exchange) if a != ''}

    def getHeatingsystems(self, distribution: list | tuple) -> list[dict]:
        """This..."""
        if len(distribution) == 2:
            return [distribute_fully(distribution[0], self.currentD),
                    distribute_fully(distribution[1], self.exchangeD)]
        
        return [distribute_fully(distribution[0], self.currentD),
                distribute_fully(distribution[1], self.currentD),
                distribute_fully(distribution[2], self.exchangeD)]
    def linkComponents(self, components) -> None:
        """This..."""
        self.currentMap = {a:components[b] for a,b in self.currentMap.items()}
        self.exchangeMap = {a:components[b] for a,b in self.exchangeMap.items()}
        return None