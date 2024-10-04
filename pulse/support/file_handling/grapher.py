"""
grapher.py
----------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file deals with the data type code
"""

# --------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------

import copy
import logging
import seaborn as sns
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LogNorm
import numpy as np
from scipy.ndimage import gaussian_filter1d
import locale

locale.setlocale(locale.LC_ALL, '')


from pulse.support.file_handling.data_adaption import (
    cummulate,
    dict_merge,
    find_top,
    group_products,
    handle_data,
    invert,
    title_for_export
)


# --------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------

# VARIABLES
from ..variables import M2, YEARS, KWH, NR, T, INDICATOR_NAMES, EMISSION_INFO

# FUNCTIONS
from ..variables import (
    combine_colors,
    adapt_detail,
    color_rand,
    color_range,
    hex_to_rgba,
)
from .exporter import export_csv_from_dict
from .importer import import_json

# CLASSES
from ..variables import Detail, Impact

# --------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------
NUMBERS, PRODUCTS, ENERGY, LCA, COMPARE = range(5)

THICK = 1
THIN = 0.1
CUTOFF = 0.1
MAP = 10
COLORS = {}

# --------------------------------------------------------------------------------------
# Classes
# --------------------------------------------------------------------------------------

class Graph:
    """A class for graph class."""

    def __init__(
        self,
        data: dict,
        kind: int,
        buildings: dict,
        scenario: str,
        impact: Impact = Impact.GWP100,
    ):
        """The initializer for the grouped products."""
        self.data = copy.deepcopy(data)
        self.kind = kind
        self.buildings = buildings
        self.scenario = scenario
        self.impact = impact

        global INDICATOR_NAMES
        if not INDICATOR_NAMES:
            INDICATOR_NAMES = import_json(title="impactCategories", location="data/lca")

    def plot(self, **kwargs):
        """This function plots."""
        try:
            if self.kind == NUMBERS:
                return_ = self.plot_number(**kwargs)
            elif self.kind == PRODUCTS:
                return_ = self.plot_products(**kwargs)
            elif self.kind == ENERGY:
                return_ = self.plot_energy(**kwargs)
            elif self.kind == LCA:
                return_ = self.plot_LCA(**kwargs)
            elif self.kind == COMPARE:
                return_ = self.plot_comp(**kwargs)
            else:
                raise NameError(f"{self.kind} is not a valid option for graphing.")
            return return_
        except NameError as err:
            logging.error(err)
            return None
        except AttributeError as err:
            logging.error(err)
            return None
        except AssertionError as err:
            logging.error(err)
            return None

    def plot_number(self, kind: str, **kwargs) -> None:
        """This function plots numbers."""
        if kind == "total":
            return self.plot_number_total(**kwargs)
        if kind == "subgroup":
            return self.plot_number_subgroup(**kwargs)
        raise NameError(f"'{kind}' is not a valid option for plotting numbers!")

    def plot_products(self, kind: str, **kwargs) -> None:
        """This function plots products."""
        if kind == "total":
            return self.plot_products_total(**kwargs)
        if kind == "category":
            return self.plotProductsCategory(**kwargs)
        if kind == "top":
            return self.plot_top(**kwargs)
        raise NameError(f"'{kind}' is not a valid option for plotting products!")

    def plot_energy(self, kind: str, **kwargs) -> None:
        """This function plots energy."""
        if kind == "category":
            return self.plotEnergyCategory(**kwargs)
        if kind == "hss":
            return self.plotEnergyHSS(**kwargs)
        if kind == "heatmap":
            return self.plotEnergyHeatmap(**kwargs)
        if kind == "top":
            return self.plot_top(**kwargs)
        raise NameError(f"'{kind}' is not a valid option for plotting energy!")

    def plot_LCA(self, kind: str, **kwargs) -> None:
        """This function plots lca."""
        if kind == "category":
            return self.plotLCACategory(**kwargs)
        if kind == "products":
            return self.plotLCAProducts(**kwargs)
        if kind == "components":
            return print("Grouped LCA is not yet implemented!")
        if kind == "sankey":
            return self.plotSankey(**kwargs)
        raise NameError(
            f"'{kind}' is not a valid option for plotting life cycle assesments!"
        )

    def plot_comp(self, kind: str, **kwargs) -> None:
        """This function plots comparison graphs."""
        if kind == "numbers":
            return print("Numbers Comp is not yet implemented!")
        if kind == "products":
            return print("Product Comp is not yet implemented!")
        if kind == "energy":
            return print("Energy Comp is not yet implemented!")
        if kind == "lca":
            return self.plotCompYearlyLCA(**kwargs)
        if kind == "lca stages":
            return self.plotCompLCAStages(**kwargs)
        raise NameError(f"'{kind}' is not a valid option for plotting comparisonts!")

    def plot_top(
            self,
            number: int | str = 10,
            selection: str | list[str] = "heating",
            color: str ='range',
        ) -> None:
        """Plots the top of a specified graph."""
        years = list(self.data.keys())
        selection = selection if isinstance(selection, list) else [selection]

        if number == "max":
            number = len(self.data[years[0]][selection[0]]["AT"])

        assert isinstance(number, int)
        typologies = find_top(self.data, number, years=years, selection=selection)

        data = {}
        for typology in typologies:
            data[typology] = [
                sum([adapt_detail(self.data[year][sel]['AT'][typology], Detail.GROUPED) for sel in selection])
                for year in years
            ]

        if color == "range":
            cols = dict(zip(typologies, color_range("#63DFFF", "#FFAE63", number)))
        elif color == "random":
            cols = dict(zip(typologies, color_rand(number)))
        else:
            raise KeyError (f"color: {color} is not valid. Must be range or random")

        top = f'Top {number}' if isinstance(number,int) else 'All'

        title = f"{self.scenario} {top} typologie{'s' if number!=1 else ''} energy demand ({str(selection).replace("[","").replace("]","").replace("'","")})"

        setup(box=[True, False, False, False])
        export_csv_from_dict(data, years, title=title_for_export(title), location="output/csv",mode=0)
        graph(data, x=years, method="stackgraph", title=title, colors=cols)
        save(f"{title} {color.capitalize()} Colors", YEARS, KWH if selection != 'water' else "l", cols)

    def plot_number_total(
        self,
        selection: str = "construction",
        method: str = "linegraph",
        colors: str = "standard",
        sm: bool = True
    ) -> None:
        """This function plots the most simple data.
        Selection: 'total', 'demolition', 'refurbishment', 'construction', 'heating system'
        """
        assert not (
            selection == "refurbishment" and method != "linegraph"
        ), "Parts of the refurbishment graph go into the negative"
        setup(box=[True, False, False, False])
        manage_colors(colors)

        temp = f" ({M2})" if sm else f" ({NR})"
        title = f"{self.scenario} - numbers - {selection} {temp}"
        years = list(self.data.keys())

        filteredData = {
            year: de_list(d['AT'], self.buildings, sm=sm)
            for year, d in filterSubcategory(self.data, selection).items()
        }

        handles = {
            'total' : ['standard', 'light', 'medium', 'deep'],
            'construction' : ['construction'],
            'demolition' : ['standard', 'light', 'medium', 'deep'],
            'refurbishment' : ['standard', 'light', 'medium', 'deep'],
            'heating system' : ['old replacement', 'upgrade', 'new replacement'],
        }


        data = handle_data(filteredData, handle=handles[selection])
        export_csv_from_dict(data, years, title=title_for_export(title), location="output/csv")
        graph(data, method=method, x=years, colors=COLORS[colors], title=title_for_export(title))
        save(
            title=title,
            x=YEARS,
            y=f"Amount {temp}",
            color=COLORS[colors],
            method=method,
        )
        return None

    def plot_number_subgroup(
        self,
        use: bool = False,
        typology: bool = False,
        years: bool = False,
        construction: bool = False,
        energy: bool = False,
        selection: str = "total",
        sm: bool = True,
        colors: str = "standard",
        method: str = "stackgraph",
        country: str = "AT",
    ) -> None:
        """This function plots the building stock number development based on a
        selection of subgroups."""
        assert selection != 'refurbishment', "Cannot use refurbishments for subgroup plotting."
        years_ = list(self.data.keys())
        manage_colors(colors)
        data = {}
        title = ""
        if use:
            title = f"{title}use,"
        if typology:
            title = f"{title}typology, "
        if years:
            title = f"{title}years, "
        if construction:
            title = f"{title}construction type, "
        if energy:
            title = f"{title}energy standard, "
        commas = title.count(",")
        if commas:
            oldP = 0
            for i in range(1, commas + 1):
                pos = title.find(",", oldP, len(title))
                if i == commas - 1:
                    title = title[:pos] + " and" + title[pos + 1 :]
                if i == commas:
                    title = title[:pos] + (f" ({M2})" if not sm else f" ({NR})")
                oldP = pos
        for building in self.buildings.values():
            code = ""
            if use or years:
                code = f"{code}{building.use} "
            if typology:
                code = f"{code}{building.code.typology} "
            if years:
                code = f"{code}{building.code.years[0]}-{building.code.years[1]} "
            if construction:
                code = f"{code}{building.code.constructionType} "
            if energy:
                code = f"{code}{building.code.energyStandard} "
            if code == "":
                raise (
                    AttributeError(
                        f"There are not attributes defined. There shall be no graph"
                    )
                )
            if code[-1] == " ":
                code = code[:-1]
            if code not in data:
                data[code] = [0 for _ in years_]
            for n, year in enumerate(years_):
                temp = (
                    self.data[year][selection][country][str(building.code)]
                    if str(building.code) in self.data[year][selection][country]
                    else [0]
                )
                data[code][n] += (
                    int(sum(temp) * (building.floor_area["Gross"] if sm else 1) + 0.5)
                    if isinstance(temp, list)
                    else int(temp * (building.floor_area["Gross"] if sm else 1))
                )
        comboColors = {}
        for key in data:
            comboColors[key] = combine_colors(
                *[COLORS[colors][key_] for key_ in key.split(" ")]
            )
        setup(box=[True, False, False, False])
        title = f"{self.scenario} - numbers - subgroup - {selection} - {title}"
        graph(data, method=method, x=years_, colors=comboColors, title=title)
        csv(title=title_for_export(title), data=data, header=years_)
        save(title=title_for_export(title), x="Year", y=f"Area ({M2})", color=comboColors, method=method)

    def plot_products_total(
        self, 
        selection: str = "total", 
        method: str = "linegraph",
        colors: str = "standard"
    ) -> None :
        """This"""

        assert selection in ['total', 'construction', 'demolition'], (
            "Plot Products Total - Has to be either total, construction or demolition"
        )


        data = {
            selection : [
                sum(
                    adapt_detail(self.data[year][selection], Detail.GROUPED)
                    .dictify()
                    .values()
                )
                for year in self.data
            ]
        }
        years = list(self.data.keys())
        setup(box=[True, False, False, False])
        title = f"{self.scenario} - Total Products {selection.capitalize()} (Tons)"
        manage_colors(colors)

        graph(data, method=method, x=years, colors=COLORS[colors], title=title)
        save(title=title, x=YEARS, y=f"Mass ({T})", color=COLORS[colors], method=method)

    def plotProductsCategory(
        self,
        positive: list[str] | str = "total",
        negative: list[str] | str | None = None,
        detail: int = 2,
        colors: str = "standard",
        method: str = "stackgraph",
    ) -> None:
        """This function plots grouped products."""
        manage_colors(colors)
        years = list(self.data.keys())
        pos_grouped, pos_all = group_products(
            filterSubcategory(copy.deepcopy(self.data), positive), x=years, detail=detail
        )
        neg_grouped, neg_all = group_products(
            filterSubcategory(copy.deepcopy(self.data), negative), x=years, detail=detail
        )
        
        setup(box=[True if not negative else False, False, False, False])

        if 'construction' in positive and \
           'refurbishment in' in positive and \
           'replacement' in positive:
            pos_label = 'All Product Flows In'
        else:
            pos_label = str(positive).replace("[","").replace("]","")

        if 'construction' in positive and \
           'refurbishment in' in positive and \
           'replacement' in positive:
            neg_label = 'All Product Flows Out'
        else:
            neg_label = str(negative).replace("[","").replace("]","")

        title = f"{self.scenario} - products - categories {pos_label}{' vs ' if negative else ''}{neg_label if negative else ''} (t)"
        graph(
            pos_grouped,
            method=method,
            x=years,
            colors=COLORS[colors],
            title=f"{title} - positive",
        )
        assert isinstance(pos_all, dict)
        export_csv_from_dict(title=title_for_export(f"{self.scenario} - products - categories {pos_label}"), data=pos_all, header=years, location='output/csv', mode=0)
        if neg_grouped:
            graph(
                invert(neg_grouped),
                x=years,
                colors=COLORS[colors],
                method=method,
                title=f"{title} - negative",
            )
            plt.axhline(y=0, color="#000000")

            assert isinstance(neg_all, dict)
            export_csv_from_dict(title=title_for_export(f"{self.scenario} - products - categories {neg_label}"), data=neg_all, header=years, location='output/csv', mode=0)
        save(title, x=YEARS, y="Amount (t)", color=COLORS[colors], method=method)

    def plotEnergyCategory(
        self,
        hss=False,
        method="stackgraph",
        colors: str = "standard",
        country: str = "AT",
    ) -> None:
        manage_colors(colors)
        years_ = list(self.data.keys())
        data = {}
        csv_data = {"Residential": {}, "Non-residential": {}}
        for key_ in self.data[years_[0]]:
            if key_ == "electricity" or (key_ == "heating" and hss):
                
                subkeys = []
                for typo in self.data[years_[0]][key_][country].values():
                    for hs in typo:
                        if hs not in subkeys:
                            subkeys.append(hs)
                subkeys.sort()

                for subkey_ in subkeys:
                    data[subkey_] = [
                        sum(
                            [
                                self.data[year][key_][country][typo][subkey_]
                                if subkey_ in self.data[year][key_][country][typo]
                                else 0
                                for typo in self.data[year][key_][country]
                            ]
                        )
                        for year in years_
                    ]
                    csv_data["Residential"][subkey_] = [
                        sum(
                            [
                                self.data[year][key_][country][typo][subkey_]
                                if subkey_ in self.data[year][key_][country][typo]
                                else 0
                                for typo in self.data[year][key_][country]
                                if typo[3:6] in ["SFH", "TEH", "MFH", "ABL"]
                            ]
                        )
                        for year in years_
                    ]
                    csv_data["Non-residential"][subkey_] = [
                        sum(
                            [
                                self.data[year][key_][country][typo][subkey_]
                                if subkey_ in self.data[year][key_][country][typo]
                                else 0
                                for typo in self.data[year][key_][country]
                                if typo[3:6] not in ["SFH", "TEH", "MFH", "ABL"]
                            ]
                        )
                        for year in years_
                    ]
            else:
                data[key_] = [
                    adapt_detail(self.data[year][key_], Detail.GROUPED)
                    for year in years_
                ]
                csv_data["Residential"][key_] = [
                    sum(
                        [
                            adapt_detail(self.data[year][key_], Detail.TYPOLOGY)["AT"][
                                typo
                            ]
                            for typo in adapt_detail(
                                self.data[year][key_], Detail.TYPOLOGY
                            )["AT"]
                            if typo[3:6] in ["SFH", "TEH", "MFH", "ABL"]
                        ]
                    )
                    for year in years_
                ]
                csv_data["Non-residential"][key_] = [
                    sum(
                        [
                            adapt_detail(self.data[year][key_], Detail.TYPOLOGY)["AT"][
                                typo
                            ]
                            for typo in adapt_detail(
                                self.data[year][key_], Detail.TYPOLOGY
                            )["AT"]
                            if typo[3:6] not in ["SFH", "TEH", "MFH", "ABL"]
                        ]
                    )
                    for year in years_
                ]

        title = f"{self.scenario} - energy - demand per category{' including hss' if hss else ''} ({KWH})"
        setup(box=[True, False, False, False])
        graph(data=data, x=years_, colors=COLORS[colors], method=method, title=title)
        csv(title=f"{title}_res", data=csv_data["Residential"], header=years_)
        csv(title=f"{title}_non_res", data=csv_data["Non-residential"], header=years_)
        csv(title=title, data=data, header=years_)
        save(title, YEARS, KWH, color=COLORS[colors])
        return None

    def plotEnergyHSS(self, method="stackgraph", colors: str = "standard") -> None:
        """This function plots the energy heating systems."""
        manage_colors(colors)
        years_ = list(self.data.keys())
        data = {}
        csv_data = {"Residential": {}, "Non-residential": {}}

        for country in self.data[years_[0]]["heating"]:
            for typology in self.data[years_[0]]["heating"][country]:
                for component in self.data[years_[0]]["heating"][country][typology]:
                    if component not in data:
                        data[component] = [0 for _ in years_]
                    if component not in csv_data["Residential"]:
                        csv_data["Residential"][component] = [0 for _ in years_]
                    if component not in csv_data["Non-residential"]:
                        csv_data["Non-residential"][component] = [0 for _ in years_]
                    for pos, year in enumerate(years_):

                        if typology[3:6] in ["SFH", "TEH", "MFH", "ABL"]:
                            csv_data["Residential"][component][pos] += self.data[year][
                                "heating"
                            ][country][typology][component]
                        else:
                            csv_data["Non-residential"][component][pos] += self.data[
                                year
                            ]["heating"][country][typology][component]

                        data[component][pos] += self.data[year]["heating"][country][
                            typology
                        ][component]

        data = dict(sorted(data.items()))
        title = f"{self.scenario} - energy - heating demand by heating system"
        setup(box=[True, False, False, False])
        graph(data, method=method, x=years_, colors=COLORS[colors], title=title)
        csv(title=title, data=data, header=years_)
        csv(title=f"{title}_res", data=csv_data["Residential"], header=years_)
        csv(title=f"{title}_non_res", data=csv_data["Non-residential"], header=years_)

        save(title=title, x=YEARS, y=KWH, color=COLORS[colors], method=method)
        return None

    def plotEnergyHeatmap(
            self, 
            years: list[int] = [2023, 2050],
            cmap: str = 'plasma'
        ) -> None:
        """This function plots an energy heatmap"""

        dfs = {
            year_: pd.DataFrame(self.data[year_]["heating"]["AT"]) for year_ in years
        }

        for year, df in dfs.items():
            title = f"{self.scenario} - energy - heating systems heat map ({year})"
            plt.figure(figsize=(40, 10), dpi=300)

            plt.clf()

            plt.subplots_adjust(left=0.3)
            plt.xticks(fontsize=2)
            plt.yticks(fontsize=4)
            sns.heatmap(
                df,
                annot=False,
                cmap=cmap,
                norm=LogNorm(vmin=1.0, vmax=1_000_000_000.0),
                linewidths=0.5,
                linecolor="black",
            )

            plt.xticks(rotation=45, ha="right")
            save(
                title, x="Typology", y="Heating System", color=None, custom_legend=False
            )
        return None

    def plotLCACategory(
        self,
        ylim: tuple | None = None,
        #lrm: bool = True,
        colors: str = "standard",
        alpha: float = 1.0,
        method: str = "stackgraph",
    ) -> None:
        """This function plots the lca calculations"""
        emissionInfo = EMISSION_INFO[self.impact.name]

        manage_colors(colors)
        years_ = list(self.data.keys())
        title = f"{self.scenario} - lca - development by category - {emissionInfo.description}"
        data = {}

        for category in self.data[years_[0]]:
            data[category] = [
                adapt_detail(self.data[year][category], Detail.GROUPED)
                for year in years_
            ]

        setup(box=[True, False, False, False])
        plt.annotate(
            emissionInfo.tag,
            xy=(0.5, -0.1),
            xycoords="axes fraction",
            ha="center",
            fontsize=8,
        )
        graph(
            data,
            method=method,
            x=years_,
            colors=COLORS[colors],
            lrm=False,
            title=title,
            ylim=ylim,
            alpha=alpha,
        )
        csv(title=title, data=data, header=years_)
        save(
            title=title,
            x=YEARS,
            y=emissionInfo.unit,
            color=COLORS[colors],
            method=method,
            custom_legend=False,
        )
        return None

    def plotLCAProducts(self, colors: str = 'standard', alpha = 1) -> None:
        """This function plots lca impact per product."""
        emissionInfo = EMISSION_INFO[self.impact.name]
        data = {}
        keys_ = []
        labels = []
        for yearlyData in self.data.values():
            for impactCat, impactData in yearlyData.items():
                if impactCat not in data:
                    data[impactCat] = {}
                
                data[impactCat] = dict_merge(data[impactCat], sum_last_level(impactData))

        title = f"{self.scenario} LCA per Product"

        export_csv_from_dict(data, None, title=title_for_export(title), location="output/csv", mode=1)

        groupedData = {}


        for cat, catData in data.items():
            for product, amount in catData.items():
                if len(product) != 6 or product[2] != '_': continue
                if product[:2] not in groupedData:
                    groupedData[product[:2]] = {}
                if cat not in groupedData[product[:2]]:
                    groupedData[product[:2]][cat] = 0

                if product[:2] not in keys_:
                    keys_.append(product[:2])

                if cat not in labels:
                    labels.append(cat)
        
                groupedData[product[:2]][cat] += amount

        setup(box=[False, True, False, False])        
        plt.annotate(
            emissionInfo.tag,
            xy=(0.5, -0.1),
            xycoords="axes fraction",
            ha="center",
            fontsize=8,
        )
        bottom = [0 for _ in groupedData[list(groupedData.keys())[0]]]
        for key in keys_:
            values_A = [groupedData[key][l] if key in groupedData and l in groupedData[key] else 0 for l in labels]


            plt.barh(
                labels, values_A, left=bottom, label=key, color=COLORS[colors][key], alpha=alpha
            )

            bottom = [b + a for b, a in zip(bottom, values_A)]

        save(title, x=emissionInfo.unit, y="Emission category", color=COLORS[colors], custom_legend=False)



    def plotCompYearlyLCA(self, selection: list | None = None, smoothing: list | None = None, sigma: int = 1) -> None:
        emissionInfo = EMISSION_INFO[self.impact.name]
        data = {}
        years = None
        title = f"All Scenarios - compare - lca{' only ' if selection else ''}{selection if selection else ''}{' smoothed' if smoothing else ''} ({emissionInfo.description})"
        title = title.replace("['", "").replace("']", "").replace("','", ", ")
        for scenario, data_ in self.data.items():
            if not years:
                years = list(data_["lca"].keys())
            if not selection:
                data[scenario] = [
                    adapt_detail(data_["lca"][year], Detail.GROUPED) for year in years
                ]
            else:
                data[scenario] = [
                    #sum(
                    {   key:
                        adapt_detail(value, Detail.GROUPED)
                        for key, value in adapt_detail(
                            data_["lca"][year], Detail.COMPONENT
                        ).items()
                        if key in selection
                    }
                    #)
                    for year in years
                ]

        if smoothing:
            for smooth in smoothing:
                for s in data:
                    smooth_category(data[s], smooth, sigma)

        for s in data:
            data[s] = [sum(d.values()) if isinstance(d, dict) else d for d in data[s]]


        colors = color_range("#000000", "#ffaaaa", len(data.items()))

        setup(box=[True, False, False, False])
        plt.annotate(
            emissionInfo.tag,
            xy=(0.5, -0.1),
            xycoords="axes fraction",
            ha="center",
            fontsize=8,
        )
        for nr, (scenario, amount) in enumerate(data.items()):
            plt.plot(years, amount, label=scenario, color=colors[nr])
        plt.ylim(bottom=0)
        csv(title=title, data=data, header=years)
        save(title=title, x=YEARS, y=emissionInfo.unit, color=None, custom_legend=False)

        return None

    def plotCompLCAStages(self, colors="standard") -> None:
        emissionInfo = EMISSION_INFO[self.impact.name]
        data = {}
        scenario_ = list(self.data.keys())[0]
        manage_colors(colors)

        for lcaCat in self.data[scenario_]["lca"][2023]:
            data[lcaCat] = {}
            for scenario in self.data:
                data[lcaCat][scenario] = sum(
                    adapt_detail(
                        self.data[scenario]["lca"][year][lcaCat], Detail.GROUPED
                    )
                    for year in self.data[scenario]["lca"]
                )

        setup(box=[False, True, False, False])

        bottom = [0 for _ in data[list(data.keys())[0]]]
        for key, data_ in data.items():
            labels = list(data[key].keys())
            values_A = list(data[key].values())
            plt.barh(
                labels, values_A, left=bottom, label=key, color=COLORS["standard"][key]
            )

            bottom = [b + a for b, a in zip(bottom, values_A)]  #
        title = f"All Scenarios - LCA Categories"
        plt.title(title)
        plt.xlabel(emissionInfo.unit)
        plt.ylabel("Scenarios")
        plt.annotate(
            emissionInfo.tag,
            xy=(0.5, -0.1),
            xycoords="axes fraction",
            ha="center",
            fontsize=8,
        )

        
        #csv(title=title, data=data, header=years)
        save(title=title, x=YEARS, y=emissionInfo.unit, color=None, custom_legend=False)

        return None

    def plotSankey(
        self,
        year: int | str = "all",
        country: str = "AT",
        selection: list[str] | None = None,
        gray: tuple[bool, bool] = (True, False),
        colors: str = "standard",
        alpha: float = 0.3,
    ):
        manage_colors(colors)
        impactSelection: list[str] = (
            ["A1-A3", "A4", "A5", "B4", "B5", "C1", "C2", "C3-C4"]
            if not selection
            else selection
        )

        translation = {
            "SFH": "Single-family house",
            "TEH": "Terraced house",
            "MFH": "Multi-family house",
            "ABL": "Apartment block",
            "OFF": "Office",
            "TRA": "Trade",
            "OTH": "Other non-residential",
            "HOR": "Hotel and restaurant",
            "HEA": "Health",
            "EDU": "Education",
            "MI": "Mineral construction materials",
            "KU": "Synthetic materials",
            "HO": "Wood and derived timber products",
            "ME": "Metals",
            "EL": "Electrical installation",
            "NA": "Building materials from renewable resources",
            "SA": "Sanitary installation",
            "OP": "Openings (doors, windows)",
            "HV": "Other products for heating systems",
        }

        ImpactBuilding = {}
        BuildingComponent = {}
        ComponentProduct = {}

        for impactCat, impactCatData in (
            self.data[year].items()
            if year != "all"
            else cummulate(self.data, 1).items()
        ):
            if impactCat not in impactSelection:
                continue
            if impactCat not in ImpactBuilding:
                ImpactBuilding[impactCat] = {}
            for typology, typoData in impactCatData[country].items():
                #_typology = typology[3:6]
                DETAILED = True
                MAP = ['Masonry', 'Concrete', 'Wood']
                if DETAILED:
                    _typology = typology[3:6] + (f'-new-{MAP[int(typology[17])-1]}' if typology[7:11] in ['2010', '2011'] else '-old')
                if _typology not in ImpactBuilding[impactCat]:
                    ImpactBuilding[impactCat][_typology] = 0
                if _typology not in BuildingComponent:
                    BuildingComponent[_typology] = {}
                for component, compData in typoData.items():
                    if component not in BuildingComponent[_typology]:
                        BuildingComponent[_typology][component] = 0
                    if component not in ComponentProduct:
                        ComponentProduct[component] = {}
                    if type(compData) is float:
                        ImpactBuilding[impactCat][_typology] += compData
                        BuildingComponent[_typology][component] += compData
                        continue
                    for product, quantity in compData.items():
                        _product = product[:2]
                        if _product not in ComponentProduct[component]:
                            ComponentProduct[component][_product] = 0
                        ImpactBuilding[impactCat][_typology] += quantity
                        BuildingComponent[_typology][component] += quantity
                        ComponentProduct[component][_product] += quantity

        connections = []
        d = {}
        p = {}

        for impact, impactData in ImpactBuilding.items():
            if impact not in d:
                d[impact] = 0
            for building, amount in impactData.items():
                if amount < 0:
                    continue
                connections.append(
                    [
                        impact,
                        building,
                        amount,
                        (
                            (
                                hex_to_rgba(COLORS[colors][impact], alpha=alpha)
                                if impact in COLORS[colors]
                                else "rgba(153, 85, 153, 0.5)"
                            )
                            if not gray[1]
                            else hex_to_rgba("#aaaaaa", 0.5)
                        ),
                    ]
                )
                d[impact] += amount

        for building, buildingData in BuildingComponent.items():
            if building not in d:
                d[building] = 0
            for component, amount in buildingData.items():
                if amount < 0:
                    continue
                connections.append(
                    [
                        building,
                        component,
                        amount,
                        (
                            (
                                hex_to_rgba(COLORS[colors][building], alpha=alpha)
                                if building in COLORS[colors]
                                else "rgba(153, 85, 153, 0.5)"
                            )
                            if not gray[1]
                            else hex_to_rgba("#aaaaaa", 0.5)
                        ),
                    ]
                )
                d[building] += amount

        for component, compData in ComponentProduct.items():
            if component not in d:
                d[component] = 0
            for product, amount in compData.items():
                if product not in p:
                    p[product] = 0
                if amount < 0:
                    continue
                connections.append(
                    [
                        component,
                        product,
                        amount,
                        (
                            (
                                hex_to_rgba(COLORS[colors][component], alpha=alpha)
                                if component in COLORS[colors]
                                else "rgba(153, 85, 153, 0.5)"
                            )
                            if not gray[1]
                            else hex_to_rgba("#aaaaaa", 0.5)
                        ),
                    ]
                )
                p[product] += amount

        for building, buildingData in BuildingComponent.items():
            if building not in d:
                d[building] = 0
            for component, amount in buildingData.items():
                if component not in d:
                    d[component] = 0
                d[component] += amount

        d = dict_merge(d, p)

        d_map = {}
        for pos, d_ in enumerate(d.keys()):
            d_map[d_] = pos

        labels = [
            f"{translation[d_] if d_ in translation else d_} ({locale.format_string('%.0f', amount/1_000_000, grouping=True)})"
            for d_, amount in d.items()
        ]

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=25,
                        line=(
                            {"color": "black", "width": 0.5}
                            if gray[0]
                            else {"color": "white", "width": 0.5}
                        ),
                        label=labels,
                        color=[
                            (
                                (COLORS[colors][d_] if d_ in COLORS[colors] else "#ccc")
                                if not gray[0]
                                else "#aaaaaa"
                            )
                            for d_ in d
                        ],
                        # groups = [[2,3,5,6]]
                    ),
                    link=dict(
                        source=[d_map[c[0]] for c in connections],
                        target=[d_map[c[1]] for c in connections],
                        value=[c[2] for c in connections],
                        color=[c[3] for c in connections],
                    ),
                )
            ]
        )

        width = 10.5 * 300
        height = 7.4 * 300
        font = 30

        fig.update_layout(
            title_text=f"Flows of Emissions - {self.scenario} (MtCO2eq)",
            font_size=font,
            autosize=False,
            width=width,  # Set the width here
            height=height,  # Set the height here
        )

        # Export the figure as a PDF with the specified size
        fig.write_image(f"output/graphs/{self.scenario.lower()}-sankey-diagram.pdf", format='pdf', width=width, height=height)


def filterSubcategory(data: dict, key: str | list) -> dict:
    """TBA"""
    if isinstance(key, str):
        return {year: d[key] for year, d in data.items()}
    if isinstance(key, list):
        return_ = {}
        for key_ in key:
            for year_, data_ in data.items():
                if year_ not in return_:
                    return_[year_] = {}
                for typo in data_[key_]['AT']:
                    for comp in data_[key_]['AT'][typo]:
                        for product_, amount_ in data_[key_]['AT'][typo][comp].dictify().items():
                            if product_ not in return_[year_]:
                                return_[year_][product_] = 0
                            return_[year_][product_] += amount_
        return return_


def setup(grid: float = 0.25, box: list = [True, True, True, True]) -> None:
    """This function sets up a plot."""
    plt.figure(figsize=(10.5, 7.4))
    for nr, pos in enumerate(["bottom", "left", "top", "right"]):
        plt.gca().spines[pos].set_visible(box[nr])
    if grid:
        plt.grid(color="#000000", linewidth=grid)


def save(
    title: str,
    x: str,
    y: str,
    color: dict,
    method: str = "bargraph",
    custom_legend: bool = True,
) -> None:
    "This function saves a plot."
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)

    if custom_legend:
        _, labels = plt.gca().get_legend_handles_labels()
        unique_labels = list(set(labels))

        if method == "bargraph":
            proxy_artists = [
                Patch(color=color_)
                for color_ in [
                    color__ for key, color__ in color.items() if key in unique_labels
                ]
            ]
        elif method == "stackgraph":
            proxy_artists = [
                Patch(color=color_)
                for color_ in [
                    color__ for key, color__ in color.items() if key in unique_labels
                ]
            ]
        elif method == "linegraph":
            proxy_artists = [
                Line2D([0], [0], linestyle="-", color=color_)
                for color_ in [
                    color__ for key, color__ in color.items() if key in unique_labels
                ]
            ]
        else:
            raise TypeError()

        plt.legend(
            proxy_artists,
            [key for key in color if key in unique_labels],
            loc="upper right",
            handlelength=1,
            handleheight=1,
            fontsize="small",
        )
    else:
        plt.legend(loc="upper right", fontsize="small")

    plt.savefig(
        f"output/graphs/{title_for_export(title)}",
        dpi=300,
    )
    plt.close()


def csv(title: str, data: dict, header: list):
    """This function saves a csv."""
    export_csv_from_dict(
        data, header, title=title_for_export(title), location="output/csv"
    )


def bargraph(
    data: dict, *, x: list, colors: dict, bottom: bool = True, lrm=False, **kwargs
) -> None:
    """This function graphs bargraphs."""
    if kwargs or lrm:
        pass
    bottom_ = [0 for _ in x]
    for key, y_ in data.items():
        plt.bar(
            x,
            y_,
            bottom=bottom_,
            label=key,
            color=colors[key] if key in colors else "#555",
        )
        if bottom:
            bottom_ = [b_ + y__ for b_, y__ in zip(bottom_, y_)]


def linegraph(data: dict, *, x: list, colors: dict, **kwargs) -> None:
    """This function graphs linegraphs."""
    if kwargs:
        pass
    for key, y_ in data.items():
        plt.plot(x, y_, label=key, color=colors[key])


def stackgraph(
    data: dict, *, x: list, colors: dict, ylim: tuple | None = None, alpha=1, **kwargs
) -> None:
    """This function graphs a stackgraph"""
    if kwargs:
        pass
    for k in data.keys():
        if k not in colors:
            logging.warning("There is no color for %s", k)

    plt.stackplot(
        x,
        list(data.values()),
        labels=list(data.keys()),
        colors=[colors[k] if k in colors else "#555" for k in data.keys()],
        alpha=alpha,
    )
    if ylim:
        plt.ylim(ylim)


def graph(*args, method: str, **kwargs) -> None:
    """This function graphs a graph."""
    logging.debug(
        "Graphing a %s%s",
        method,
        " titled '" + kwargs["title"] + "'" if "title" in kwargs else "",
    )
    try:
        if method == "bargraph":
            return bargraph(*args, **kwargs)
        if method == "linegraph":
            return linegraph(*args, **kwargs)
        if method == "stackgraph":
            return stackgraph(*args, **kwargs)
        raise NameError(f"{method} is not a valid option for graphing")
    except NameError as err:
        logging.error(err)
        return None
    except TypeError as err:
        logging.error(err)
        return None
    except IndexError as err:
        logging.error(
            "%s Maybe there is something wrong with the settings or smth.",
            err
        )
        return None


def manage_colors(colors: str) -> None:
    """This function manages colors."""
    global COLORS
    if colors not in COLORS:
        COLORS[colors] = import_json(title=colors, location="data/colors")

def sum_last_level(d):
    result = {}

    def recurse(current_dict):
        for key, value in current_dict.items():
            if isinstance(value, dict):
                recurse(value)
            else:
                if key in result:
                    result[key] += value
                else:
                    result[key] = value

    recurse(d)
    return result


def smooth_category(d, cat, sigma) -> None:
    if isinstance(d, dict):
        col = np.array([d_[cat] for d_ in d.values()])
    elif isinstance(d, list):
        col = np.array([d_[cat] for d_ in d])
    else:
        raise TypeError

    new_col = gaussian_filter1d(col, sigma)

    for nr, _ in enumerate(d):
        d[nr][cat] = new_col[nr]

def de_list(d: dict[str, list | int | float], stock: dict, sm: bool = False) -> list:
    if isinstance(next(iter(d.values())), list):
        result_length = len(next(iter(d.values())))
        result = [0] * result_length

        # Sum the corresponding elements from each list
        for bld, lst in d.items():
            for i in range(result_length):
                result[i] += lst[i] * (1 if not sm else stock[bld].floor_area['Gross'])
                #print((1 if not sm else stock[bld].floor_area['Gross']))
            
        
        return result
    if isinstance(next(iter(d.values())), (int, float)):
        result = [0] 
        for bld, data in d.items():
            assert isinstance(data, (int, float))
            result[0] += data * (1 if not sm else stock[bld].floor_area['Gross'])
        return result
