"""
variables

---------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------------------
# Variables
# --------------------------------------------------------------------------------------------------
from .characters import M2, M3, KM2, B0, B1, EMISSION_INFO, YEARS, KWH, NR, T
from .globals import (
    CONSTRUCTION_TYPE,
    STANDARD,
    INDICATOR,
    INDICATOR_NAMES,
    PROGRESS_BAR,
    TYPOLOGIES,
    CURRENT_PROSPECTIVE,
    GRAPH_OPTIONS,
    VERSION,
    NO_B8,
    LANGUAGE,
    U_VALUE_TYPES,
    PRODUCT_IDs,
)

# --------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------
from .colors import combine_colors, color_range, color_rand, hex_to_rgba
from .format import (
    int_komma,
    float_komma,
    float_empty,
    float_dash,
    list_strip,
    distribute_fully,
    percent,
    list_int_komma,
    list_float,
    distribute_in_relation,
    remove_available,
    add_available,
    get_share_of_used,
    prime,
)
from .reducers import reduce_detail, find_detail, adapt_detail, remove_empty

# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
from .ascii import Loading, Logo
from .globals import ObjectType, Detail, Version, Impact, Use, Renovation
