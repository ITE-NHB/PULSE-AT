"""
buildings.py

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the data type building
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# VARIABLES
from ..variables import U_VALUE_TYPES

# FUNCTIONS
from ..variables import int_komma, float_komma

# CLASSES
from .building_components import BuildingComponents
from .building_products import BuildingProducts
from .code import Code
from .energy_carriers import EnergyCarriers
from ..variables import ObjectType, Renovation

# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------


class Building:
    """A class for Buildings for the detailed pulse calculation."""

    def __init__(self, **kwargs) -> None:
        """This function initializes the Buildings class."""
        kwargs = {key.strip(): data for key, data in kwargs.items()}
        self.code: Code = Code(kwargs.pop(next(iter(kwargs))), ObjectType.BUILDING)
        self.version: str = "A"

        self.country: str = str(kwargs["Country"])
        self.use: str = kwargs["Use"]
        self.typology: str = kwargs["Typology"]
        self.years: tuple[int, int] = (
            int(kwargs["From (year)"]),
            int(kwargs["To (year)"]),
        )
        self.year_range: range = range(self.years[0], self.years[1] + 1)
        self.energy_class: str = kwargs["Energy class"]
        self.construction_type: str = kwargs["Construction type"]
        self.floor_area: dict = {
            "Gross": float_komma(kwargs["Gross floor area (m2)"].replace(",", "")),
            "Net Heated": float_komma(kwargs["Net floor (heated) area (m2)"]),
            "Net Cooled": float_komma(kwargs["Net cooled area (m2)"]),
        }
        self.volume: float = float_komma(kwargs["Volume (m3)"].replace(",", ""))
        self.storeys: int = int(kwargs["Number of storeys"])
        self.dwellings: int = int(kwargs["Number of dwellings or units"])
        self.resident_per_dwelling: int | None = (
            int(kwargs["Average number of habitants (per dwelling)"])
            if kwargs["Average number of habitants (per dwelling)"].strip() != "-"
            else None
        )
        self.residents: int | None = (
            self.dwellings * self.resident_per_dwelling if self.resident_per_dwelling else None
        )
        self.products = None
        self.shared_of_used: list = [
            float(kwargs["Share of occupied dwellings or units"]),
            float(kwargs["Share of vacant dwellings or units"]),
            (
                float(kwargs["Share of secondary dwellings or units"])
                if kwargs["Share of secondary dwellings or units"].strip() != "-"
                else 0
            ),
        ]

        self.carriers: dict = {
            "Current": {
                carrier: {"component": comp, "share": share}
                for carrier, comp, share in zip(
                    kwargs["Energy carriers (current)"],
                    kwargs["ID component (current)"],
                    kwargs["Share (current)"],
                )
                if carrier != ""
            },
            "Exchange": {
                carrier: {"component": comp, "share": share}
                for carrier, comp, share in zip(
                    kwargs["Energy carriers (exchange)"],
                    kwargs["ID component (exchange)"],
                    kwargs["Share (exchange)"],
                )
                if carrier != ""
            },
        }

        self.components: BuildingComponents = BuildingComponents(
            code=self.code,
            kind=kwargs["Element type"],
            idBuilt=kwargs["ID component (as-built)"],
            area=kwargs["Area (m2)"],
            uDefault=kwargs["U-value default (W/m2K)"],
            idLight=kwargs["ID component (light refurbishment)"],
            uLight=kwargs["U-value light (W/m2K)"],
            idMedium=kwargs["ID component (medium refurbishment)"],
            uMedium=kwargs["U-value medium (W/m2K)"],
            idDeep=kwargs["ID component (deep refurbishment)"],
            uDeep=kwargs["U-value deep (W/m2K)"],
        )

        self.number: dict = {
            "total": int_komma(kwargs["Number of buildings in stock (31.12.2022)"]),
            "light": int_komma(kwargs["Number of refurbished buildings (light)"]),
            "medium": int_komma(kwargs["Number of refurbished buildings (medium)"]),
            "deep": int_komma(kwargs["Number of refurbished buildings (deep)"]),
            "protected": int_komma(
                kwargs['Number of protected buildings ("Denkmalschutz")']
            ),
        }

        self.heating_demand: list = [
            float_komma(kwargs["Space heating demand Existing state (kWh/m2a)"]),
            float_komma(kwargs["Space heating demand Light refurbishment (kWh/m2a)"]),
            float_komma(kwargs["Space heating demand Medium refurbishment (kWh/m2a)"]),
            float_komma(kwargs["Space heating demand Deep refurbishment (kWh/m2a)"]),
            float_komma(kwargs["Energy demand for domestic hot water (kWh/m2GFAa)"]),
        ]

        self.cooling_consumption = float(
            kwargs["Final energy consumption space cooling (kWh/m2Aa)"]
        )

        self.electric_consumption = {
            "B6.1": float(
                kwargs["Electricity demand  (excl. heating) - B6.1 (kWh/m2NFAa)"]
            ),
            "B6.2": float_komma(
                kwargs["Electricity demand - B6.2 & B6.3 (kWh/m2NFAa)"]
            ),
            "B8": float_komma(kwargs["Energy demand - B8 (kWh/building)"]),
        }
        self.water_use = float_komma(kwargs["Water use per building per year (m3)"])

        self.hs: EnergyCarriers = EnergyCarriers(
            kwargs["Energy carriers (current)"],
            kwargs["ID component (current)"],
            kwargs["Share (current)"],
            kwargs["Energy carriers (exchange)"],
            kwargs["ID component (exchange)"],
            kwargs["Share (exchange)"],
        )

    def __repr__(self) -> str:
        """This function overwrites the repr for the Buildings class."""
        return f'Building Object "{self.code}"'

    def get_used_components(self, used_component: list) -> None:
        """This function collects all components that are being used by the building"""
        for _, component in self.components:
            if component["code"] not in used_component:
                used_component.append(component["code"])
            for t in ["light", "medium", "deep"]:
                if component[t]["code"] not in used_component:
                    used_component.append(component[t]["code"])

        for heating_systems in self.carriers.values():
            for system in heating_systems.values():
                if system["component"] not in used_component:
                    used_component.append(system["component"])

    def get_u_requirements(self, requirements: dict) -> None:
        """This function adds the u-value requirements of the given building to the requirements dictionary."""
        for key, component in self.components:
            if key not in U_VALUE_TYPES or not component["u-value"]:
                continue
            if component["code"] not in requirements:
                requirements[component["code"]] = [[], []]
            if U_VALUE_TYPES[key] not in requirements[component["code"]][0]:
                requirements[component["code"]][0].append(U_VALUE_TYPES[key])
            if (component["u-value"]) not in requirements[component["code"]][1]:
                requirements[component["code"]][1].append((component["u-value"]))
            for kind in ["light", "medium", "deep"]:
                if (
                    key not in U_VALUE_TYPES
                    or not component[kind]["code"]
                    or not component[kind]["u-value"]
                ):
                    continue
                if component[kind]["code"] not in requirements:
                    # requirements[component[kind]['code']] = [U_VALUE_TYPES[key],[]]
                    requirements[component[kind]["code"]] = [[], []]
                if U_VALUE_TYPES[key] not in requirements[component[kind]["code"]][0]:
                    requirements[component[kind]["code"]][0].append(U_VALUE_TYPES[key])
                if (
                    component["u-value"],
                    component[kind]["u-value"],
                ) not in requirements[component[kind]["code"]][1]:
                    requirements[component[kind]["code"]][1].append(
                        (component["u-value"], component[kind]["u-value"])
                    )

    def link_components(self, components: dict) -> None:
        """This functiom links the provided components to the building class."""
        for _, component in self.components:
            if component["code"] == '0':
                continue
            _ = (
                self.components.link_component(components[component["code"]])
                if component["code"] != "N/A"
                else self.components.link_component(None)
            )

        for i, t in enumerate((Renovation.LIGHT, Renovation.MEDIUM, Renovation.DEEP)):
            for component in self.components.renoList(t):
                if not isinstance(component[2], str):
                    continue
                if component[2] != "":
                    self.components.link_reno_components(components[component[2]], i)
                else:
                    self.components.link_reno_components(0, i)
        self.hs.linkComponents(components)

    def calc_products(self, alt, components, detail) -> None:
        """This function calculates the products for a building."""
        self.products = BuildingProducts(
            str(self.code),
            self.components,
            components,
            alt,
            new=self.code.years[0] >= 2010,
            detail=detail,
        )
