"""
globals.py
----------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

import os
from enum import Enum

# GLOBAL SWITCHES
NO_B8 = True


# GLOBAL VARIABLES THAT ARE USED SYSTEM WIDE AND SHOULD ONLY BE SET ONCE
INDICATOR = 3
INDICATOR_NAMES = None
TERMINAL_WIDTH, _ = os.get_terminal_size()
PROGRESS_BAR = None
CURRENT_PROSPECTIVE = None
VERSION = None
NUMBERS = range(1)

# STATIC INFORMATION THAT IS USED SYSTEM WIDE
PRODUCT_IDs = {"categories":{}, "subcategories":{}, "products":{}}

TYPOLOGIES = {
    'Residential':("SFH","TEH","MFH","ABL"),
    'Non-residential':("OFF","TRA","EDU","HEA","HOR","OTH")
}

GRAPH_OPTIONS = {
    "numbers" : ['total', 'existent', 'subgroup'],
    "products" : ['total', 'category', 'top'],
    "energy" : ['category', 'hss', 'heatmap', 'top'],
    "lca" : ['category', 'components', 'sankey'],
    "compare" : ['numbers', 'products', 'energy', 'lca', 'lca stages'],
    "map" : ['lca']
}

U_VALUE_TYPES = {
    "Foundation" :      "EB",
    "Retaining walls" : "BW",
    "External walls" :  "AW",
    "Roof" :            "FD",
    "Attic floor" :     "AD",
    "Ground floor":     "KD"
}

CONSTRUCTION_TYPE = {0:"None", 1:"Masonry", 2:"Concrete",3:"Wood"}
STANDARD = {0: "None", 1:"Standard", 2:"Advanced",3:"NZEB"}
PRODUCT_CATEGORIES = ['HO', 'KU', 'MI', 'NA', 'ME', 'OP', 'SA', 'EL', 'HV']
LANGUAGE = "EN"

# ENUMS THAT ARE USED SYSTEM WIDE
class Detail(Enum):
    """This class is an Enum for the detail of data."""
    NO_CALC =   0
    GROUPED =   1
    COUNTRY =   2
    TYPOLOGY =  3
    COMPONENT = 4
    PRODUCT =   5

class Version(Enum):
    """This class is used to store information about the currently used version of Pulse."""
    PULSE_MAIN = 1
    PULSE_EU = 2

class Impact(Enum):
    """This class is an Enum for the impact categories."""
    AE_ACIDIFICATION = 0
    GWP100 = 1
    GWP100_BIOGENIC = 2
    GWP100_FOSSIL = 3
    GWP100_LAND_USE = 4
    CTUE = 5
    ADP_FUELS = 6
    P = 7
    N = 8
    AE_EUTHROPHICATION = 9
    CTUH_CARCINOGENIC = 10
    CTUH_NON_CARCINOGENIC = 11
    U235 = 12
    LAND_USE = 13
    ADP_ELEMENTS = 14
    ODP = 15
    PARTICULATE_MATTER_FORMATION = 16
    PHOTOCHEMICAL_OXIDANT_FORMATION = 17
    WATER_USE = 18

class Renovation(Enum):
    """This class deals with different renovation types."""
    LIGHT = 0
    MEDIUM = 1
    DEEP = 2

class Use(Enum):
    """This class deals with different uses."""
    RESIDENTIAL = 0
    NON_RESIDENTIAL = 1

class ObjectType(Enum):
    """This class deals with object types."""
    PRODUCT = 0
    COMPONENT = 1
    BUILDING = 2
