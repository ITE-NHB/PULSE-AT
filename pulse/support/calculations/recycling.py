"""
recycling.py
----------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

from ..data_types import GroupedProducts
from ..variables import adapt_detail, Detail

import copy

RECYCLING_FACTORS = {
    'HO' : {
        'HO_201': ('HO_216', 0),
        'HO_204': ('HO_216', 0),
        'HO_209': ('HO_217', 0),
        'HO_210': ('HO_217', 0),
        'HO_211': ('HO_217', 0),
        'HO_212': ('HO_218', 0),
        'HO_208': ('HO_219', 0)
    },
    'KU_2' : {
        'KU_201': ('KU_218', 0),
        'KU_202': ('KU_218', 0),
        'KU_203': ('KU_218', 0),
        'KU_204': ('KU_218', 0),
        'KU_205': ('KU_218', 0),
        'KU_206': ('KU_218', 0),
        'KU_207': ('KU_218', 0)
    },
    'MI_3' : {
        'MI_101': ('MI_131', 0)
    },
    'MI_2' : {
        'MI_202': ('MI_218', 0),
        'MI_205': ('MI_219', 0),
        'MI_206': ('MI_220', 0)
    },
    'MI_501' : {
        'MI_501': (None, 0)
    },
    'MI_502' : {
        'MI_502': (None, 0)
    },
    'MI_503' : {
        'MI_503': (None, 0)
    }
}

def calcDemoRecycling(products: dict, scenario: dict, detail: Detail) -> dict:
    """This function calculates the recycling."""

    return_rec = {}
    return_out = {}

    for country, countryData in products.items():
        return_out[country], return_rec[country] = {}, {}
        for typology, typoData in countryData.items():
            if not typoData: continue
            return_out[country][typology], return_rec[country][typology] = {}, {}
            for component, compData in typoData.items():
                if compData.empty(): continue
                if not compData: continue
                return_out[country][typology][component], return_rec[country][typology][component] = GroupedProducts("Temp", "t"), GroupedProducts("Temp", "t")
                for product, quantity in compData.dictify().items():
                    
                    if product[:2] in RECYCLING_FACTORS or product[:4] in RECYCLING_FACTORS or product in RECYCLING_FACTORS:
                        return_rec[country][typology][component] += (product, quantity * scenario['recycling'])
                        return_out[country][typology][component] += (product, quantity * (1-scenario['recycling']))
                    else:
                        return_out[country][typology][component] += (product, quantity)

    return return_rec, return_out

def calcConstructionRecycling(construction, demolition, detail) -> dict:
    """"""
    return_con = {}

    con_prods = adapt_detail(copy.deepcopy(construction), Detail.GROUPED)
    decon_prods = adapt_detail(copy.deepcopy(demolition), Detail.GROUPED)

    reducers = {}
    for recycledProd, goalProd in RECYCLING_FACTORS.items():
        currentConValue = 0


        for prod in goalProd:
            currentConValue += sum(con_prods.getProducts(prod).values())

        currentDecon = decon_prods.getProducts(recycledProd)
        currentDeconValue = sum(currentDecon.values())

        if currentConValue == 0:
            reducers[recycledProd] = 0
        else:
            reducers[recycledProd] = (currentDeconValue/currentConValue if currentDeconValue/currentConValue < 1 else 1)


    for country, countryData in construction.items():
        return_con[country] = {}
        for typology, typoData in countryData.items():
            if not typoData: continue
            return_con[country][typology] = {}
            for component, compData in typoData.items():
                return_con[country][typology][component] = GroupedProducts("Temp", "t")
                for product, quantity in compData.dictify().items():
                    found = False  
                    for recycledProd, goalProd in RECYCLING_FACTORS.items():
                        if found: break
                        if product in goalProd:
                            found = True
                            return_con[country][typology][component] += (product, quantity * (1 - reducers[recycledProd]))
                            return_con[country][typology][component] += (goalProd[product][0], quantity * reducers[recycledProd]) if goalProd[product][0] else (product, quantity * reducers[recycledProd])
                            break
                    if not found:   return_con[country][typology][component] += (product, quantity)


    return return_con