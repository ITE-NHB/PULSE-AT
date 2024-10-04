# --------------------------------------------------------------------------------------------------
# buildingProductGroup.py
#
# Author: Benedict Schwark 
# Supervision: Nicolas Alaux
# Other contributors: See README.md
# License: See LICENSE.md
#
# Description: This file deals with the data type building components
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
import logging

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------
from .grouped_products import GroupedProducts
from .building_components import BuildingComponents
from ..variables import Detail


# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class BuildingProducts:
    def __init__(
        self,
        building_code,
        buildingComponents: BuildingComponents,
        allComponents: dict,
        altRequirements: dict,
        new: bool,
        detail: Detail,
    ) -> None:
        """"""
        self.code = building_code
        self.detail = detail
        self.buildingComponents = buildingComponents
        self.allComponents = allComponents
        self.altRequirements = altRequirements
        self.new = new
        if new:
            return self.newBuildingProducts()
        if not new:
            return self.oldBuildingProducts()
        raise TypeError

    def newBuildingProducts(self) -> None:
        #logging.debug("Calculating products for typology '%s'", self.code)

        if not self.detail.value:
            return None

        self.products = {}
        temp_component = ["a"] + self.altRequirements["components"]
        temp_basement = ["a"] if not self.altRequirements["basement"][0] else ["a", "b"]
        for _c_ in temp_component:
            for _b_ in temp_basement:
                self.products[f"{_c_}{_b_}"] = {}
                self.products[f"{_c_}{_b_}"]["all"] = {}
                self.products[f"{_c_}{_b_}"]["all"]["std"] = GroupedProducts(
                    f"{_c_}{_b_}-all-std", "t"
                )
                self.products[f"{_c_}{_b_}"]["all"]["replace"] = GroupedProducts(
                    f"{_c_}{_b_}-all-replace", "t"
                )

        for _c_ in temp_component:
            for key, component_ in self.buildingComponents:
                code_, comp_, area_, u_ = (
                    component_["code"],
                    component_["component"],
                    component_["area"],
                    component_["u-value"],
                )

                if not comp_:
                    continue

                if _c_ != "a" and key != "Windows":
                    comp_ = (
                        self.allComponents[f"{code_[:-1]}{_c_}"]
                        if f"{code_[:-1]}{_c_}" in self.allComponents
                        else comp_
                    )
                if _c_ != "a" and key == "Windows":
                    comp_ = (
                        self.allComponents[f"{code_[:-1]}w"]
                        if f"{code_[:-1]}w" in self.allComponents
                        else comp_
                    )

                temp_ = GroupedProducts("temp_", "t")
                replace_ = GroupedProducts("repa_", "t")
                temp_ += comp_.grouped_products * area_

                if u_ in comp_.grouped_products.additions:
                    logging.debug(
                        "Typology %s has u value %f for component %s",
                        self.code,
                        u_,
                        comp_
                    )

                temp_ += (
                    comp_.grouped_products.additions[f"U-Value: {u_}"] * area_
                    if f"U-Value: {u_}" in comp_.grouped_products.additions
                    else None
                )
                replace_ += comp_.replaceable_products * area_
                replace_ += (
                    comp_.replaceable_products.additions[f"U-Value: {u_}"] * area_
                    if f"U-Value: {u_}" in comp_.replaceable_products.additions
                    else None
                )

                self.products[f"{_c_}a"]["all"]["std"] += temp_
                self.products[f"{_c_}a"]["all"]["replace"] += replace_

                if self.altRequirements["basement"][0]:
                    if key != "Foundation" and key != "Retaining walls":
                        self.products[f"{_c_}b"]["all"]["std"] += temp_
                        self.products[f"{_c_}b"]["all"]["replace"] += replace_

                if self.detail == Detail.TYPOLOGY:
                    continue

                self.products[f"{_c_}a"][key] = {
                    "std": GroupedProducts(f"{_c_}a-{key}-std", "t"),
                    "replace": GroupedProducts(f"{_c_}a-{key}-replace", "t"),
                }
                self.products[f"{_c_}a"][key]["std"] += temp_
                self.products[f"{_c_}a"][key]["replace"] += replace_

                if self.altRequirements["basement"][0]:
                    if key != "Foundation" and key != "Retaining walls":
                        self.products[f"{_c_}b"][key] = {
                            "std": GroupedProducts(f"{_c_}b-{key}-std", "t"),
                            "replace": GroupedProducts(f"{_c_}b-{key}-replace", "t"),
                        }
                        self.products[f"{_c_}b"][key]["std"] += temp_
                        self.products[f"{_c_}b"][key]["replace"] += replace_
        return None

    def oldBuildingProducts(self) -> None:
        """This function calculates the old building products"""

        # In case the calculation should only be done for the number development the building
        # products do not get calculated.
        if not self.detail:
            return None


        self.products = {}

        # The alt components are dynamic and can be any single letter
        temp_component = ["a"] + self.altRequirements["components"]

        for renoType in ["std", "out", "light", "medium", "deep"]:
            self.products[renoType] = {}
            self.products[renoType]["all"] = {}

            # Existent buildings can only be std, so light, medium and deep only get calculated for
            # the renovation packages.
            for _c_ in (
                temp_component if renoType in ["light", "medium", "deep"] else ["a"]
            ):
                self.products[renoType]["all"][_c_] = {}
                self.products[renoType]["all"][_c_]["std"] = GroupedProducts(
                    f"{renoType}-all-{_c_}-std", "t"
                )
                self.products[renoType]["all"][_c_]["replace"] = GroupedProducts(
                    f"{renoType}-all-{_c_}-replace", "t"
                )

        for key, component_ in self.buildingComponents:
            code_, comp_, area_, u_ = (
                component_["code"],
                component_["component"],
                component_["area"],
                component_["u-value"],
            )
            if not comp_:
                continue
            temp_ = GroupedProducts("temp_", "t")
            replace_ = GroupedProducts("repa_", "t")
            temp_ += comp_.grouped_products * area_

            #if f"U-Value: {u_}" in comp_.grouped_products.additions:
            #    logging.debug("  Component '%s' has a u value demand of %f", comp_, u_)
            #else:
            #    logging.debug("  Component '%s' has no u value demand", comp_)

            temp_ += (
                comp_.grouped_products.additions[f"U-Value: {u_}"] * area_
                if f"U-Value: {u_}" in comp_.grouped_products.additions
                else None
            )
            replace_ += comp_.replaceable_products * area_
            replace_ += (
                comp_.replaceable_products.additions[f"U-Value: {u_}"] * area_
                if f"U-Value: {u_}" in comp_.replaceable_products.additions
                else None
            )

            if key not in self.products["std"]:
                self.products["std"][key] = {
                    letter: {
                        "std": GroupedProducts("Temp", "t"),
                        "replace": GroupedProducts("Temp", "t"),
                    }
                    for letter in temp_component
                }
                self.products["out"][key] = {
                    letter: {
                        "std": GroupedProducts("Temp", "t"),
                        "replace": GroupedProducts("Temp", "t"),
                    }
                    for letter in temp_component
                }

            temp_out = GroupedProducts("temp_out", "t")

            temp_out += comp_.refurbishment_products * area_

            self.products["std"]["all"]["a"]["std"] += temp_
            self.products["std"]["all"]["a"]["replace"] += replace_
            self.products["out"]["all"]["a"]["std"] += temp_out
            self.products["out"]["all"]["a"]["replace"] += temp_out

            self.products["std"][key]["a"]["std"] += temp_
            self.products["std"][key]["a"]["replace"] += replace_
            self.products["out"][key]["a"]["std"] += temp_out
            self.products["out"][key]["a"]["replace"] += temp_out

            for renoType in ["light", "medium", "deep"]:
                if self.detail == Detail.COMPONENT:
                    if key not in self.products[renoType]:
                        self.products[renoType][key] = {}

                if not component_[renoType]["code"]:
                    continue

                r_code_, r_comp_, r_u_ = (
                    component_[renoType]["code"],
                    component_[renoType]["component"],
                    component_[renoType]["u-value"],
                )
                for _c_ in temp_component:
                    r_comp__ = r_comp_
                    if _c_ != "a" and key != "Windows":

                        r_comp__ = (
                            self.allComponents[f"{r_code_[:-1]}{_c_}"]
                            if f"{r_code_[:-1]}{_c_}" in self.allComponents
                            else r_comp_
                        )
                    
                    if _c_ != "a" and key == "Windows":
                        r_comp__ = (
                            self.allComponents[f"{code_[:-1]}w"]
                            if f"{code_[:-1]}w" in self.allComponents
                            else r_comp_
                        )

                    t_temp_ = GroupedProducts("temp_", "t")
                    t_replace_ = GroupedProducts("replace_", "t")

                    t_temp_ += r_comp__.grouped_products * area_
                    t_replace_ += r_comp__.replaceable_products * area_

                    # U-Value additions are already negative, so they can be added to the temp
                    t_temp_ += (r_comp__.grouped_products.additions[f"U-Value: {r_u_}"] * area_
                        if f"U-Value: {r_u_}" in r_comp__.grouped_products.additions
                        else None
                    )


                    if key not in self.products[renoType]:
                        self.products[renoType][key] = {
                            letter: {
                                "std": GroupedProducts("Temp", "t"),
                                "replace": GroupedProducts("Temp", "t"),
                            }
                            for letter in temp_component
                        }

                    self.products[renoType]["all"][_c_]["std"] += t_temp_
                    self.products[renoType]["all"][_c_]["replace"] += t_replace_

                    if _c_ not in self.products[renoType][key]:
                        self.products[renoType][key][_c_] = {
                            "std": GroupedProducts("Temp", "t"),
                            "replace": GroupedProducts("Temp", "t"),
                        }

                    self.products[renoType][key][_c_]["std"] += t_temp_
                    self.products[renoType][key][_c_]["replace"] += t_replace_

            if self.detail == Detail.TYPOLOGY:
                continue

            if key not in self.products["std"]:
                self.products["std"][key] = {}
            if _c_ not in self.products["std"][key]:
                self.products["std"][key][_c_] = {}
            if "std" not in self.products["std"][key][_c_]:
                self.products["std"][key][_c_]["std"] = GroupedProducts(
                    f"std-{key}-{_c_}-std", "t"
                )
            if "replace" not in self.products["std"][key][_c_]:
                self.products["std"][key][_c_]["replace"] = GroupedProducts(
                    f"std-{key}-{_c_}-replace", "t"
                )

            self.products["std"][key][_c_]["std"] += temp_
            self.products["std"][key][_c_]["replace"] += replace_

        # Removing the empty GroupedProducts elements for simplicity.
        for key in self.products:
            for key_ in self.products[key]:
                for key__ in self.products[key][key_]:
                    for key___ in self.products[key][key_][key__]:
                        if self.products[key][key_][key__][key___].empty():
                            self.products[key][key_][key__][key___] = None
        return None

    def get(
        self,
        basement: bool = False,
        altComp: str = "a",
        reno: str = "std",
        replace: bool = False,
        detail: Detail = Detail.TYPOLOGY,
    ) -> GroupedProducts | dict[str, GroupedProducts]:
        """"""
        if basement:
            assert self.altRequirements["basement"][
                0
            ], f"Cannot require the basement of a building that didnt calculate it!"
        if altComp != "a":
            assert (
                altComp in self.altRequirements["components"]
            ), f"Cannot require comnponent {altComp} that is not valid!"
        assert reno in [
            "std",
            "out",
            "light",
            "medium",
            "deep",
        ], f"Cannot solve renovation requirement {reno}"

        if self.new:
            if detail == Detail.TYPOLOGY:
                return self.products[f"{altComp}{'a' if not basement else 'b'}"]["all"][
                    "std" if not replace else "replace"
                ]
            if detail == Detail.COMPONENT:
                return {
                    key: self.products[f"{altComp}{'a' if not basement else 'b'}"][key][
                        "std" if not replace else "replace"
                    ]
                    for key in self.products[f"{altComp}{'a' if not basement else 'b'}"]
                    if key != "all"
                }
            raise TypeError
        if not self.new:
            if detail == Detail.TYPOLOGY: 
                return self.products[reno]["all"][altComp][
                    "std" if not replace else "replace"
                ]
            if detail == Detail.COMPONENT:
                return {
                    key: (
                        self.products[reno][key][altComp][
                            "std" if not replace else "replace"
                        ]
                        if altComp in self.products[reno][key]
                        else 0
                    )
                    for key in self.products[reno]
                    if key != "all"
                }
            raise TypeError
        raise TypeError