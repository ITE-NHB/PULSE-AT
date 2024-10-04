"""
characters.py

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file stores a collection of different special characters for use in graphs.
"""

# --------------------------------------------------------------------------------------------------
# Units
# --------------------------------------------------------------------------------------------------
M2 = r"$m^2$"  # square meters
KM2 = r"$m^2$"  # square kilometers
M3 = r"$m^3$"  # cubic meters
YEARS = r"$Years$"  # years
KWH = r"$kWh$"  # kilo watt hours
NR = r"$Nr.$"  # nr
T = r"$t$"  # ton


class EmissionInformation:
    """This class is used to store emission information"""
    def __init__(self, unit: str, description: str, tag: str, source: str) -> None:
        """This is the initializer for the EmissionInformation class"""
        self.unit = unit
        self.description = description
        self.source = source
        self.tag = tag
    def __repr__(self) -> str:
        return self.description
    def __bool__(self) -> bool:
        return True

EMISSION_INFO = {
    "AE_ACIDIFICATION": EmissionInformation(
        unit="mol H+-Eq",
        description="acidification",
        source="EF v3.1 EN15804",
        tag="acidification, accumulated exceedance (AE)",
    ),
    "GWP100": EmissionInformation(
        unit=r"$kg CO_2-Eq$",
        description="climate change: total",
        source="EF v3.1 EN15804",
        tag="climate change: total, global warming potential (GWP100)",
    ),
    "GWP100_BIOGENIC": EmissionInformation(
        unit=r"$kg CO_2-Eq$",
        description="climate change: biogenic",
        source="EF v3.1 EN15804",
        tag="climate change: biogenic, global warming potential (GWP100)",
    ),
    "GWP100_FOSSIL": EmissionInformation(
        unit=r"$kg CO_2-Eq$",
        description="climate change: fossil",
        source="EF v3.1 EN15804",
        tag="climate change: fossil, global warming potential (GWP100)",
    ),
    "GWP100_LAND_USE": EmissionInformation(
        unit=r"$kg CO_2-Eq$",
        description="climate change: land use and land use change",
        source="EF v3.1 EN15804",
        tag="climate change: land use and land use change, global warming potential (GWP100)",
    ),
    "CTUE": EmissionInformation(
        unit=r"$CTUe$",
        description="ecotoxicity",
        source="EF v3.1 EN15804",
        tag="ecotoxicity: freshwater, comparative toxic unit for ecosystems (CTUe)",
    ),
    "ADP_FUELS": EmissionInformation(
        unit=r"$MJ, net calorific value$",
        description="energy resources",
        source="EF v3.1 EN15804",
        tag="energy resources: non-renewable, abiotic depletion potential (ADP): fossil fuels",
    ),
    "P": EmissionInformation(
        unit=r"$kg P-Eq$",
        description="eutrophication: freshwater",
        source="EF v3.1 EN15804",
        tag="eutrophication: freshwater, fraction of nutrients reaching freshwater" +
            "end compartment (P)",
    ),
    "N": EmissionInformation(
        unit=r"$kg N-Eq$",
        description="eutrophication: marine",
        source="EF v3.1 EN15804",
        tag="eutrophication: marine, fraction of nutrients reaching marine end compartment (N)",
    ),
    "AE_EUTHROPHICATION": EmissionInformation(
        unit=r"$mol N-Eq$",
        description="eutrophication: terrestrial",
        source="EF v3.1 EN15804",
        tag="eutrophication: terrestrial, accumulated exceedance (AE)",
    ),
    "CTUH_CARCINOGENIC": EmissionInformation(
        unit=r"$CTUh$",
        description="human toxicity: carcinogenic",
        source="EF v3.1 EN15804",
        tag="human toxicity: carcinogenic, comparative toxic unit for human (CTUh)",
    ),
    "CTUH_NON_CARCINOGENIC": EmissionInformation(
        unit=r"$CTUh$",
        description="human toxicity: non-carcinogenic",
        source="EF v3.1 EN15804",
        tag="human toxicity: non-carcinogenic, comparative toxic unit for human (CTUh)",
    ),
    "U235": EmissionInformation(
        unit=r"$kBq U235-Eq$",
        description="ionising radiation",
        source="EF v3.1 EN15804",
        tag="ionising radiation: human health, human exposure efficiency relative to u235",
    ),
    "LAND_USE": EmissionInformation(
        unit=r"$dimensionless$",
        description="land use",
        source="EF v3.1 EN15804",
        tag="land use, soil quality index",
    ),
    "ADP_ELEMENTS": EmissionInformation(
        unit=r"$kg Sb-Eq$",
        description="material resources",
        source="EF v3.1 EN15804",
        tag="material resources: metals/minerals, abiotic depletion potential (ADP): " +
            "elements (ultimate reserves)",
    ),
    "ODP": EmissionInformation(
        unit=r"$kg CFC-11-Eq$",
        description="ozone depletion",
        source="EF v3.1 EN15804",
        tag="ozone depletion, ozone depletion potential (ODP)",
    ),
    "PARTICULATE_MATTER_FORMATION": EmissionInformation(
        unit=r"$disease incidence$",
        description="particulate matter formation",
        source="EF v3.1 EN15804",
        tag="particulate matter formation, impact on human health",
    ),
    "PHOTOCHEMICAL_OXIDANT_FORMATION": EmissionInformation(
        unit=r"$kg NMVOC-Eq$",
        description="photochemical oxidant formation",
        source="EF v3.1 EN15804",
        tag="photochemical oxidant formation: human health, tropospheric ozone " +
            "concentration increase",
    ),
    "WATER_USE": EmissionInformation(
        unit=r"$m^3 world eq. deprived$",
        description="water use",
        source="EF v3.1 EN15804",
        tag="water use, user deprivation potential (deprivation-weighted water consumption)",
    ),
}

# --------------------------------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------------------------------
B0 = r"$ß_0$"
B1 = r"$ß_1$"
