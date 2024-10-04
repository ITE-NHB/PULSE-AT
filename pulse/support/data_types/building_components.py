"""
buildingComponents.py

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the data type building components
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# FUNCTIONS
from ..variables import float_empty, list_strip

# CLASSES
from ..variables import Renovation

# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class BuildingComponents:
    """A class for the components of a building."""

    def __init__(self, **kwargs):
        """This function..."""
        self.code = kwargs["code"]
        self.kind: list = list_strip(kwargs["kind"])
        self.codes: list = list_strip(kwargs["idBuilt"])
        self.components: list | None = None
        self.area: list = [
            (float_empty(a)
            if '-' not in a
            else [float_empty(a_) for a_ in a.split('-')])
            if a.strip() != "-"
            else 0 
            for a in kwargs["area"]
        ]
        self.u: list = (
            # TODO: FIX
            ([float_empty(a) for a in kwargs["uDefault"]]
            if isinstance(kwargs["uDefault"], list)
            else [float_empty(kwargs["uDefault"])] + ["" for _ in self.kind][1:]
            )
            if kwargs["uDefault"] 
            else ["" for _ in self.kind]
        )
        self.light_codes: list = (
            list_strip(kwargs["idLight"])
            if kwargs["idLight"]
            else ["" for _ in self.kind]
        )
        self.light_comps: list | None  = None
        self.light_u: list = (
            [float_empty(a) for a in kwargs["uLight"]]
            if kwargs["idLight"]
            else ["" for _ in self.kind]
        )
        self.medium_codes: list = (
            list_strip(kwargs["idMedium"])
            if kwargs["idMedium"]
            else ["" for _ in self.kind]
        )
        self.medium_comps: list | None  = None
        self.medium_u: list = (
            [float_empty(a) for a in kwargs["uMedium"]]
            if kwargs["uMedium"]
            else ["" for _ in self.kind]
        )
        self.deep_codes: list = (
            list_strip(kwargs["idDeep"])
            if kwargs["idDeep"]
            else ["" for _ in self.kind]
        )
        self.deep_comps: list | None  = None
        self.deep_u: list = (
            [float_empty(a) for a in kwargs["uDeep"]]
            if kwargs["uDeep"]
            else ["" for _ in self.kind]
        )

    def __repr__(self):
        """This function..."""
        output = f"+{'-'*64}+{'-'*18}+{'-'*18}+{'-'*18}+\n"
        output = (
            f"{output}|{'Standard':^64}|{'Light':^18}|{'Medium':^18}|{'Deep':^18}|\n"
        )
        output = f"{output}+{'-'*64}+{'-'*18}+{'-'*18}+{'-'*18}+\n"
        output = f"{output}| {'Component':^33} - {'Codes':^8} - {'Area':^7} - {'U':^5} | {'Codes':^8} - {'U':^5} | {'Codes':^8} - {'U':^5} | {'Codes':^8} - {'U':^5} |\n"
        for pos, kind in enumerate(self.kind):
            area = f"{self.area[pos]:7.2f}" if isinstance(self.area[pos], float) else "N/A"
            output = (
                f"{output}| {kind:>33} - {self.codes[pos]:>8} - {area:>7} - {self.u[pos]:>5.3f} |"
                if self.u[pos]
                else f"{output}| {kind:>33} - {self.codes[pos]:>8} - {area:>7} - {'N/A':>5} |"
            )
            output = (
                f"{output} {self.light_codes[pos]} - {self.light_u[pos]:>5.3f} |"
                if self.light_codes[pos]
                else (
                    f"{output} {' '*17}|"
                    if not isinstance(self.light_u[pos], list)
                    else f"{output} {'?'*17}|"
                )
            )
            output = (
                f"{output} {self.medium_codes[pos]} - {self.medium_u[pos]:>5.3f} |"
                if not isinstance(self.medium_u[pos], list) and self.medium_codes[pos]
                else (
                    f"{output} {self.medium_codes[pos]} - {'N/A':>5} |"
                    if self.medium_codes[pos]
                    else f"{output} {' '*17}|"
                )
            )
            output = (
                f"{output} {self.deep_codes[pos]} - {self.deep_u[pos]:>5.3f} |"
                if not isinstance(self.deep_u[pos], list) and self.deep_codes[pos]
                else (
                    f"{output} {self.deep_codes[pos]} - {'N/A':>5} |"
                    if self.deep_codes[pos]
                    else f"{output} {' '*17}|"
                )
            )
            output = f"{output}\n"
        output = f"{output}+{'-'*64}+{'-'*18}+{'-'*18}+{'-'*18}+\n"
        return output

    def __iter__(self) -> iter:
        """This function overwrites the iter."""
        for i, code in enumerate(self.codes):
            yield self.kind[i], {
                "code": code,
                "component": (
                    self.components[i]
                    if self.components and len(self.components) == len(self.codes)
                    else None
                ),
                "u-value": self.u[i],
                "area": self.area[i],
                "light": {
                    "code": self.light_codes[i],
                    "component": (
                        self.light_comps[i]
                        if self.light_comps and len(self.light_comps) == len(self.codes)
                        else None
                    ),
                    "u-value": self.light_u[i],
                },
                "medium": {
                    "code": self.medium_codes[i],
                    "component": (
                        self.medium_comps[i]
                        if self.medium_comps and len(self.medium_comps) == len(self.codes)
                        else None
                    ),
                    "u-value": self.medium_u[i],
                },
                "deep": {
                    "code": self.deep_codes[i],
                    "component": (
                        self.deep_comps[i]
                        if self.deep_comps and len(self.deep_comps) == len(self.codes)
                        else None
                    ),
                    "u-value": self.deep_u[i],
                },
            }

    def __getitem__(self, pos: int) -> list:
        """This function overwrites the getter for the BuildingComponents class."""
        assert 0 <= pos <= len(self.codes), f"{pos}"
        if self.components:
            return [
                self.kind[pos],
                self.codes[pos],
                self.components[pos],
                self.u[pos],
                self.area[pos],
            ]
        return [self.kind[pos], self.codes[pos], self.u[pos], self.area[pos]]

    def renoList(self, kind: Renovation) -> list:
        """This function returns the light, medium or deep components of the component list."""
        if kind == Renovation.LIGHT:
            return (
                [
                    [k, c, lc, u, lu, a]
                    for k, c, u, lc, lu, a in zip(
                        self.kind,
                        self.codes,
                        self.u,
                        self.light_comps,
                        self.light_u,
                        self.area,
                    )
                    if lc
                ]
                if self.light_comps
                else [
                    [k, c, lc, u, lu, a]
                    for k, c, u, lc, lu, a in zip(
                        self.kind,
                        self.codes,
                        self.u,
                        self.light_codes,
                        self.light_u,
                        self.area,
                    )
                ]
            )  # if lc]
        if kind == Renovation.MEDIUM:
            return (
                [
                    [k, c, mc, u, mu, a]
                    for k, c, u, mc, mu, a in zip(
                        self.kind,
                        self.codes,
                        self.u,
                        self.medium_comps,
                        self.medium_u,
                        self.area,
                    )
                    if mc
                ]
                if self.medium_comps
                else [
                    [k, c, mc, u, mu, a]
                    for k, c, u, mc, mu, a in zip(
                        self.kind,
                        self.codes,
                        self.u,
                        self.medium_codes,
                        self.medium_u,
                        self.area,
                    )
                ]
            )  #  if mc]
        if kind == Renovation.DEEP:
            return (
                [
                    [k, c, dc, u, du, a]
                    for k, c, u, dc, du, a in zip(
                        self.kind,
                        self.codes,
                        self.u,
                        self.deep_comps,
                        self.deep_u,
                        self.area,
                    )
                    if dc
                ]
                if self.deep_comps
                else [
                    [k, c, dc, u, du, a]
                    for k, c, u, dc, du, a in zip(
                        self.kind,
                        self.codes,
                        self.u,
                        self.deep_codes,
                        self.deep_u,
                        self.area,
                    )
                ]
            )  #  if dc]
        raise KeyError

    def link_component(self, component: object) -> None:
        """This function links a new components."""
        if not self.components:
            self.components = []
        self.components.append(component)
        assert (
            self.components[-1] is None
            or self.components[-1].code == self.codes[len(self.components) - 1]
        ), f"The specified component is not compatible with its code: {self.components[-1].code}, {self.codes[len(self.components)-1]}"

    def link_reno_components(self, component, t) -> None:
        if not self.light_comps:
            self.light_comps = []
        if not self.medium_comps:
            self.medium_comps = []
        if not self.deep_comps:
            self.deep_comps = []
        if t == 0:
            self.light_comps.append(component)
        if t == 1:
            self.medium_comps.append(component)
        if t == 1:
            self.deep_comps.append(component)
