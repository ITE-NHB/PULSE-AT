# ----------------------------------------------------------------------------------------------------------------
# stockItem.py=
# 
# Author: Benedict Schwark 
# Supervision: Nicolas Alaux
# Other contributors: See README.md
# License: See LICENSE.md
#
# Description: This file deals with the data type code
# ----------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------
# Imports Global Libraries
# ----------------------------------------------------------------------------------------------------------------
import copy
import math
from typing import Any

# ----------------------------------------------------------------------------------------------------------------
# Imports Local Libraries
# ----------------------------------------------------------------------------------------------------------------

# FUNCTIONS
from ..file_handling.importer import import_json
from ..variables import (
    distribute_in_relation,
    remove_available,
    add_available,
    get_share_of_used,
)

# CLASSES
from .building_number import BuildingNumber

# ----------------------------------------------------------------------------------------------------------------
# Global Variables
# ----------------------------------------------------------------------------------------------------------------
DECONSTRUCTION_STATISTIC = {}  # it is up to date.
REPLACEMENT_STATISTIC = {}

INCREMENT = 1
LIGHT_RENO = True  # Allows the light buildings to be upgraded to medium or deep
OVERHANG = 0
CHANGE_HSS = 0.5  # Default Exchanging rate for heating systems
LIFETIME_HSS = 20  # Default Lifetime for heating systems

HED = f"╠{'═'*6}╤{'═'*9}╤{'═'*9}╤{'═'*9}╤{'═'*9}╤{'═'*9}╤{'═'*6}╣"
HOR = f"╟{'─'*6}┼{'─'*9}┼{'─'*9}┼{'─'*9}┼{'─'*9}┼{'─'*9}┼{'─'*6}╢"
END = f"╚{'═'*6}╧{'═'*9}╧{'═'*9}╧{'═'*9}╧{'═'*9}╧{'═'*9}╧{'═'*6}╝"

# ----------------------------------------------------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------------------------------------------------
intN = lambda x: int(x) if "-" not in x else int(x[x.find("-") + 1 :])


class StockItem:
    """This is a class to deal with layered elements"""

    def __init__(self, building, use, years, number) -> None:
        """This function initializes the stock item."""

        global DECONSTRUCTION_STATISTIC
        global REPLACEMENT_STATISTIC
        if not DECONSTRUCTION_STATISTIC:
            DECONSTRUCTION_STATISTIC = import_json(
                title="weibull", location="statistics"
            )
 
        self.building = building
        self.years = years
        self.use = use

        self.number = (
            BuildingNumber(number, self.years, self.use)
            if not isinstance(number, BuildingNumber)
            else copy.deepcopy(number)
        )

        assert self.number.check(throw_error=True), "NOO"
        self.development = {}
        return

    def __repr__(self) -> str:
        string = f"\n╔{'═'*63}╗\n║{str(self.building.code).center(63)}║\n{HED}\n║ year │{'total'.center(9)}│{'bare'.center(9)}│{'light'.center(9)}│{'medium'.center(9)}│{'deep'.center(9)}│ {'hss'.center(5)}║\n{HOR}\n║ init │ {self.number} ║"
        for dev, data in self.development.items():
            string = f"{string}\n║ {dev} │ {data.number} ║"
        string = f"{string}\n{END}"
        return string

    def __getitem__(self, __name: int | str) -> Any:
        return self.development[__name]

    def newYear(self, year: int) -> None:
        """This creates and initializes a new year."""
        if not self.development:
            self.development[year] = StockItem(
                self.building, self.use, self.years, self.number
            )
            return None
        else:
            assert (
                list(self.development.keys())[-1] == year - INCREMENT
            ), f"The new year must be one increment ({INCREMENT}) larger than the old year."
            old_ = self.development[year - INCREMENT]
            self.development[year] = StockItem(
                old_.building, old_.use, old_.years, old_.number
            )
            return None

    def calcDemolition(self, year: int) -> list[int]:
        """This function calculates the demolitions."""
        if self.years[-1] == 2022:
            return [
                0,
                0,
                0,
                0,
            ]  # NOTE: Immediately removes new buildings from the equation

        overhang = 0
        assert self.number.check(throw_error=True), "NOO"

        total = [0, 0, 0, 0]
        for bYear, amount in self.number.total.items():

            age = year - int(bYear)

            deconRate = DECONSTRUCTION_STATISTIC[
                self.building.typology if self.use != "Residential" else "Residential"
            ]["2100" if int(bYear) > 1945 else "1945"][str(age)]

            temp_amount = max(amount - self.number.protected[bYear], 0)

            demoAmount = int(temp_amount * deconRate + overhang)
            overhang = (temp_amount * deconRate + overhang) % 1
            # demoAmount = int(math.ceil(amount * deconRate))

            total = self.number.demo(bYear, demoAmount, total)

            self.number.check()
        OVERHANG = overhang

        assert self.number.check(throw_error=True), "NOO"
        return total

    def calcRefurbishment(self, light, medium, deep):
        """This function calculates the refurishments."""

        overflow = [None, None, None]

        assert self.number.check(throw_error=True), "NOO"
        d1, d2, d3 = (
            distribute_in_relation(light, self.number.bare),
            distribute_in_relation(medium, self.number.bare),
            distribute_in_relation(deep, self.number.bare),
        )

        self.number.check(throw_error=True)
        old1, old2, old3, old4 = (
            self.number.bare.values(),
            self.number.light.values(),
            self.number.medium.values(),
            self.number.deep.values(),
        )

        self.number.check(throw_error=True)
        self.number.bare, overflow[0] = remove_available(self.number.bare, d1)
        self.number.bare, overflow[1] = remove_available(self.number.bare, d2)
        self.number.bare, overflow[2] = remove_available(self.number.bare, d3)

        self.number.light = add_available(self.number.light, d1, overflow[0])
        self.number.medium = add_available(self.number.medium, d2, overflow[1])
        self.number.deep = add_available(self.number.deep, d3, overflow[2])

        self.number.check(throw_error=True)

        if LIGHT_RENO:
            if type(overflow[1]) is list:
                new1 = {k: o for k, o in zip(d1, overflow[1])}
                self.number.light, overflow[1] = remove_available(
                    self.number.light, new1
                )
                self.number.medium = add_available(
                    self.number.medium, new1, overflow[1]
                )
            if type(overflow[2]) is list:
                new2 = {k: o for k, o in zip(d2, overflow[2])}
                self.number.light, overflow[2] = remove_available(
                    self.number.light, new2
                )
                self.number.deep = add_available(self.number.deep, new2, overflow[2])

        self.number.check(throw_error=True)

        l, m, d = (
            sum([b - a for a, b in zip(old2, self.number.light.values())]),
            sum([b - a for a, b in zip(old3, self.number.medium.values())]),
            sum([b - a for a, b in zip(old4, self.number.deep.values())]),
        )
        return [-(l + m + d), l, m, d], overflow

    def calcConstruction(
        self,
        year: int,
        number: int,
        pop: int | None = None,
        sm: int | None = None,
        scenario: dict | None = None,
    ) -> int:
        """This..."""
        assert year not in self.number.bare
        assert year not in self.number.total

        if pop:
            number = math.ceil(
                number
                / self.building.residents
                * (
                    1
                    / get_share_of_used(
                        self.building.shared_of_used,
                        scenario["use of empty"],
                        self.building.use,
                        self.building.code,
                    )
                )
            )
        if sm:
            number = math.ceil(
                number
                / self.building.floor_area["Net Heated"]
                * (
                    1
                    / get_share_of_used(
                        self.building.shared_of_used,
                        scenario["use of empty"],
                        self.building.use,
                        self.building.code,
                    )
                )
            )

        assert number != None, "SHOULDNT BE THE CASE"

        self.number.total[year] = number
        self.number.bare[year] = number
        self.number.hs_old[year] = number
        self.number.light[year] = 0
        self.number.medium[year] = 0
        self.number.deep[year] = 0

        return number

    def calcHSS(self, year: int, scenario):
        """This function calculates the heating system exchange."""
        temp_hss_exchange = (
            scenario["HSS"]["exchange"]
            if scenario["HSS"]["exchange"] != None
            else CHANGE_HSS
        )
        temp_hss_lifetime = (
            scenario["HSS"]["lifetime"]
            if scenario["HSS"]["lifetime"] != None
            else LIFETIME_HSS
        )

        exchange = {}
        for (key, numberOld), numberNew in zip(
            self.number.hs_old.items(), self.number.hs_new.values()
        ):
            exchange[key] = [0, 0, 0]
            if (year - int(key)) % temp_hss_lifetime:
                continue

            replaceOld = numberOld
            replaceNew = numberNew

            refurbish = min(
                int((replaceOld + replaceNew) * temp_hss_exchange + 0.5),
                self.number.hs_old[key],
            )

            self.number.hs_old[
                key
            ] -= refurbish  # Subtracting from the old not renovated

            self.number.hs_mid[key] = min(
                self.number.hs_mid[key] + replaceOld, self.number.hs_old[key]
            )

            assert (
                refurbish >= 0
            ), "Why is the refurbishment negative, that is not supposed to happen"

            self.number.hs_new[key] += refurbish

            exchange[key][0] += replaceOld - refurbish
            exchange[key][1] += refurbish
            exchange[key][2] += replaceNew
        return exchange

    def get_total(self, year: int) -> int:
        return self.development[year].number.get_total()
