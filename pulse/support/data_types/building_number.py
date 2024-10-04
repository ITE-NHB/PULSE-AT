"""
building_number.py
---------------------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the data type building components
"""
# --------------------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------

# FUNCTIONS
from ..file_handling import import_json
from ..variables import distribute_fully

# --------------------------------------------------------------------------------------------------
# Variables
# --------------------------------------------------------------------------------------------------
# Only gets initialized upon first function call of getDistribution
CONSTRUCTION_STATISTIC = None

# Describes the rates with which buildings get demolished. in this case 100% for bare, 100% for
# light, 0% for medium and deep
DEMO_LEVEL = (
    1,
    1,
    0,
    0,
)

# --------------------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------------------
class BuildingNumber:
    """This is a class to deal with building number"""

    def __init__(self, numbers: dict, years: range, use: str) -> None:
        """This function initializes the building number."""
        global CONSTRUCTION_STATISTIC
        if not CONSTRUCTION_STATISTIC:
            CONSTRUCTION_STATISTIC = import_json(
                title="constructionStatistic", location="statistics"
            )

        construction = CONSTRUCTION_STATISTIC[use][str(years[0])]
        assert (
            round(sum(construction.values()), 10) == 1
        ), f"Check the construction statistics. They should add up to 1, but are adding to: {sum(construction.values())}"

        self.total = distribute_fully(numbers["total"], construction)
        self.bare: dict = distribute_fully(
            numbers["total"] - numbers["light"] - numbers["medium"] - numbers["deep"],
            construction,
        )
        self.light = distribute_fully(numbers["light"], construction)
        self.medium = distribute_fully(numbers["medium"], construction)
        self.deep = distribute_fully(numbers["deep"], construction)
        self.protected = distribute_fully(numbers["protected"], construction)
        self.hs_old = distribute_fully(numbers["total"], construction)
        self.hs_mid = {k: 0 for k in self.hs_old}
        self.hs_new = {k: 0 for k in self.hs_old}

        # self.demolition =   {k:0 for k in self.total}
        # self.newRefurb =    {k:[0,0,0] for k in self.total}

        self.check(throw_error=True)

    def __repr__(self) -> str:
        return f"{
            sum(self.total.values()):7,
        } │ {
            sum(self.bare.values()):7,
        } │ {sum(self.light.values()):7,} │ {sum(self.medium.values()):7,} │ {sum(self.deep.values()):7,} │ {sum(self.hs_new.values())/sum(self.total.values()) * 100 :3.0f}%"

    def check(self, throw_error=True):
        """This function is checking if everything is valid"""
        if not throw_error:
            return sum(
                [
                    sum(self.bare.values()),
                    sum(self.light.values()),
                    sum(self.medium.values()),
                    sum(self.deep.values()),
                ]
            ) == sum(self.total.values())
        assert sum(
            [
                sum(self.bare.values()),
                sum(self.light.values()),
                sum(self.medium.values()),
                sum(self.deep.values()),
            ]
        ) == sum(self.total.values()), "The building numbers dont add up"
        assert sum(self.hs_old.values()) + sum(self.hs_new.values()) == sum(
            self.total.values()
        )
        return True

    def demoHSS(self, year, amount):
        """This function demolishes the heating system adjacent things."""
        if self.hs_old[year] >= amount:
            self.hs_old[year] -= amount
        else:
            net_amount_ = amount - self.hs_old[year]
            self.hs_old[year] = 0
            self.hs_new[year] -= net_amount_

            if self.hs_new[year] < 0:
                self.hs_new[year] = 0

        # Making sure it doesnt become lower than old
        if self.hs_new[year] < self.hs_old[year]:
            self.hs_old[year] = self.hs_old[year]

    def demo(self, year, amount, total):
        """Thus function demolishes the buildings"""
        # DEMOLISH BARE
        net_amount = int(amount * DEMO_LEVEL[0] + 0.5)

        if self.bare[year] >= net_amount:
            self.total[year] -= net_amount
            self.bare[year] -= net_amount
            total[0] += net_amount
            self.demoHSS(year, net_amount)
            return total

        total[0] = self.bare[year]
        self.total[year] -= self.bare[year]
        net_amount -= self.bare[year]
        self.demoHSS(year, self.bare[year])
        self.bare[year] = 0

        if not DEMO_LEVEL[1]:
            return total
        net_amount = int(net_amount / DEMO_LEVEL[0] * DEMO_LEVEL[1] + 0.5)

        if self.light[year] >= net_amount:
            self.total[year] -= net_amount
            self.light[year] -= net_amount
            total[1] += net_amount
            self.demoHSS(year, net_amount)
            return total

        total[1] = self.light[year]
        self.total[year] -= self.light[year]
        net_amount -= self.light[year]
        self.demoHSS(year, self.light[year])
        self.light[year] = 0

        if not DEMO_LEVEL[2]:
            return total
        net_amount = int(net_amount / DEMO_LEVEL[1] * DEMO_LEVEL[2] + 0.5)

        if self.medium[year] >= net_amount:
            self.total[year] -= net_amount
            self.medium[year] -= net_amount
            total[2] += net_amount
            self.demoHSS(year, net_amount)
            return total

        total[2] = self.medium[year]
        self.total[year] -= self.medium[year]
        net_amount -= self.medium[year]
        self.demoHSS(year, self.medium[year])
        self.medium[year] = 0

        if not DEMO_LEVEL[3]:
            return total
        net_amount = int(net_amount / DEMO_LEVEL[2] * DEMO_LEVEL[3] + 0.5)

        if self.deep[year] >= net_amount:
            self.total[year] -= net_amount
            self.deep[year] -= net_amount
            total[3] += net_amount
            self.demoHSS(year, net_amount)
            return total

        total[3] = self.deep[year]
        self.total[year] -= self.deep[year]
        net_amount -= self.deep[year]
        self.demoHSS(year, self.deep[year])
        self.deep[year] = 0

        return total

    def listify(self) -> list:
        self.check()
        return [
            sum(self.bare.values()),
            sum(self.light.values()),
            sum(self.medium.values()),
            sum(self.deep.values()),
        ]

    def listify_hss(self) -> list:

        return [
            max(sum(self.hs_old.values()) - sum(self.hs_old.values()), 0),
            min(sum(self.hs_old.values()), sum(self.hs_old.values())),
            max(sum(self.hs_new.values()), 0),
        ]

    def get_total(self) -> int:
        return sum(self.total.values())
