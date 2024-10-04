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

from ..variables import LANGUAGE

from ..variables import percent, list_int_komma, list_float

from ..variables import Use

TYPOLOGIES = [["SFH", "TEH", "MFH", "ABL"], ["EDU", "HEA", "HOR", "OFF", "OTH", "TRA"]]
alphabet = "bcdefghijklmnop"


# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
def concentrate(l: list) -> str:
    for l_ in l:
        assert (
            l_ == l[0]
        ), f"Every instance of the list should be the same, but {l_} is not {l}"
    return l[0]


class Scenario:
    """A class for products."""

    def __init__(self, **kwargs) -> None:
        """This function initializes the product class."""
        self.name: str = kwargs.pop("Scenario")
        self.region: str = kwargs.pop("Region")
        self.years: range = kwargs.pop("Years")
        self.population: list = list_int_komma(
            kwargs["Variable"].pop("Population")["Data"]
        )
        self.floorAreaPP: list = list_float(
            kwargs["Variable"].pop("Floor area per person (NFA)")["Data"]
        )
        self.prospective: str = (
            concentrate(kwargs["Variable"].pop("Prospective scenario")["Data"])
            if "Prospective scenario" in kwargs["Variable"]
            else ""
        )
        self.recyclingRate: list | None = (
            percent(kwargs["Variable"].pop("Recycling rate"))
            if "Recycling rate" in kwargs["Variable"]
            else None
        )

        self.useOfEmpty: dict = {
            "empty dwellings": (
                percent(kwargs["Variable"].pop("Use of empty dwellings"))
                if "Use of empty dwellings" in kwargs["Variable"]
                else None
            ),
            "secondary dwellings": (
                percent(kwargs["Variable"].pop("Use of secondary dwellings"))
                if "Use of secondary dwellings" in kwargs["Variable"]
                else None
            ),
            "empty units": (
                percent(kwargs["Variable"].pop("Use of empty units"))
                if "Use of empty units" in kwargs["Variable"]
                else None
            ),
        }
        self.shareOfNew = {}
        for typology in TYPOLOGIES[Use.RESIDENTIAL.value]:
            self.shareOfNew[f"{typology}"] = (
                [percent(kwargs["Variable"].pop(f"Share of new {typology}")), {}]
                if f"Share of new {typology}" in kwargs["Variable"]
                else [None, {}]
            )
            for t in ("energy", "construction"):
                self.shareOfNew[f"{typology}"][1][t] = {}
                for i in range(1, 4):
                    if f"Share of new {typology} {t} {i}" in kwargs["Variable"]:
                        self.shareOfNew[f"{typology}"][1][t][i] = (
                            percent(
                                kwargs["Variable"].pop(
                                    f"Share of new {typology} {t} {i}"
                                )
                            )
                            if f"Share of new {typology} {t} {i}" in kwargs["Variable"]
                            else None
                        )
                    elif f"Share of new *** {t} {i}" in kwargs["Variable"]:
                        self.shareOfNew[f"{typology}"][1][t][i] = percent(
                            kwargs["Variable"][f"Share of new *** {t} {i}"]
                        )

        self.increaseNew = {}
        for typology in TYPOLOGIES[Use.NON_RESIDENTIAL.value]:
            self.increaseNew[f"{typology}"] = (
                [percent(kwargs["Variable"].pop(f"Increase in new {typology}")), {}]
                if f"Increase in new {typology}" in kwargs["Variable"]
                else [None, {}]
            )
            for t in ("energy", "construction"):
                self.increaseNew[f"{typology}"][1][t] = {}
                for i in range(1, 4):
                    if f"Share of new {typology} {t} {i}" in kwargs["Variable"]:
                        self.increaseNew[f"{typology}"][1][t][i] = (
                            percent(
                                kwargs["Variable"].pop(
                                    f"Share of new {typology} {t} {i}"
                                )
                            )
                            if f"Share of new {typology} {t} {i}" in kwargs["Variable"]
                            else None
                        )
                    elif f"Share of new *** {t} {i}" in kwargs["Variable"]:
                        self.increaseNew[f"{typology}"][1][t][i] = percent(
                            kwargs["Variable"][f"Share of new *** {t} {i}"]
                        )

        for t in ("energy", "construction"):
            for i in range(1, 4):
                if f"Share of new *** {t} {i}" in kwargs["Variable"]:
                    kwargs["Variable"].pop(f"Share of new *** {t} {i}")

        self.altComponent: dict = {
            letter: percent(kwargs["Variable"].pop(f"Share of {letter} component"))
            for letter in alphabet
            if f"Share of {letter} component" in kwargs["Variable"]
        }

        self.noBasement: list | None = (
            percent(kwargs["Variable"].pop("Share of no basement"))
            if "Share of no basement" in kwargs["Variable"]
            else None
        )
        self.refurbish: dict = {
            "light": (
                percent(kwargs["Variable"].pop("Share of refurbished buildings light"))
                if "Share of refurbished buildings light" in kwargs["Variable"]
                else None
            ),
            "medium": (
                percent(kwargs["Variable"].pop("Share of refurbished buildings medium"))
                if "Share of refurbished buildings medium" in kwargs["Variable"]
                else None
            ),
            "deep": (
                percent(kwargs["Variable"].pop("Share of refurbished buildings deep"))
                if "Share of refurbished buildings deep" in kwargs["Variable"]
                else None
            ),
        }
        self.heatingExchange: dict = {
            "exchange": (
                percent(kwargs["Variable"].pop("Heating systems exchange"))
                if "Heating systems exchange" in kwargs["Variable"]
                else None
            ),
            "lifetime": (
                [
                    int(float(t))
                    for t in kwargs["Variable"].pop("Heating systems lifetime")["Data"]
                ]
                if "Heating systems lifetime" in kwargs["Variable"]
                else None
            ),
        }
        self.increaseInNFA: dict = {
            "heated": (
                percent(kwargs["Variable"].pop("Increase in heated NFA"))
                if "Increase in heated NFA" in kwargs["Variable"]
                else None
            ),
            "cooled": (
                percent(kwargs["Variable"].pop("Increase in cooled NFA"))
                if "Increase in cooled NFA" in kwargs["Variable"]
                else None
            ),
        }
        self.shareOfSolar: dict

        assert not kwargs[
            "Variable"
        ], f"ERROR: There is at least one scenario aspect that is not able to be solved. {list(kwargs['Variable'].keys())}"

    def __repr__(self) -> str:
        """This function overwrites the repr for the Product class."""
        return f'Scenario Object "{self.name}"'

    def getAltRequirements(self, basement: list[bool], components: list) -> None:
        """This function adds additional component requirements based on scenarios to the two inputs."""
        for key in self.altComponent:
            if key not in components:
                components.append(key)
        if self.noBasement:
            basement[0] = True
        return None

    def getYear(self, year) -> dict:
        instance = year - self.years[0]
        return {
            "population": self.population[instance],
            "floorArea": self.floorAreaPP[instance],
            "refurbish": [
                self.refurbish["light"][instance] if self.refurbish["light"] else None,
                (
                    self.refurbish["medium"][instance]
                    if self.refurbish["medium"]
                    else None
                ),
                self.refurbish["deep"][instance] if self.refurbish["deep"] else None,
            ],
            "new Constr 1": {
                typology: [
                    data1[0][instance] if data1[0] else None,
                    {
                        key: {
                            key2: data3[instance] if data3 else None
                            for key2, data3 in data2.items()
                        }
                        for key, data2 in data1[1].items()
                    },
                ]
                for typology, data1 in self.shareOfNew.items()
            },
            "new Constr 2": {
                typology: [
                    data1[0][instance] if data1[0] else None,
                    {
                        key: {
                            key2: data3[instance] if data3 else None
                            for key2, data3 in data2.items()
                        }
                        for key, data2 in data1[1].items()
                    },
                ]
                for typology, data1 in self.increaseNew.items()
            },
            "use of empty": [
                (
                    self.useOfEmpty["empty dwellings"][instance]
                    if self.useOfEmpty["empty dwellings"]
                    else None
                ),
                (
                    self.useOfEmpty["secondary dwellings"][instance]
                    if self.useOfEmpty["secondary dwellings"]
                    else None
                ),
                (
                    self.useOfEmpty["empty units"][instance]
                    if self.useOfEmpty["empty units"]
                    else None
                ),
            ],
            "HSS": {
                "exchange": (
                    self.heatingExchange["exchange"][instance]
                    if self.heatingExchange["exchange"]
                    else None
                ),
                "lifetime": (
                    self.heatingExchange["lifetime"][instance]
                    if self.heatingExchange["lifetime"]
                    else None
                ),
            },
            "no basement": self.noBasement[instance] if self.noBasement else None,
            "alt comp": (
                {k: c[instance] for k, c in self.altComponent.items()}
                if self.altComponent
                else None
            ),
            "NFA": {
                "heated": (
                    self.increaseInNFA["heated"][instance]
                    if self.increaseInNFA["heated"]
                    else None
                ),
                "cooled": (
                    self.increaseInNFA["cooled"][instance]
                    if self.increaseInNFA["cooled"]
                    else None
                ),
            },
            "recycling": self.recyclingRate[instance] if self.recyclingRate else None,
        }
