# PULSE-AT - Version 1.0

## Concept
This model allows for the “Prospective Upscaling of Life cycle Scenarios and Environmental impacts of Austrian buildings” (PULSE-AT). In other words, it aims at calculating the enviromental impacts of the building stock of a country (in this case Austria) based on different parameters and scenarios. Information on future material stocks and flows, energy and water consumption, is also calculated by the model. It combines dynamic material flow analysis (MFA) and life cycle assessment (LCA) methods.

This first version of PULSE-AT was fully described in the following publication:

Alaux, N., Schwark, B., Hörmann, M., Ruschi Mendes Saade, M., Passer, A. (2024). Assessing the prospective environmental impacts and circularity potentials of building stocks: An open-source model from Austria (PULSE-AT). _Journal of Industrial Ecology_, 1–14. https://doi.org/10.1111/jiec.13558

Please cite this article when further using the model, its input files or its results (see license for more information).

## How to use:
### Technical requirements
python 3.12\
pandas 2.1.4\
matplotlib 3.8.2\
numpy 1.26.3\
scipy 1.11.4\
seaborn 0.13.2\
plotly 5.18.0\
pytest 8.1.1 (For testing purposes only. Otherwise not needed)

### Input files:
The input files provided in the supplementary information files of the article ("Building_list", "Components_list", "Products_list" and "Scenarios_list") should be put as csv files in the input folder in order for the model to run.

### Output:
The output specifies the wanted output and the necessary calculations.The options are: _numbers_, _products_, _energy_ and _lca_ <br />
Each of these options provide a collection of subgraphs with a selection of options.<br />
- **numbers:** models the progression of the number of buildings
    - **total:** models the progression of the total number of buildings.
    - **existent:** models the progression of the of buildings built before and after the starting point.
- **products:** models the development of products in the building stock.
    - **total:** models the entire amount of products in the building stock in tons.
    - **category:** models the selected flow of products by year, split by category.
- **energy:** models the progression of the energy demand of the building stock.
    - **category:** models the different energy categories.
    - **hss:** models the development of the heating systems.
- **lca:** models the progression of the lca development.
    - **category:** models the different lca categories.
    - **sankey:** models the lca flows as a sankey diagram.
- **compare:** models a comparison between different scenarios.
    - **lca:** models a graph of different scenarios lca development.

If you do not own a license for the ecoinvent database, you can use this model to estimate future numbers of buildings, material stocks and flows, as well as energy consumption. This does not require programming experience. You can also modify the csv input files to represent the situation of another country (see publication for more details).

If you own a license for the ecoinvent database, you can additionally generate the LCA graphs. For that, please make sure that you have linked every material of the product file to an LCA data (brightway key). Then, generate the prospective LCA databases that you need with premise. Finally, run the lca_database.py file. This might require additional programming skills.

## Credits and contact: 

**Nicolas Alaux**: Conceptualization, Methodology, Investigation, Software, Writing - Original Draft. 

**Benedict Schwark**: Conceptualization, Data curation, Software, Writing - Review & Editing. 

**Marius Hörmann**: Investigation, Data curation, Writing - Review & Editing. 

**Marcella Ruschi Mendes Saade**: Methodology, Validation, Writing - Review & Editing, Supervision. 

**Alexander Passer**: Methodology, Validation, Resources, Writing - Review & Editing, Supervision. <a href="mailto:alexander.passer@tugraz.at">alexander.passer@tugraz.at</a><br />
