"""
main.py
-------
Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

This is the main interface for the pulse building stock calculations 
"""

import pulse

# ------------------------------------------------------------------------------------------------ #
# The exact calculations that are being done are defined here in the SETTINGS dictionary. The      #
# dictionary defines what gets calculated, based on what the required outputs are. The             #
# Scenarios_list.csv then influences how these things get calculated.                              #
# ------------------------------------------------------------------------------------------------ #
SETTINGS: dict[str, dict[str, list[dict]] | pulse.Impact | bool | str] = {
    # ----------------------------------------------------------------------------------------------
    # output
    # 
    # The output parameter of the SETTINGS dictionary defines which outputs
    # are being made. There are five parent categories of output types.
    # numbers, products, energy, lca, compare.
    # This is done to make the calculations quicker. If you are only interested
    # in numbers there is no need for product calculations.
    # The actual plots that will be plotted get selected as a list of dictionaries, where each
    # dictionary needs the specifier kind with one of the available options. Additional settings can
    # then be put into the dictionary and will be parsed to the grapher later on.
    # ----------------------------------------------------------------------------------------------
    'output': dict(
        # ------------------------------------------------------------------------------------------
        # numbers
        #
        # This part of the calculations deals exclusively with the number of buildings of different
        # typologies.
        #
        # Options:
        #   total:      Outputs the total numbers of the selected group.
        #      -args:   selection: str (default: construction)
        #                   Can either be total, construction, demolition, refurbishment or heating
        #                   system. This selects which aspect is put out.
        #               colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               method: str (default: 'bargraph')
        #                   The method used in graphing (options: linegraph, bargraph, stackgraph).
        #                   Note: the combination refurbishment and bargraph or stackgraph is not
        #                   permitted.
        #
        #   subgroup:   Outputs the selected group by a defined subgroup. These subgroups can be
        #               combined.
        #      -args:   use: bool (default: false)
        #                   If this variable is set the use of the buildings get shown.
        #               typology: bool (default: false)
        #                   If this variable is set the typology group (SFH...) of the buildings
        #                   get shown.
        #               years: bool (default: false)
        #                   If this variable is set the year ranges of the buildings get shown.
        #               construction: bool (default: false)
        #                   If this variable is set the construction type of the buildings get shown.
        #               energy: bool (default: false)
        #                   If this variable is set the energy type of the buildings get shown.
        #               selection: str (default: 'total')
        #                   Can either be total, construction, demolition or heating system. This 
        #                   selects which aspect is put out.
        #               colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               method: str (default: 'bargraph')
        #                   The method used in graphing (options: linegraph, bargraph, stackgraph).
        #
        # ------------------------------------------------------------------------------------------
        numbers = [
            dict(kind='total', selection='total', method='stackgraph', sm=True),
            dict(kind='total', selection='construction', method='stackgraph', sm=True),
            dict(kind='total', selection='demolition', method='stackgraph', sm=True),
            dict(kind='total', selection='refurbishment', sm=True),
            dict(kind='total', selection='heating system', method='stackgraph', sm=True),
            dict(kind='total', selection='total', method='stackgraph', sm=False),
            dict(kind='total', selection='construction', method='stackgraph', sm=False),
            dict(kind='total', selection='demolition', method='stackgraph', sm=False),
            dict(kind='total', selection='refurbishment', sm=False),
            dict(kind='total', selection='heating system', method='stackgraph', sm=False),
            dict(kind='subgroup', use=True, sm=False),
            dict(kind='subgroup', typology=True, selection='refurbishment', sm=True),
            dict(kind='subgroup', typology=True, construction=True, selection='construction', sm=True),
            dict(kind='subgroup', typology=True, construction=True, selection='construction', sm=False),
            dict(kind='subgroup', typology=True, sm=False),
            dict(kind='subgroup', years=True, sm=True),
            dict(kind='subgroup', years=True, selection='heating system'),
            dict(kind='subgroup', construction=True),
            dict(kind='subgroup', energy=True),
            dict(kind='subgroup', construction=True, energy=True)
        ],
        # ------------------------------------------------------------------------------------------
        # products
        #
        # This part of the calculation deals with the various different material (in this model 
        # described as products) flows.
        #
        # Options:
        #   total:      Outputs the total mass of products or product flows in a category.
        #      -args:   selection: str (default: total)
        #                   Selects which grouping gets put out. Either total, construction or
        #                   demolition
        #               colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               method: str (default: 'bargraph')
        #                   The method used in graphing (options: linegraph, bargraph, stackgraph).
        #
        #  category:    Outputs the different product categories per year.
        #      -args:   positive: str | list[str] (default: total)
        #                   This is the selection of one or more aspects that will be plotted on the
        #                   positive y axis. Options are: total, construction, demolition,
        #                   refurbishment in, refurbishment out and replacement
        #               negative: str | list[str] | None (default: None)
        #                   This is the selection of zero, one or more aspects that will be plotted
        #                   on the negative y axis. Same options as positive.
        #               detail: int (0-2) (default: 2)
        #                   This value describes if the product codes can be more detailed
        #                   0: Only the first two letters of the product code will be used
        #                       HO_101 -> HO
        #                   1: The first digit (subgroup) will be shown, if that subgroup makes up
        #                   at least 10% of the entire mass.
        #                       HO_101 -> HO_1
        #                   2: The entire code will be shown, if that specific product makes up at
        #                   least 10% of the entire mass.
        #                       HO_101 -> HO_101
        #               colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               method: str (default: 'bargraph')
        #                   The method used in graphing (options: linegraph, bargraph, stackgraph).
        #
        # ------------------------------------------------------------------------------------------
        products = [
            dict(kind='total'),
            dict(kind='total', selection='construction'),
            dict(kind='total', selection='demolition'),
            dict(kind='category', positive='total'),
            dict(kind='category'),
            dict(kind='category', positive='construction', negative='demolition'),
            dict(
                kind='category',
                positive=['construction', 'refurbishment in', 'replacement'],
                negative=['demolition', 'refurbishment out', 'replacement']
            ),
            dict(kind='category', positive='refurbishment in', negative='refurbishment out'),
            dict(kind='category', positive='replacement', negative='replacement')
        ],
        # ------------------------------------------------------------------------------------------
        # energy
        #
        #
        #
        # Options:
        #   category:   Plots the heating demand per category per year.
        #      -args:   hss: bool (default: False)
        #                   If activated, the heating category will be split into its heating
        #                   systems.
        #               colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               method: str (default: 'bargraph')
        #                   The method used in graphing (options: linegraph, bargraph, stackgraph).
        #
        #   hss:        Plots only the heating systems per year.
        #      -args:   colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               method: str (default: 'bargraph')
        #                   The method used in graphing (options: linegraph, bargraph, stackgraph).
        #
        #   heatmap:    Plots a heatmap that shows the heating demand per typology per heating
        #               system for a selection of years.
        #      -args:   years: list[int] (default = [2023, 2050])
        #                   The choosen years (each one will get a heatmap).
        #               cmap: std (default = 'plasma')
        #                   The colormap used in the heatmap. For more see:
        #                   https://seaborn.pydata.org/tutorial/color_palettes.html
        #   top:        Plots the most contributing typologies to the enrgy demand.
        #      -args:   number: int | str (default = 10)
        #                   The top how many are shown. If it is 'max' all typologies will be shown.
        #               selection: str | list[str] (standard: 'heating')
        #                   Selects the selection that is shown. Options are heating, cooling, 
        #                   water
        #               color: str (range, random) (standard: random)
        #                   Selects the method that colors are choosen. Either in a range or random.
        #
        # ------------------------------------------------------------------------------------------
        energy = [
            dict(kind='category'),
            dict(kind='category', hss=True),
            dict(kind='hss'),
            dict(kind='heatmap'),
            dict(kind='top', number='max', color='random'),
            dict(kind='top', number='max', color='range'),
            dict(kind='top', number=20, color='random'),
            dict(kind='top', number=20, color='range'),
            dict(kind='top', number=20, color='random'),
            dict(kind='top', number=20, color='random', selection=['heating', 'cooling'])
        ],
        # ------------------------------------------------------------------------------------------
        # lca
        #
        # This part of the calculation computes the life cycle assessment results by multiplying the
        # previously done calculations with the in the scenario specified impact categories.
        #
        # Options:
        #   category:   This output shows the yearly lca results per impact category.
        #     -args:    ylim: tuple | None (default: None)
        #                   The limit on the y-axis. Should be a tuple of size two (lower limit and
        #                   upper limit) or None. If it is None the automatic limits will be used.
        #               colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               alpha: float (default: 1.0)
        #                   The alpha value of the colors.
        #               method: str (default: 'bargraph')
        #                   The method used in graphing (options: linegraph, bargraph, stackgraph)
        #
        #   products:   This output shows the cummulated lca impacts per product category.
        #     -args:    colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               alpha: float (default: 1.0)
        #                   The alpha value of the colors.
        #
        #   sankey:     This output creates a sankey diagramm using plotly.
        #     -args:    year: int | str (default: 'all')
        #                   Selection of The years that should be shown in the sankey diagramm.
        #                   If all the sankey will show the cummulative numbers over all years.
        #               selection: list[str] | None (default: None)
        #                   The selection of impact categories that will be shown. If it is None all
        #                   impact categories will be shown.
        #               gray: tuple[bool, bool] (default: (True, False)),
        #                   If the first value in the tuple is set to True the Nodes will be gray.
        #                   If the second value in the tuple is set to True the Connections will be
        #                   gray.
        #               colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #               alpha: float (default: 0.3)
        #                   The alpha value of the connections.
        #
        # ------------------------------------------------------------------------------------------
        lca = [
            #dict(kind='category', method='stackgraph'),
            #dict(kind='products'),
            #dict(kind='sankey'),
            #dict(kind='sankey', year=2023, selection=['A1-A3', 'A4', 'A5'])
        ],
        # ------------------------------------------------------------------------------------------
        # compared
        #
        # This output option does not compute any additional calculations. It just compares the
        # previously done calculations between the different scenarios.
        #
        # Options:
        #
        #   lca:        This output compares the yearly cummulative lca results of the different
        #               scenarios.
        #     -args:    selection: list | None (default: None)
        #                   A selection of lca stages that will be included in the output.
        #                   If None all categories will be used.
        #               smoothing: list | None (default: None)
        #                   A list of lca stages that will be smoothed out using a gauss function.
        #                   If None, none of the categories will be smoothed out.
        #               sigma: int (default: 1)
        #                   The sigma used in the smoothing. (Using scipy.ndimage.gaussian_filter1d)
        #
        #   lca stages: This graph compares the cummulated lca stages per scenario.
        #     -args:    colors: str (default: 'standard')
        #                   Selection of the color scheme.
        #
        # ------------------------------------------------------------------------------------------
        compare = [
            #dict(kind='lca'),
            #dict(kind='lca', selection=['B4', 'B5'], smoothing=['B4'], sigma=2),
            #dict(kind='lca', selection=['B5']),
            #dict(kind='lca', selection=['B4'], smoothing=['B4'], sigma=2),
            #dict(kind='lca stages')
        ]
    ),
    # ----------------------------------------------------------------------------------------------
    # indicator
    #
    # This parameter defines which lca indicator is used for the lca calculation.
    # ----------------------------------------------------------------------------------------------
    'indicator': pulse.Impact.GWP100_FOSSIL,
    # ----------------------------------------------------------------------------------------------
    # reload
    #
    # This parameter can be set to true if you want to recompute all pre calculations (construction
    # and deconstruction statistics). If it is set to false (Which is the default if it isnt
    # specified) they will only be calculated if the files dont exist.
    # ----------------------------------------------------------------------------------------------
    'reload' : False,
    # ----------------------------------------------------------------------------------------------
    # clear_output
    #
    # This parameter can be set to true if you want to remove all old outputs.
    # ----------------------------------------------------------------------------------------------
    'clear_output' : True,
    # ----------------------------------------------------------------------------------------------
    # version
    #
    # This parameter can be set to true if you want to remove all old outputs.
    # ----------------------------------------------------------------------------------------------
    'version' : 'AT - 1.0'
}
buildingStockCalculation = pulse.BuildingStockCalculations(
    pulse.fileLocations,
    **SETTINGS
)
buildingStockCalculation.run(multi_threaded_=False)
