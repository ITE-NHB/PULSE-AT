"""
products.py

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

from ..variables import adapt_detail, remove_empty, distribute_fully

from ..data_types import GroupedProducts
from ..variables import Detail

MULTIPLIER = 0.15

# --------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------


def calc_products(
    stock: dict,
    numbers: dict,
    products: dict,
    scenario: dict,
    year: int,
    detail: Detail,
) -> dict:
    """This function calculates the products of the building stock based on different factors."""
    temp_ = {}
    temp_["total"] = calc_products_total(
        stock, year=year, scenario=scenario, detail=detail
    )
    temp_["construction"] = calc_products_construction(
        stock, year=year, scenario=scenario, detail=detail
    )
    temp_["demolition"] = calc_products_demolition(
        stock, numbers["demolition"], detail=detail
    )
    temp_["refurbishment in"], temp_["refurbishment out"] = calc_products_refurbishment(
        stock,
        numbers["refurbishment"],
        numbers["heating system"],
        scenario=scenario,
        year=year,
        detail=detail,
    )
    temp_["replacement"] = calc_products_replacements(
        stock,
        numbers["heating system"],
        year=year,
        products=products,
        scenario=scenario,
        detail=detail,
    )
    return temp_


def calc_products_total(
    stock: dict, *, year: int, scenario: dict, detail: Detail
) -> dict:
    """This function calculates the total products in the building stock of a given year."""
    if detail.value > Detail.COMPONENT.value:
        detail = Detail.COMPONENT

    return_ = {}

    for country, countryData in stock.items():
        if country not in return_:
            return_[country] = {}
        for building in countryData.values():
            options = (
                sum(building[year].number.bare.values()),
                sum(building[year].number.light.values()),
                sum(building[year].number.medium.values()),
                sum(building[year].number.deep.values()),
            )
            building_ = building.building
            building_code = str(building_.code)

            # detail = detail.TYPOLOGY

            if detail.value < Detail.COMPONENT.value:
                print(building_.products.get())
                print(building_.products.get(reno="std"))
                print(building_.products.get(reno="out"))
                print(building_.products.get(reno="light"))
                print(building_.products.get(reno="medium"))
                print(building_.products.get(reno="deep"))
                input()

                return_[country][building_code] = GroupedProducts("temp", "t")
                return_[country][building_code] += building_.products.get()

            elif detail == Detail.COMPONENT:
                for component, grouped_products in building_.products.get(
                    detail=Detail.COMPONENT, reno="std"
                ).items():
                    if building_code not in return_[country]:
                        return_[country][building_code] = {}
                    if component not in return_[country][building_code]:
                        return_[country][building_code][component] = GroupedProducts(
                            "temp", "t"
                        )
                    return_[country][building_code][component] += (
                        grouped_products * sum(options) if grouped_products else None
                    )

                for quantities, reno in zip(options[1:], ["light", "medium", "deep"]):
                    if not quantities:
                        continue
                    if building_code not in return_[country]:
                        return_[country][building_code] = {}
                    for component, grouped_products in building_.products.get(
                        detail=Detail.COMPONENT, reno=reno
                    ).items():
                        if component not in return_[country][building_code]:
                            return_[country][building_code][component] = (
                                GroupedProducts("temp", "t")
                            )

                        return_[country][building_code][component] += (
                            grouped_products * quantities if grouped_products else None
                        )

                for component, grouped_products in building_.products.get(
                    detail=Detail.COMPONENT, reno="out"
                ).items():
                    if building_code not in return_[country]:
                        return_[country][building_code] = {}
                    if component not in return_[country][building_code]:
                        return_[country][building_code][component] = GroupedProducts(
                            "temp", "t"
                        )
                    return_[country][building_code][component] -= (
                        grouped_products * sum(options[1:])
                        if grouped_products
                        else None
                    )
                
                for hss_, amount_ in building_.hs.getHeatingsystems(
                    [sum(building.number.hs_old.values()), 0]
                )[0].items():
                    if "Heating System" not in return_[country][building_code]:
                        return_[country][building_code]["Heating System"] = (
                            GroupedProducts("temp", "t")
                        )
                    return_[country][building_code]["Heating System"] += (
                        building_.hs.currentMap[hss_].grouped_products
                        * amount_
                        * building_.floor_area["Net Heated"]
                        * (
                            1 + scenario["NFA"]["heated"]
                            if scenario["NFA"]["heated"]
                            else 1
                        )
                    )
                for hss_, amount_ in building_.hs.getHeatingsystems(
                    [0, sum(building.number.hs_new.values())]
                )[1].items():
                    if "Heating System" not in return_[country][building_code]:
                        return_[country][building_code]["Heating System"] = (
                            GroupedProducts("temp", "t")
                        )
                    return_[country][building_code]["Heating System"] += (
                        building_.hs.exchangeMap[hss_].grouped_products
                        * amount_
                        * building_.floor_area["Net Heated"]
                        * (
                            1 + scenario["NFA"]["heated"]
                            if scenario["NFA"]["heated"]
                            else 1
                        )
                    )

    # temp_ = remove_empty(adapt_detail(return_, detail))
    # assert isinstance(temp_, dict)
    return return_


def calc_products_construction(
    stock: dict, *, year: int, scenario: dict, detail: Detail
) -> dict:
    """"""
    if detail.value > Detail.COMPONENT.value:
        detail = Detail.COMPONENT

    DISTRIBUTION = productDistribution(scenario["alt comp"], scenario["no basement"])
    if detail == Detail.GROUPED:
        temp_ = GroupedProducts("Temp", "t")
    if detail.value > Detail.GROUPED.value:
        temp_ = {}

    for country, countryData in stock.items():

        if detail == Detail.COUNTRY:
            temp_[country] = GroupedProducts("Temp", "t")
        if detail.value > Detail.COUNTRY.value:
            temp_[country] = {}
        for building in countryData.values():
            building_ = building.building
            building_code = str(building_.code)
            if year not in building[year].number.total:
                continue

            if detail == Detail.TYPOLOGY:
                temp_[country][building_code] = GroupedProducts("Temp", "t")
            if detail.value > Detail.TYPOLOGY.value:
                temp_[country][building_code] = {}

            for subTypo_, amount_ in distribute_fully(
                building[year].number.total[year], DISTRIBUTION
            ).items():
                if detail == Detail.GROUPED:
                    temp_ += (
                        building_.products.get(
                            basement=subTypo_[1] == "b", altComp=subTypo_[0]
                        )
                        * amount_
                    )
                if detail == Detail.COUNTRY:
                    temp_[country] += (
                        building_.products.get(
                            basement=subTypo_[1] == "b", altComp=subTypo_[0]
                        )
                        * amount_
                    )
                if detail == Detail.TYPOLOGY:
                    temp_[country][building_code] += (
                        building_.products.get(
                            basement=subTypo_[1] == "b", altComp=subTypo_[0]
                        )
                        * amount_
                    )
                if detail == Detail.COMPONENT:
                    for component_, products_ in building_.products.get(
                        basement=subTypo_[1] == "b",
                        altComp=subTypo_[0],
                        detail=Detail.COMPONENT,
                    ).items():
                        if component_ not in temp_[country][building_code]:
                            temp_[country][building_code][component_] = GroupedProducts(
                                "temp", "t"
                            )
                        temp_[country][building_code][component_] += products_ * amount_

            for hss_, amount_ in building_.hs.getHeatingsystems(
                [building[year].number.total[year], 0]
            )[0].items():
                if detail == Detail.GROUPED:
                    temp_ += (
                        building_.hs.currentMap[hss_].grouped_products
                        * amount_
                        * building_.floor_area["Net Heated"]
                        * (
                            1 + scenario["NFA"]["heated"]
                            if scenario["NFA"]["heated"]
                            else 1
                        )
                    )
                if detail == Detail.COUNTRY:
                    temp_[country] += (
                        building_.hs.currentMap[hss_].grouped_products
                        * amount_
                        * building_.floor_area["Net Heated"]
                        * (
                            1 + scenario["NFA"]["heated"]
                            if scenario["NFA"]["heated"]
                            else 1
                        )
                    )
                if detail == Detail.TYPOLOGY:
                    temp_[country][building_code] += (
                        building_.hs.currentMap[hss_].grouped_products
                        * amount_
                        * building_.floor_area["Net Heated"]
                        * (
                            1 + scenario["NFA"]["heated"]
                            if scenario["NFA"]["heated"]
                            else 1
                        )
                    )
                if detail == Detail.COMPONENT:
                    if "Heating System" not in temp_[country][building_code]:
                        temp_[country][building_code]["Heating System"] = (
                            GroupedProducts("temp", "t")
                        )
                    temp_[country][building_code]["Heating System"] += (
                        building_.hs.currentMap[hss_].grouped_products
                        * amount_
                        * building_.floor_area["Net Heated"]
                        * (
                            1 + scenario["NFA"]["heated"]
                            if scenario["NFA"]["heated"]
                            else 1
                        )
                    )
    return remove_empty(temp_)


def calc_products_demolition(stock: dict, numbers: dict, *, detail: Detail) -> dict:
    """"""
    if detail.value > Detail.COMPONENT.value:
        detail = Detail.COMPONENT

    if detail == Detail.GROUPED:
        temp_ = GroupedProducts("Temp", "t")
    if detail.value > Detail.GROUPED.value:
        temp_ = {}

    for country, countryData in numbers.items():

        if detail == Detail.COUNTRY:
            temp_[country] = GroupedProducts("Temp", "t")
        if detail.value > Detail.COUNTRY.value:
            temp_[country] = {}

        for building_code, demoNr in countryData.items():
            building_ = stock[country][building_code].building
            if detail == Detail.TYPOLOGY:
                temp_[country][building_code] = GroupedProducts("Temp", "t")
            if detail.value > Detail.TYPOLOGY.value:
                temp_[country][building_code] = {}

            if not any(demoNr):
                continue

            if detail != Detail.COMPONENT:
                bld_temp_ = GroupedProducts("Temp", "t")
                bld_temp_ += building_.products.get() * sum(demoNr)
                if any(demoNr[1:]):
                    bld_temp_ -= building_.products.get(reno="out") * sum(demoNr[1:])
                    bld_temp_ += building_.products.get(reno="light") * demoNr[1]
                    bld_temp_ += building_.products.get(reno="medium") * demoNr[2]
                    bld_temp_ += building_.products.get(reno="deep") * demoNr[3]

            if detail == Detail.GROUPED:
                temp_ += bld_temp_
            if detail == Detail.COUNTRY:
                temp_[country] += bld_temp_
            if detail == Detail.TYPOLOGY:
                temp_[country][building_code] += bld_temp_
            if detail == Detail.COMPONENT:
                temp_out = building_.products.get(reno="out", detail=Detail.COMPONENT)
                temp_light = building_.products.get(
                    reno="light", detail=Detail.COMPONENT
                )
                temp_medium = building_.products.get(
                    reno="medium", detail=Detail.COMPONENT
                )
                temp_deep = building_.products.get(reno="deep", detail=Detail.COMPONENT)
                for comp, products in building_.products.get(
                    detail=Detail.COMPONENT
                ).items():
                    assert isinstance(temp_, dict)
                    temp_[country][building_code][comp] = GroupedProducts("Temp", "t")
                    temp_[country][building_code][comp] += (products * sum(demoNr)) if products else None
                    temp_[country][building_code][comp] += (
                        temp_out[comp] * sum(demoNr[1:])
                        if comp in temp_out and temp_out[comp]
                        else None

                    )
                    temp_[country][building_code][comp] += (
                        temp_light[comp] * demoNr[1]
                        if comp in temp_light and temp_light[comp]
                        else None
                    )
                    temp_[country][building_code][comp] += (
                        temp_medium[comp] * demoNr[2]
                        if comp in temp_medium and temp_medium[comp]
                        else None
                    )
                    temp_[country][building_code][comp] += (
                        temp_deep[comp] * demoNr[3]
                        if comp in temp_deep and temp_deep[comp]
                        else None
                    )

    return remove_empty(temp_)


def calc_products_replacements(
    stock: dict, hss: dict, *, year: int, products: dict, scenario: dict, detail: Detail
) -> dict:
    """"""
    if detail.value > Detail.COMPONENT.value:
        detail = Detail.COMPONENT

    if detail == Detail.GROUPED:
        temp_ = GroupedProducts("Temp", "t")
    if detail.value > Detail.GROUPED.value:
        temp_ = {}

    for country, countryData in stock.items():
        if detail == Detail.COUNTRY:
            temp_[country] = GroupedProducts("Temp", "t")
        if detail.value > Detail.COUNTRY.value:
            temp_[country] = {}
        for (code_, building), hss_info in zip(
            countryData.items(), hss[country].values()
        ):
            building_ = building.building
            hss_ = hss[country][code_] if code_ in hss[country] else None
            if detail == Detail.TYPOLOGY:
                temp_[country][code_] = GroupedProducts("Temp", "t")
            if detail.value > Detail.TYPOLOGY.value:
                temp_[country][code_] = {}

            if detail != Detail.COMPONENT:
                replaceable = building_.products.get(replace=True).dictify()

                for year_, amount_ in building.number.total.items():
                    age_ = year - int(year_)
                    for product, p_amount_ in replaceable.items():
                        if not age_:
                            continue
                        if not products[product].serviceLife:
                            continue
                        if age_ % products[product].serviceLife:
                            continue
                        if detail == Detail.GROUPED:
                            temp_ += (product, amount_ * p_amount_ * MULTIPLIER)
                        if detail == Detail.COUNTRY:
                            temp_[country] += (
                                product,
                                amount_ * p_amount_ * MULTIPLIER,
                            )
                        if detail == Detail.TYPOLOGY:
                            temp_[country][code_] += (
                                product,
                                amount_ * p_amount_ * MULTIPLIER,
                            )

            if detail == Detail.COMPONENT:
                replaceable = {
                    comp: compData.dictify() if compData else None
                    for comp, compData in building_.products.get(
                        replace=True, detail=Detail.COMPONENT
                    ).items()
                }
                for year_, amount_ in building.number.total.items():
                    age_ = year - int(year_)
                    for comp, compReplace in replaceable.items():
                        if not compReplace: continue
                        for product, p_amount_ in compReplace.items():
                            if not age_:
                                continue
                            if not products[product].serviceLife:
                                continue
                            if age_ % products[product].serviceLife:
                                continue
                            if comp not in temp_[country][code_]:
                                temp_[country][code_][comp] = GroupedProducts(
                                    "Temp", "t"
                                )
                            temp_[country][code_][comp] += (
                                product,
                                amount_ * p_amount_ * MULTIPLIER,
                            )
            #continue
            for hss_, amount_ in building_.hs.getHeatingsystems([hss_info[0], 0])[
                0
            ].items():
                if not hss_:
                    continue
                temp__ = (
                    building_.hs.currentMap[hss_].grouped_products
                    * amount_
                    * building_.floor_area["Net Heated"]
                    * (
                        1 + scenario["NFA"]["heated"]
                        if scenario["NFA"]["heated"]
                        else 1
                    )
                )
                if detail == Detail.GROUPED:
                    temp_ += temp__
                if detail == Detail.COUNTRY:
                    temp_[country] += temp__
                if detail == Detail.TYPOLOGY:
                    temp_[country][code_] += temp_

                if detail == Detail.COMPONENT:
                    if "Heating System" not in temp_[country][code_]:
                        temp_[country][code_]["Heating System"] = GroupedProducts(
                            "Temp", "t"
                        )
                    temp_[country][code_]["Heating System"] += temp__

            for hss_, amount_ in building_.hs.getHeatingsystems([0, hss_info[2]])[
                1
            ].items():
                if not hss_ or not amount_:
                    continue
                temp__ = (
                    building_.hs.exchangeMap[hss_].grouped_products
                    * amount_
                    * building_.floor_area["Net Heated"]
                    * (
                        1 + scenario["NFA"]["heated"]
                        if scenario["NFA"]["heated"]
                        else 1
                    )
                )
                if detail == Detail.GROUPED:
                    temp_ += temp__
                if detail == Detail.COUNTRY:
                    temp_[country] += temp__
                if detail == Detail.TYPOLOGY:
                    temp_[country][code_] += temp__
                if detail == Detail.COMPONENT:
                    if "Heating System" not in temp_[country][code_]:
                        temp_[country][code_]["Heating System"] = GroupedProducts(
                            "Temp", "t"
                        )
                    temp_[country][code_]["Heating System"] += temp__

    return remove_empty(temp_)


def calc_products_refurbishment(
    stock: dict, numbers: dict, hss: dict, *, year: int, scenario: dict, detail: Detail
) -> dict:
    """"""
    if detail.value > Detail.COMPONENT.value:
        detail = Detail.COMPONENT

    if detail == Detail.GROUPED:
        temp_in, temp_out = GroupedProducts("Temp", "t"), GroupedProducts("Temp", "t")
    if detail.value > Detail.GROUPED.value:
        temp_in, temp_out = {}, {}

    for country, countryData in stock.items():
        if detail == Detail.COUNTRY:
            temp_in[country], temp_out[country] = GroupedProducts(
                "Temp", "t"
            ), GroupedProducts("Temp", "t")
        if detail.value > Detail.COUNTRY.value:
            temp_in[country], temp_out[country] = {}, {}

        for code_, building in countryData.items():
            if code_ not in numbers[country]:
                continue
            number = numbers[country][code_]
            if not any(number):
                continue
            if detail == Detail.TYPOLOGY:
                temp_in[country][code_], temp_out[country][code_] = GroupedProducts(
                    "Temp", "t"
                ), GroupedProducts("Temp", "t")
            if detail.value > Detail.TYPOLOGY.value:
                temp_in[country][code_], temp_out[country][code_] = {}, {}

            building_ = building.building
            if detail != Detail.COMPONENT:
                temp_1_ = GroupedProducts("Temp", "t")
                temp_2_ = GroupedProducts("Temp", "t")
                temp_1_ -= building_.products.get(reno="out") * number[0]
                temp_2_ += building_.products.get(reno="light") * number[1]
                temp_2_ += building_.products.get(reno="medium") * number[2]
                temp_2_ += building_.products.get(reno="deep") * number[3]

            if detail == Detail.GROUPED:
                assert isinstance(temp_in, GroupedProducts)
                assert isinstance(temp_out, GroupedProducts)
                temp_in += temp_2_
                temp_out += temp_1_
            if detail == Detail.COUNTRY:
                assert isinstance(temp_in, dict)
                assert isinstance(temp_out, dict)
                temp_in[country] += temp_2_
                temp_out[country] += temp_1_
            if detail == Detail.TYPOLOGY:
                assert isinstance(temp_in, dict)
                assert isinstance(temp_out, dict)
                temp_in[country][code_] += temp_2_
                temp_out[country][code_] += temp_1_
            if detail == Detail.COMPONENT:

                for letter, multiplier in zip(
                    ["a"] + (list(scenario["alt comp"].keys()) if scenario["alt comp"] else []),
                    [
                        1- (
                            sum(scenario["alt comp"].values())
                            if scenario["alt comp"] else 0
                        )
                    ] + (list(scenario["alt comp"].values()) if scenario["alt comp"] else [])
                ):
                    if not multiplier:
                        continue

                    temp_light = building_.products.get(
                        altComp=letter,
                        reno="light",
                        detail=Detail.COMPONENT
                    )
                    temp_medium = building_.products.get(
                        altComp=letter,
                        reno="medium", detail=Detail.COMPONENT
                    )
                    temp_deep = building_.products.get(
                        altComp=letter,
                        reno="deep",
                        detail=Detail.COMPONENT
                    )
                    for comp, products in building_.products.get(
                        altComp=letter,
                        reno="out",
                        detail=Detail.COMPONENT
                    ).items():
                        assert isinstance(temp_in, dict)
                        assert isinstance(temp_out, dict)


                        temp_in[country][code_][comp] = GroupedProducts("Temp", "t")
                        temp_out[country][code_][comp] = GroupedProducts("Temp", "t")
                        temp_out[country][code_][comp] += products * (number[0] * -1) * multiplier if products else None
                        temp_in[country][code_][comp] += (
                            temp_light[comp] * number[1] * multiplier if comp in temp_light and temp_light[comp] else None
                        )
                        temp_in[country][code_][comp] += (
                            temp_medium[comp] * number[2] * multiplier if comp in temp_medium and temp_medium[comp] else None
                        )
                        temp_in[country][code_][comp] += (
                            temp_deep[comp] * number[3] * multiplier if comp in temp_deep and temp_deep[comp] else None
                        )
            if "Heating System" not in temp_out[country][code_]:
                temp_out[country][code_]["Heating System"] = GroupedProducts(
                    "Temp", "t"
                )

            if "Heating System" not in temp_in[country][code_]:
                temp_in[country][code_]["Heating System"] = GroupedProducts(
                    "Temp", "t"
                )
            
            if str(building_.code) not in hss['AT']: continue
            for hss_, amount_ in building_.hs.getHeatingsystems([hss['AT'][str(building_.code)][1],0])[0].items():
                if not amount_: continue
                temp_out[country][code_]["Heating System"] += building_.hs.currentMap[hss_].grouped_products * amount_ * building_.floor_area['Net Heated'] * (1 + scenario["NFA"]['heated'] if scenario["NFA"]['heated'] else 1)
        
            for hss_, amount_ in building_.hs.getHeatingsystems([0,hss['AT'][str(building_.code)][1]])[1].items():
                if not amount_: continue
                temp_in[country][code_]["Heating System"] += (
                    building_.hs.exchangeMap[hss_].grouped_products * 
                    (amount_ * 
                    building_.floor_area['Net Heated'] * 
                    (1 + scenario["NFA"]['heated'] if scenario["NFA"]['heated'] else 1))
                )

    return remove_empty(temp_in), remove_empty(temp_out)


def productDistribution(altComp: dict, basement: float) -> dict:
    """"""
    distribution = {"aa": 1}
    if altComp:
        for comp, share in altComp.items():
            distribution["aa"] -= share
            distribution[f"{comp}a"] = share
    if basement:
        distribution_ = {}
        for comp, share in distribution.items():
            distribution_[f"{comp}"] = share * (1 - basement)
            distribution_[f"{comp[0]}b"] = share * basement
        return distribution_
    return distribution
