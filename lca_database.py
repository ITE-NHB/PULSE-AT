"""
lca_database.py
-------
Author: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

This is the script that generates the lca database.

A working brightway2 installation with ecoinvent 3.9.1 is necessary to run this script. 
An example of tutorial can be found here:
https://github.com/maximikos/Brightway2_Intro/blob/757a089c1645d059d9188f971d4a3a22c20f5563/BW2_tutorial.ipynb
As prerequisite, you should also have generated databases for 2030, 2040 and 2050 with premise.
An easy to use, example notebook is available here:
https://github.com/polca/premise/blob/master/examples/examples.ipynb
The databases should be named following this example: eidb_2040_REMIND-SSP2-PkBudg500
(more generically: "eidb_{year}_{IAM_model}-{prospective_scenario}")
All the products in the product file should be mapped to an existing brightway key
(see summplementary information files of the paper). 
In particular, the ones with 'TUG' should be replaced, as they are internal to the TU Graz database.
This also applies to the definition of LCA scenarios and data at the beginning of this script.
"""

import brightway2 as bw
import csv
import ast
import json

bw.projects.set_current("PULSE") #Choose your working brightway project

#----------------------------------------------------------------------------------------------------------------------------------------------------
# Definition of scenarios and LCA data. 
# This section is the only part of the LCA code that might have to be modified for better representation of another country.

scenarios_A4 = {
# Key is the PCR category, value is the quantity for A4 in km. 
# Each element of the list is for a specific lorry type in the following order:
# Lorry 16-32 ton (Euro 5); Lorry 7.5-16 ton (Euro 5); Lorry 3.5-7.5 ton (Euro 5); Lorry >32 ton (Euro 5)
# It corresponds to the input_data_A4 list below.
    "1.1." : [82.875, 0.875, 0, 25],
    "1.1.1." : [82.875, 0.875, 0, 25],
    "1.2." : [82.875, 0.875, 0, 25],
    "1.2.1." : [82.875, 0.875, 0, 25],
    "1.2.2." : [82.875, 0.875, 0, 25],
    "1.3." : [82.875, 0.875, 0, 25],
    "1.3.1." : [82.875, 0.875, 0, 25],
    "1.4." : [82.875, 0.875, 0, 25],
    "1.4.1." : [82.875, 0.875, 0, 25],
    "1.4.1.1" : [82.875, 0.875, 0, 25],
    "1.4.2." : [82.875, 0.875, 0, 25],
    "1.4.3." : [82.875, 0.875, 0, 25],
    "1.4.3.1" : [82.875, 0.875, 0, 25],
    "2.1." : [470, 0, 0, 0],
    "2.1.1." : [470, 0, 0, 0],
    "2.1.2." : [470, 0, 0, 0],
    "2.1.3." : [470, 0, 0, 0],
    "2.1.4." : [470, 0, 0, 0],
    "2.2.1." : [100, 0, 0, 0],
    "2.2.2." : [100, 0, 0, 0],
    "2.2.3." : [100, 0, 0, 0],
    "2.3.1." : [150, 0, 0, 0],
    "2.3.2." : [50, 0, 0, 0],
    "2.3.3." : [50, 0, 0, 0],
    "2.3.4." : [250, 0, 0, 0],
    "2.3.5." : [250, 0, 0, 0],
    "2.3.6." : [250, 0, 0, 0],
    "2.3.7." : [250, 0, 0, 0],
    "2.3.8." : [250, 0, 0, 0],
    "2.3.9." : [250, 0, 0, 0],
    "2.3.10." : [250, 0, 0, 0],
    "2.4." : [0, 35.2, 6.3, 90],
    "2.4.1." : [0, 35.2, 6.3, 90],
    "2.4.2." : [0, 35.2, 6.3, 90],
    "2.4.3." : [0, 35.2, 6.3, 90],
    "2.4.4." : [0, 35.2, 6.3, 90],
    "2.4.5." : [0, 35.2, 6.3, 90],
    "2.5." : [57.85, 3.15, 0, 60],
    "2.5.1." : [57.85, 3.15, 0, 60],
    "2.5.2." : [150, 0, 0, 0],
    "2.5.3." : [150, 0, 0, 0],
    "2.5.4." : [150, 0, 0, 0],
    "2.5.5." : [150, 0, 0, 0],
    "2.5.6." : [150, 0, 0, 0],
    "2.5.7." : [57.85, 3.15, 0, 60],
    "2.5.8." : [57.85, 3.15, 0, 60],
    "2.5.9." : [57.85, 3.15, 0, 60],
    "2.6." : [57.85, 3.15, 0, 60],
    "2.6.1." : [57.85, 3.15, 0, 60],
    "2.7." : [37.35, 4.15, 0, 90],
    "2.7.1." : [37.35, 4.15, 0, 90],
    "2.7.2." : [37.35, 4.15, 0, 90],
    "2.7.3." : [37.35, 4.15, 0, 90],
    "2.7.4." : [37.35, 4.15, 0, 90],
    "2.7.5." : [57.85, 3.15, 0, 60],
    "2.8." : [57.85, 3.15, 0, 60],
    "2.8.1." : [57.85, 3.15, 0, 60],
    "2.8.2." : [57.85, 3.15, 0, 60],
    "2.8.3." : [57.85, 3.15, 0, 60],
    "2.8.4." : [57.85, 3.15, 0, 60],
    "2.8.5." : [57.85, 3.15, 0, 60],
    "2.8.6." : [100, 0, 0, 0],
    "2.8.7." : [100, 0, 0, 0],
    "2.8.8." : [57.85, 3.15, 0, 60],
    "2.9." : [100, 0, 0, 0],
    "2.9.1.1." : [100, 0, 0, 0],
    "2.10." : [57.85, 3.15, 0, 60],
    "2.10.1." : [57.85, 3.15, 0, 60],
    "2.10.2." : [57.85, 3.15, 0, 60],
    "2.11." : [100, 0, 0, 0],
    "2.11.1." : [57.85, 3.15, 0, 60],
    "2.11.2." : [57.85, 3.15, 0, 60],
    "2.11.3." : [100, 0, 0, 0],
    "2.11.4." : [57.85, 3.15, 0, 60],
    "2.12.1." : [57.85, 3.15, 0, 60],
    "2.12.2." : [57.85, 3.15, 0, 60],
    "2.12.3." : [57.85, 3.15, 0, 60],
    "2.12.4." : [57.85, 3.15, 0, 60],
    "2.12.5." : [57.85, 3.15, 0, 60],
    "2.12.6." : [57.85, 3.15, 0, 60],
    "2.13." : [100, 0, 0, 0],
    "2.14.1." : [250, 0, 0, 0],
    "2.15.1." : [100, 0, 0, 0],
    "2.15.2." : [50, 0, 0, 0],
    "2.15.2.1." : [50, 0, 0, 0],
    "2.15.2.2." : [50, 0, 0, 0],
    "2.15.2.3." : [250, 0, 0, 0],
    "2.15.3." : [57.85, 3.15, 0, 60],
    "2.15.4." : [57.85, 3.15, 0, 60],
    "2.15.5." : [250, 0, 0, 0],
    "2.16." : [57.85, 3.15, 0, 60],
    "2.16.1." : [100, 0, 0, 0],
    "2.16.2." : [313, 0, 0, 0],
    "2.16.3." : [57.85, 3.15, 0, 60],
    "2.16.4." : [57.85, 3.15, 0, 60],
    "2.16.5." : [57.85, 3.15, 0, 60],
    "2.16.6." : [100, 0, 0, 0],
    "2.16.7." : [100, 0, 0, 0],
    "2.16.8." : [100, 0, 0, 0],
    "2.17." : [100, 0, 0, 0],
    "2.18." : [57.85, 3.15, 0, 60],
    "2.18.1." : [57.85, 3.15, 0, 60],
    "2.19." : [30.5, 30.5, 0, 60],
    "2.19.1." : [30.5, 30.5, 0, 60],
    "2.19.2." : [30.5, 30.5, 0, 60],
    "2.19.3." : [30.5, 30.5, 0, 60],
    "2.19.4." : [30.5, 30.5, 0, 60],
    "2.19.5." : [30.5, 30.5, 0, 60],
    "2.19.6." : [30.5, 30.5, 0, 60],
    "2.19.7." : [30.5, 30.5, 0, 60],
    "2.20." : [57.85, 3.15, 0, 60],
    "2.20.1." : [46.4, 42.25, 4.850, 10],
    "2.21." : [46.4, 42.25, 4.850, 10],
    "2.21.1." : [46.4, 42.25, 4.850, 10],
    "2.21.2." : [46.4, 42.25, 4.850, 10],
    "2.21.3." : [46.4, 42.25, 4.850, 10],
    "2.21.4." : [46.4, 42.25, 4.850, 10],
    "2.22." : [57.85, 3.15, 0, 60],
    "2.22.1." : [57.85, 3.15, 0, 60],
    "2.22.1.1" : [57.85, 3.15, 0, 60],
    "2.22.2." : [57.85, 3.15, 0, 60],
    "2.22.2.1." : [57.85, 3.15, 0, 60],
    "2.22.2.2." : [57.85, 3.15, 0, 60],
    "2.22.2.3." : [57.85, 3.15, 0, 60],
    "2.22.3." : [57.85, 3.15, 0, 60],
    "2.22.4." : [57.85, 3.15, 0, 60],
    "2.22.5." : [57.85, 3.15, 0, 60],
    "2.22.5.1." : [57.85, 3.15, 0, 60],
    "2.22.5.2." : [57.85, 3.15, 0, 60],
    "2.22.5.3." : [57.85, 3.15, 0, 60],
    "2.23." : [57.85, 3.15, 0, 60],
    "2.23.1." : [57.85, 3.15, 0, 60],
    "2.23.2." : [100, 0, 0, 0],
    "2.24." : [0, 35.2, 6.3, 90],
    "2.24.1." : [0, 35.2, 6.3, 90],
    "2.24.2." : [0, 35.2, 6.3, 90],
    "2.25." : [57.85, 3.15, 0, 60],
    "3." : [0, 28, 7, 100],
    "3.1." : [0, 28, 7, 100],
    "3.1.1." : [0, 28, 7, 100],
    "3.2." : [0, 28, 7, 100],
    "3.2.1." : [0, 28, 7, 100],
    "3.3." : [0, 28, 7, 100],
    "3.3.1." : [0, 28, 7, 100],
    "3.3.2." : [0, 28, 7, 100],
    "3.3.3." : [100, 0, 0, 0],
}

input_data_A4 = [
    ("eicutoff391", '774f0b2116e353e111ea31f3b84f9b60'), #'market for transport, freight, lorry 16-32 metric ton, EURO5' (ton kilometer, RER, None)
    ("eicutoff391", '9e4679ca5bd1ebfaf4bcd0169e59caf4'), #'market for transport, freight, lorry 7.5-16 metric ton, EURO5' (ton kilometer, RER, None)
    ("eicutoff391", '89623197c57b56d7c134a66cbe3e995d'), #'market for transport, freight, lorry 3.5-7.5 metric ton, EURO5' (ton kilometer, RER, None)
    ("eicutoff391", 'e76596f45bcb935639d775d8df91257e') #'market for transport, freight, lorry >32 metric ton, EURO5' (ton kilometer, RER, None)
]

scenario_losses_A5 = {
# Key is the waste category, value is the percentage of waste loss. 
    "wc_01" : 6,
    "wc_02" : 5,
    "wc_03" : 5.7,
    "wc_04" : 0,
    "wc_05" : 1,
    "wc_06" : 0,
    "wc_07" : 7,
    "wc_08" : 7,
    "wc_09" : 6.7,
    "wc_10" : 7,
    "wc_11" : 5,
    "wc_12" : 5,
    "wc_13" : 5,
    "wc_14" : 5,
    "wc_15" : 5,
    "wc_16" : 8.3,
    "wc_17" : 8.3,
    "wc_18" : 12.5,
    "wc_19" : 7.5,
    "wc_20" : 5.7,
    "wc_21" : 14.2,
    "wc_22" : 5,
    "wc_23" : 10,
    "wc_24" : 5,
    "wc_25" : 5,
    "wc_26" : 5,
    "wc_27" : 0,
    "wc_28" : 5,
    "wc_29" : 9.5,
    "wc_30" : 7.5,
    "wc_31" : 5,
    "wc_32" : 5,
    "wc_33" : 5,
    "wc_34" : 5,
    "wc_35" : 5,
    "wc_36" : 5,
    "wc_37" : 5,
}

input_data_A5C1 = {
    "Heizöl" : ("eicutoff391", '49c90be1ed9e14ba786bf050a5ca7878'), #'heat production, light fuel oil, at boiler 10kW, non-modulating' (megajoule, Europe without Switzerland, None)
    "Gasöl" : ("eicutoff391", 'b6bc259ec2679e2c6b9696e4ed334cfd'), #'heat and power co-generation, oil' (megajoule, AT, None)
    "Diesel" : ("eicutoff391", '0c8f3330261952e02d86355874fd2dd8'), #'diesel, burned in building machine' (megajoule, GLO, None)
    "Benzin" : ("eicutoff391", '0c8f3330261952e02d86355874fd2dd8'), #'diesel, burned in building machine' (megajoule, GLO, None)
    "Flüssiggas" : ("eicutoff391", '944f4d6357140424a2ed2bc5b8a2c60f'), #'propane, burned in building machine' (megajoule, GLO, None)
    "Erdgas" : ("eicutoff391", '944f4d6357140424a2ed2bc5b8a2c60f'), #'propane, burned in building machine' (megajoule, GLO, None)
    "Elektrische Energie" : ("eicutoff391", '6f61d8326ee98b75ab4136e87d0844c6'), #'market for electricity, medium voltage' (kilowatt hour, AT, None)
    "Fernwärme" : ('TUG', 'fe78fc75eafa46fdadc0a348cd40c820'), #Modelled for Austria
    "Brennholz" : ("eicutoff391", '1ba2cc981b5bfe68121c1e34a357e232'), #'heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014' (kilowatt hour, AT, None)
    "Biogene Brenn- und Treibstoffe" : ("eicutoff391", '1ba2cc981b5bfe68121c1e34a357e232'), #'heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014' (kilowatt hour, AT, None)
    "Brennbare Abfälle" : ("eicutoff391", '7ca4c09b524a2b348cd1d63e387e130f') #'heat, from municipal waste incineration to generic market for heat district or industrial, other than natural gas' (megajoule, AT, None)
}

assumptions_A5C1 = {
    "share_buildings_construction" : 0.59, #Taken from input-output tables sector decomposition
    "ratio_A5C1" : 0.045, #Derived from typical ratios for A5 and C1
    "volume_new_buildings" : 49170549,
    "volume_demolished_buildings" : 5814809,
    "NEA_BAU_2019" : { #Top-down data from the useful energy analysis. Dictionnary in TJ
        "Heizöl" : 323, 
        "Gasöl" : 118,
        "Diesel" : 8049,
        "Benzin" : 35,
        "Flüssiggas" : 160,
        "Erdgas" : 1275,
        "Elektrische Energie" : 2007,
        "Fernwärme" : 197,
        "Brennholz" : 2,
        "Biogene Brenn- und Treibstoffe" : 680,
        "Brennbare Abfälle" : 18
    }
}

input_data_B6B7B8 = {    
    'oil central heating, standard boiler': ('TUG', '49c90be1ed9e14ba786bf050a5ca7878_copy1'), #heat production, light fuel oil, at boiler 10kW, non-modulating (AT) - embodied removed
    'oil central heating, condensing boiler': ('TUG', '444ca2eb647396fb8b8b88c53322d6f0_copy1'), #heat production, light fuel oil, at boiler 10kW condensing, non-modulating (AT) - embodied removed
    'single stoves oil': ('TUG', '49c90be1ed9e14ba786bf050a5ca7878_copy1'), #heat production, light fuel oil, at boiler 10kW, non-modulating (AT) - embodied removed
    'gas central heating, standard boiler': ('TUG', 'c745bd82a38ab3cd83677fb32050a6ba_copy1'), #heat production, natural gas, at boiler atmospheric low-NOx non-modulating <100kW (AT) - embodied removed
    'gas central heating, condensing boiler': ('TUG', '08a8c898dfec55ccb38dace70475e015_copy1'), #heat production, natural gas, at boiler atm. low-NOx condensing non-modulating <100kW (AT) - embodied removed
    'gas central heating, condensing boiler, with solar thermal': ('TUG', '08a8c898dfec55ccb38dace70475e015_copy1'), #heat production, natural gas, at boiler atm. low-NOx condensing non-modulating <100kW (AT) - embodied removed
    'wood central heating': ('TUG', '56d1e925b1744ccb1c801047f2728b6d_copy1'), #heat production, mixed logs, at wood heater 6kW (AT) - embodied removed
    'pellets central heating': ('TUG', 'cc1d6fe92f62f55dbd3dec9054531128_copy1'), #heat production, wood pellet, at furnace 9kW, state-of-the-art 2014 (AT) - embodied removed
    'pellets central heating, with solar thermal': ('TUG', 'cc1d6fe92f62f55dbd3dec9054531128_copy1'), #heat production, wood pellet, at furnace 9kW, state-of-the-art 2014 (AT) - embodied removed
    'heat pump': ("eicutoff391", 'b253c79a76e57927a4c4ddae1fafd3df'), #Market for electricity, low voltage, (AT)  
    'electric direct heating': ("eicutoff391", 'b253c79a76e57927a4c4ddae1fafd3df'), #Market for electricity, low voltage, (AT)
    'electric direct heating, with solar thermal': ("eicutoff391", 'b253c79a76e57927a4c4ddae1fafd3df'), #Market for electricity, low voltage, (AT)         
    'district heating': ('TUG', 'fe78fc75eafa46fdadc0a348cd40c820'), #Created for Austria
    'not specified': ('TUG', 'c745bd82a38ab3cd83677fb32050a6ba_copy1'), #Assumed to be standard gas boiler
    'Final Space Cooling' : ('TUG', '6453fdcb4516b181aab04f9602ce53f5_copy1'), #cooling energy, from natural gas, at cogen unit with absorption chiller 100kW - embodied removed (AT)
    'B6.1' : ("eicutoff391", 'b253c79a76e57927a4c4ddae1fafd3df'), #Market for electricity, low voltage, (AT)
    'B6.2 & B6.3' : ("eicutoff391", 'b253c79a76e57927a4c4ddae1fafd3df'), #Market for electricity, low voltage, (AT)
    'B8' : ("eicutoff391", '68f3fd1076d3d424f5188efe3a2cb3b9'), #Market for transport, passenger car, small size, diesel, EURO 5
    'Water Use' : ("eicutoff391", '4fe1f2dae4830593ee2d608cb2d5ff2c') #market for tap water (Europe without Switzerland)
}

scenario_C2 = {
#Key is the waste category, values are in km.
#Assumed to be the same truck category for all distances, hence only one activity in the input data.

    "wc_01" : [30, 2.5, 0],
    "wc_02" : [30, 2.5, 0],
    "wc_03" : [30, 2.5, 0],
    "wc_04" : [30, 2.5, 0],
    "wc_05" : [30, 2.5, 0],
    "wc_06" : [30, 7.5, 0],
    "wc_07" : [30, 0, 100],
    "wc_08" : [30, 0, 95],
    "wc_09" : [30, 0, 85],
    "wc_10" : [30, 0, 25],
    "wc_11" : [30, 2.5, 0],
    "wc_12" : [30, 5, 30],
    "wc_13" : [30, 0, 40],
    "wc_14" : [30, 0, 5],
    "wc_15" : [30, 2.5, 60],
    "wc_16" : [30, 25, 50],
    "wc_17" : [30, 2.5, 95],
    "wc_18" : [30, 2.5, 95],
    "wc_19" : [30, 50, 0],
    "wc_20" : [30, 35, 0],
    "wc_21" : [30, 40, 0],
    "wc_22" : [30, 42.5, 5],
    "wc_23" : [30, 5, 85],
    "wc_24" : [30, 45, 0],
    "wc_25" : [30, 5, 40],
    "wc_26" : [30, 5, 40],
    "wc_27" : [30, 5, 45],
    "wc_28" : [30, 10, 65],
    "wc_29" : [30, 0, 95],
    "wc_30" : [30, 2.5, 0],
    "wc_31" : [30, 0, 100],
    "wc_32" : [30, 0, 100],
    "wc_33" : [30, 50, 0],
    "wc_34" : [30, 0, 100],
    "wc_35" : [30, 50, 0],
    "wc_36" : [30, 15, 0],
    "wc_37" : [30, 0, 75],
}

input_data_C2 = ("eicutoff391", '267c887af46bd684eb8daf39dd1a5818') #'market for transport, freight, lorry 16-32 metric ton, EURO6' (ton kilometer, RER, None)

input_data_C3C4 = {
    "wc_01" : ("eicutoff391", 'efd764591dd2304ae5d3fbf7d218b613'), #'market for waste brick' (kilogram, Europe without Switzerland, None)
    "wc_02" : ('TUG', '8e4df87628a74e7bbf6dfa1dcbef3c00'), #'market for waste gravel' (unit, AT, None)
    "wc_03" : ("eicutoff391", 'a64a5b1006d28078aa1cf248f37ca370'), #'market for waste concrete, not reinforced' (kilogram, Europe without Switzerland, None)
    "wc_04" : ("eicutoff391", '9e5edd5f63360237bed75eb20499a2da'), #'market for waste glass' (kilogram, AT, None)
    "wc_05" : ('TUG', '8e4df87628a74e7bbf6dfa1dcbef3c00'), #'market for waste gravel' (unit, AT, None)
    "wc_06" : ('TUG', '8e4df87628a74e7bbf6dfa1dcbef3c00'), #'market for waste gravel' (unit, AT, None)
    "wc_07" : ("eicutoff391", 'ff4b6d4a22e11a0f887a5e7a11742a17'), #'market for waste wood, untreated' (kilogram, AT, None)
    "wc_08" : ("eicutoff391", 'ff4b6d4a22e11a0f887a5e7a11742a17'), #'market for waste wood, untreated' (kilogram, AT, None)
    "wc_09" : ("eicutoff391", 'ff4b6d4a22e11a0f887a5e7a11742a17'), #'market for waste wood, untreated' (kilogram, AT, None)
    "wc_10" : ("eicutoff391", 'ff4b6d4a22e11a0f887a5e7a11742a17'), #'market for waste wood, untreated' (kilogram, AT, None)
    "wc_11" : ('TUG', '8e4df87628a74e7bbf6dfa1dcbef3c00_copy1'), #'market for waste metals' (unit, AT, None)
    "wc_12" : ("eicutoff391", 'ae670afc889d0d64b8fc64cf6d42e6e5'), #'market for waste plastic, mixture' (kilogram, AT, None)
    "wc_13" : ("eicutoff391", 'ff4b6d4a22e11a0f887a5e7a11742a17'), #'market for waste wood, untreated' (kilogram, AT, None)
    "wc_14" : ("eicutoff391", '57ab2b96022ceb4efb970f483b3d9079'), #'market for waste packaging paper' (kilogram, AT, None)
    "wc_15" : ("eicutoff391", 'c635696e2d023c772079c92be17e1e8b'), #'market for waste polyethylene' (kilogram, AT, None)
    "wc_16" : ("eicutoff391", '3a595a2954e84bc84737299e53b505ad'), #'market for waste mineral wool' (kilogram, Europe without Switzerland, None)
    "wc_17" : ("eicutoff391", 'ff4b6d4a22e11a0f887a5e7a11742a17'), #'market for waste wood, untreated' (kilogram, AT, None)
    "wc_18" : ("eicutoff391", '0d0a9e48f1c4030a758e7f32ae3a9b4a'), #'market for waste polyurethane' (kilogram, AT, None)
    "wc_19" : ("eicutoff391", '41a992469a0605d5984299557a1c758c'), #'market for waste cement-fibre slab' (kilogram, CH, None)
    "wc_20" : ("eicutoff391", 'a64a5b1006d28078aa1cf248f37ca370'), #'market for waste concrete, not reinforced' (kilogram, Europe without Switzerland, None)
    "wc_21" : ("eicutoff391", '8c88f8d09750efb1b71ad264482680f5'), #'market for waste gypsum' (kilogram, Europe without Switzerland, None)
    "wc_22" : ("eicutoff391", 'f2b022eb4b58b68393036ba5f904cb97'), #'market for waste bitumen' (kilogram, Europe without Switzerland, None)
    "wc_23" : ("eicutoff391", '3a05f9bc8b8419cf313207e4b8369889'), #'market for waste polypropylene' (kilogram, AT, None)
    "wc_24" : ("eicutoff391", '00a66355de37391f94102c28f9794744'), #'market for waste rubber, unspecified' (kilogram, Europe without Switzerland, None)
    "wc_25" : ("eicutoff391", '4ab826ef790dca1f3a809ebf76bede8d'), #'market for waste polyvinylchloride' (kilogram, AT, None)
    "wc_26" : ("eicutoff391", '4ab826ef790dca1f3a809ebf76bede8d'), #'market for waste polyvinylchloride' (kilogram, AT, None)
    "wc_27" : ("eicutoff391", '4ab826ef790dca1f3a809ebf76bede8d'), #'market for waste polyvinylchloride' (kilogram, AT, None)
    "wc_28" : ("eicutoff391", '4ab826ef790dca1f3a809ebf76bede8d'), #'market for waste polyvinylchloride' (kilogram, AT, None)
    "wc_29" : ("eicutoff391", '0d0a9e48f1c4030a758e7f32ae3a9b4a'), #'market for waste polyurethane' (kilogram, AT, None)
    "wc_30" : ("eicutoff391", '8c88f8d09750efb1b71ad264482680f5'), #'market for waste gypsum' (kilogram, Europe without Switzerland, None)
    "wc_31" : ("eicutoff391", '7450eb721da32ec1b14c8e7e1684b3de'), #'market for waste paper, unsorted' (kilogram, Europe without Switzerland, None)
    "wc_32" : ("eicutoff391", '014c50887c9d3f308c8b2ea3654907b6'), #'market for inert waste, for final disposal' (kilogram, CH, None)
    "wc_33" : ("eicutoff391", 'f04ff5258998b6a607333d69d377104d'), #'treatment of inert waste, sanitary landfill' (kilogram, Europe without Switzerland, None)
    "wc_34" : ("eicutoff391", '696decb7ee7c6a621897e95f471edee1'), #'market for hazardous waste, for incineration' (kilogram, Europe without Switzerland, None)
    "wc_35" : ("eicutoff391", 'c3986189fb3f544f1379f31d5382f020'), #'market for hazardous waste, for underground deposit' (kilogram, RER, None)
    "wc_36" : ("eicutoff391", 'c3986189fb3f544f1379f31d5382f020'), #'market for hazardous waste, for underground deposit' (kilogram, RER, None)
    "wc_37" : ("eicutoff391", '696decb7ee7c6a621897e95f471edee1') #'market for hazardous waste, for incineration' (kilogram, Europe without Switzerland, None)
}

#----------------------------------------------------------------------------------------------------------------------------------------------------
# Definition of basic functions

def change_background_db (eidb_name: str, foreground_name: str):
    foreground_db = bw.Database(foreground_name)
    for act in foreground_db:
         for exc in act.technosphere():
                if exc["input"][0] != foreground_name:
                    exc["input"] = (eidb_name, exc["input"][1])
                    exc.save()
    act.save()
    print(f"Background changed to {eidb_name}")

def perform_LCA(activity, methods: list, fu):
    results_list = []
    lca = bw.LCA({activity : fu}, methods[0])
    lca.lci()
    lca.lcia()
    for m in methods:
        lca.switch_method(m)
        lca.redo_lcia({activity : fu})
        results_list.append(lca.score)
    return(results_list)

def multiply_list(list: list, factor):
    new_list = [list[k]*factor for k in range(len(list))]
    return(new_list)

def add_list_dictionaries(dict1: dict, dict2: dict):
    dict = {}
    for key in dict1.keys():
        if isinstance(dict1[key], list):
            newlist = [dict1[key][k] + dict2[key][k] for k in range(len(dict1[key]))]
        else:
            newlist = dict1[key]
        dict[key]=newlist
    return(dict)

def substract_list_dictionaries(dict1: dict, dict2: dict, multiplier):
    dict = {}
    for key in dict1.keys():
        if isinstance(dict1[key], list):
            newlist = [(dict1[key][k] - dict2[key][k])*multiplier for k in range(len(dict1[key]))]
        else:
            newlist = dict1[key]
        dict[key]=newlist
    return(dict)

#---------------------------------------------------------------------------------------------------------------------------------------------------
# LCA calculation functions per life cycle stage.

def calculate_A1A3_year(year: int, eidb_name: str, methods: list):
    with open("input\Products_list.csv", "r") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        data_A1A3_1year = {}
        for row in csv_reader:
            A1A3_results_list = []
            key = row[0]
            if row[15] != "":
                if ast.literal_eval(row[15])[0] == "TUG":
                    ID_A1A3 = ast.literal_eval(row[15])
                else:
                    importID = ast.literal_eval(row[15])
                    ID_A1A3 = (eidb_name, importID[1])
            else:
                ID_A1A3 = ""
            if row[16] != "kg" and row[16] != "":
                density_A1A3 = float(row[7])
            else:
                density_A1A3 = 1
            if row[18] == "":
                factor_A1A3 = 1
            else:
                factor_A1A3 = float(row[18])
            if ID_A1A3 == "":
                A1A3_results_list.append(0 for i in range(len(methods)))
            else:
                data_A1A3_1year[key] = perform_LCA(bw.get_activity(ID_A1A3), methods, 1000*factor_A1A3/density_A1A3)
    print(f"Calculation for A1-A3 for {str(year)} is finished")
    return(data_A1A3_1year) #Unit for calculation is ton.



def calculate_A4_year(year: int, eidb_name: str, methods: list, scenarios: dict, input_data: list):

    impact_lorry_list = []

    for lorry in input_data:
        new_key = (eidb_name, lorry[1])
        impact_lorry_list.append(perform_LCA(bw.get_activity(new_key), methods, 1))
    
    with open("input\Products_list.csv", "r") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        data_A4_1year = {}
        for row in csv_reader:
            A4_results_list = [0 for i in range(len(impact_lorry_list[0]))]
            key = row[0]
            PCR_A4 = row[21]
            for i in range(len(impact_lorry_list)):
                temporary = [impact_lorry_list[i][j] for j in range(len(impact_lorry_list[i]))]
                for k in range(len(temporary)):
                    if PCR_A4 != "":
                        A4_results_list[k] += temporary[k]*scenarios[PCR_A4][i]
                    else:
                        A4_results_list[k] += temporary[k]*0
            data_A4_1year[key]=[A4_results_list[k] for k in range(len(A4_results_list))]

    print(f"Calculation for A4 for {str(year)} is finished")
    return(data_A4_1year) #Unit for calculation is ton.



def calculate_A5C1_year(year: int, eidb_name: str, methods: list, scenarios: dict, input_data: dict, assumptions: dict):

    impact_A5C1 = {}
    data_A5C1_1year = {}

    for key in assumptions["NEA_BAU_2019"].keys():
        if input_data[key][0] == "TUG":
            new_key = input_data[key]
        else:
            new_key = (eidb_name, input_data[key][1]) 
        act = bw.get_activity(new_key)
        if act["unit"] == "megajoule" :
              impact_A5C1[key] = perform_LCA(act, methods, assumptions["NEA_BAU_2019"][key]*1000*1000)
        elif act["unit"] == "kilowatt hour" :
              impact_A5C1[key] = perform_LCA(act, methods, assumptions["NEA_BAU_2019"][key]*1000*1000/3.6)     
        else:
              print("There is a problem with the units")

    total_impact_A5C1 = [sum(values) for values in zip(*impact_A5C1.values())]

    data_A5C1_1year["Construction"] = [assumptions["share_buildings_construction"]*(1-assumptions["ratio_A5C1"])*total_impact_A5C1[k]/assumptions["volume_new_buildings"] for k in range(len(total_impact_A5C1))]
    data_A5C1_1year["Demolition"] = [assumptions["share_buildings_construction"]*assumptions["ratio_A5C1"]*total_impact_A5C1[k]/assumptions["volume_demolished_buildings"] for k in range(len(total_impact_A5C1))]

    with open("input\Products_list.csv", "r") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        for row in csv_reader:
            key = row[0]
            waste_cat = row[22]
            if waste_cat != "":
                data_A5C1_1year[key]=scenarios[waste_cat]/100
            else:
                data_A5C1_1year[key]=0

    print(f"Calculation for A5 and C1 for {str(year)} is finished")
    return(data_A5C1_1year) #Unit for calculation is volume of building (either built or demolished).



def calculate_B6B7B8_year(year: int, eidb_name: str, methods: list, input_data: dict):

    data_B6B7B8_1year = {}

    for key in input_data.keys():
        if input_data[key][0] == "TUG":
            new_key = input_data[key]
        else:
            new_key = (eidb_name, input_data[key][1])  
        act = bw.get_activity(new_key)
        if act["unit"] == "megajoule" :
              data_B6B7B8_1year[key] = perform_LCA(act, methods, 1)
        elif act["unit"] == "kilowatt hour" :
              data_B6B7B8_1year[key] = perform_LCA(act, methods, 1/3.6) 
        elif act["unit"] == "kilometer" :
              data_B6B7B8_1year[key] = perform_LCA(act, methods, 1/(37*0.04344796)) 
        elif act["unit"] == "kilogram" :
              data_B6B7B8_1year[key] = perform_LCA(act, methods, 1000)
        else:
              print("There is a problem with the units")    

    print(f"Calculation for B6-B7-B8 for {str(year)} is finished")
    return(data_B6B7B8_1year) #Unit for calculation is megajoule except for water (m3).



def calculate_C2_year(year: int, eidb_name: str, methods: list, scenarios: dict, input_data: tuple):
    new_key = (eidb_name, input_data[1]) 
    impact_lorry_EURO6 = perform_LCA(bw.get_activity(new_key), methods, 1)

    with open("input\Products_list.csv", "r") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        data_C2_1year = {}
        for row in csv_reader:
            key = row[0]
            waste_cat = row[22]
            if waste_cat != "":
                C2_results_list = [sum(scenarios[waste_cat])*impact_lorry_EURO6[i] for i in range(len(impact_lorry_EURO6))]
            else:
                C2_results_list = [0*impact_lorry_EURO6[i] for i in range(len(impact_lorry_EURO6))]
            data_C2_1year[key]=C2_results_list
    
    print(f"Calculation for C2 for {str(year)} is finished")
    return(data_C2_1year) #Unit for calculation is ton.



def calculate_C3C4_year(year: int, eidb_name: str, methods: list, input_data: dict):
    
    impact_C3C4 = {}

    for key in input_data.keys():
        if input_data[key][0] == "TUG":
            new_key = input_data[key]
        else:
            new_key = (eidb_name, input_data[key][1])  
        
        temp = perform_LCA(bw.get_activity(new_key), methods, 1000)
        impact_C3C4[key]=[abs(temp[k]) for k in range(len(temp))]

    with open("input\Products_list.csv", "r") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        data_C3C4_1year = {}
        for row in csv_reader:
            key = row[0]
            waste_cat = row[22]
            if waste_cat != "":
                data_C3C4_1year[key] = impact_C3C4[waste_cat]
            else:
                data_C3C4_1year[key] = [0 for i in range(len(methods))]

    print(f"Calculation for C3-C4 for {str(year)} is finished")
    return(data_C3C4_1year)  #Unit for calculation is ton.

#---------------------------------------------------------------------------------------------------------------------------------------------------
#Main function to calculate all life cycle stages with prospective background

def calculate_life_cycle_all_years(eidb_name: str, foreground_name: str, IAM_model: str, prospective_scenario: str, methods: list):
    
    data_A1A3 = {}
    data_A4 = {}
    data_A5C1 = {}
    data_B6B7B8 = {}
    data_C2 = {}
    data_C3C4 = {}

    all_years = [i for i in range(2023, 2051)] 
    start_year = 2023
    base_years = [2023, 2030, 2040, 2050]

    change_background_db(eidb_name, foreground_name)
    data_A1A3[start_year]=calculate_A1A3_year(start_year, eidb_name, methods)
    data_A4[start_year]=calculate_A4_year(start_year, eidb_name, methods, scenarios_A4, input_data_A4)
    data_A5C1[start_year]=calculate_A5C1_year(start_year, eidb_name, methods, scenario_losses_A5, input_data_A5C1, assumptions_A5C1)
    data_B6B7B8[start_year] = calculate_B6B7B8_year(start_year, eidb_name, methods, input_data_B6B7B8)
    data_C2[start_year] = calculate_C2_year(start_year, eidb_name, methods, scenario_C2, input_data_C2)
    data_C3C4[start_year] = calculate_C3C4_year(start_year, eidb_name, methods, input_data_C3C4)    

    for year in base_years:
        if year != start_year: 
            superdb_name = f"eidb_{year}_{IAM_model}-{prospective_scenario}"
            change_background_db(superdb_name, foreground_name)

            data_A1A3[year]=calculate_A1A3_year(year, superdb_name, methods)
            data_A4[year]=calculate_A4_year(year, superdb_name, methods, scenarios_A4, input_data_A4)
            data_A5C1[year]=calculate_A5C1_year(year, superdb_name, methods, scenario_losses_A5, input_data_A5C1, assumptions_A5C1)
            data_B6B7B8[year] = calculate_B6B7B8_year(year, superdb_name, methods, input_data_B6B7B8)
            data_C2[year] = calculate_C2_year(year, superdb_name, methods, scenario_C2, input_data_C2)
            data_C3C4[year] = calculate_C3C4_year(year, superdb_name, methods, input_data_C3C4)
    
    change_background_db(eidb_name, foreground_name)

    for year in all_years:
        if year not in base_years:
            for k in range(len(base_years)-1):
                if base_years[k] < year < base_years[k+1]:
                    multiplier = (year-base_years[k])/(base_years[k+1]-base_years[k])
                    data_A1A3[year] = add_list_dictionaries(data_A1A3[base_years[k]], substract_list_dictionaries(data_A1A3[base_years[k+1]], data_A1A3[base_years[k]], multiplier))
                    data_A4[year] = add_list_dictionaries(data_A4[base_years[k]], substract_list_dictionaries(data_A4[base_years[k+1]], data_A4[base_years[k]], multiplier))
                    data_A5C1[year] = add_list_dictionaries(data_A5C1[base_years[k]], substract_list_dictionaries(data_A5C1[base_years[k+1]], data_A5C1[base_years[k]], multiplier))
                    data_B6B7B8[year] = add_list_dictionaries(data_B6B7B8[base_years[k]], substract_list_dictionaries(data_B6B7B8[base_years[k+1]], data_B6B7B8[base_years[k]], multiplier))
                    data_C2[year] = add_list_dictionaries(data_C2[base_years[k]], substract_list_dictionaries(data_C2[base_years[k+1]], data_C2[base_years[k]], multiplier))
                    data_C3C4[year] = add_list_dictionaries(data_C3C4[base_years[k]], substract_list_dictionaries(data_C3C4[base_years[k+1]], data_C3C4[base_years[k]], multiplier))

    with open(f"data\lca\{prospective_scenario}_A1A3.json", "w") as json_file:
        json.dump(data_A1A3, json_file)
    with open(f"data\lca\{prospective_scenario}_A4.json", "w") as json_file:
        json.dump(data_A4, json_file)
    with open(f"data\lca\{prospective_scenario}_A5C1.json", "w") as json_file:
        json.dump(data_A5C1, json_file)
    with open(f"data\lca\{prospective_scenario}_B6B7B8.json", "w") as json_file:
        json.dump(data_B6B7B8, json_file)
    with open(f"data\lca\{prospective_scenario}_C2.json", "w") as json_file:
        json.dump(data_C2, json_file)
    with open(f"data\lca\{prospective_scenario}_C3C4.json", "w") as json_file:
        json.dump(data_C3C4, json_file)

#---------------------------------------------------------------------------------------------------------------------------------------------------
#Main function to run

methods_list = [m for m in bw.methods if 'EF v3.1 EN15804' in str(m)]

calculate_life_cycle_all_years("eicutoff391", "TUG", "REMIND", "SSP2-PkBudg500", methods_list)