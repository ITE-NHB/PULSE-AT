"""
pulse.py
--------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description:
    This file defines the wrapper object, that includes the intire building stock,
    as well as a few helper functions to deal with the interface.

"""

#---------------------------------------------------------------------------------------------------
# Imports Global Libraries
#---------------------------------------------------------------------------------------------------
import copy
import logging
import os
import threading
import time
import sys
import glob

#---------------------------------------------------------------------------------------------------
# Imports Local Libraries
#---------------------------------------------------------------------------------------------------
from .support import calculation, calc_historic_construction, calc_future_demolition, import_data

from .support import Graph, Impact, Loading, Logo, Detail

from .support import PROGRESS_BAR, GRAPH_OPTIONS

#---------------------------------------------------------------------------------------------------
# Variables
#---------------------------------------------------------------------------------------------------

fileLocations = {
    "Products" : "Products_list.csv",
    "Components" : "Components_list.csv",
    "Buildings" : "Buildings_list.csv",
    "Scenarios" : "Scenarios_list.csv"
}

DEBUG_MSG = "Debug Information is deactivated. To activate it, write 'debug' in the cmd line args"

#---------------------------------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------------------------------
def init_logging(debug: bool = False) -> None:
    """This function initiates the debugger."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - [Thread ID: %(thread)d] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='output/buildingStockModel.log',
        filemode='w'
    )

    ignored = ["matplotlib"]
    for i in ignored:
        logging.getLogger(i).setLevel(logging.WARNING)
    logging.info("New Calculation started")
    if not debug:
        logging.info(DEBUG_MSG)
    
    # Add new Logging levels
    THREAD_LEVEL = 25
    logging.addLevelName(THREAD_LEVEL, 'THREAD')

    def thread(self, message, *args, **kwards):
        if self.isEnabledFor(THREAD_LEVEL):
            # Yes, logger takes its '*args' as 'args'.
            self._log(THREAD_LEVEL, message, args, **kwards) 

    logging.Logger.thread = thread # type: ignore

def init_statistics(reload: bool = False) -> None:
    """This function initiates the statistics."""
    reload_message = ' because they were not available' if not reload else ''
    if(reload or not os.path.isfile("statistics/constructionStatistic.json")):
        calc_historic_construction()
        logging.info("Reloaded the historic construction statistics%s.", reload_message)
    if(reload or not os.path.isfile("statistics/weibull.json")):
        calc_future_demolition()
        logging.info("Reloaded the future deconstruction statistics %s.", reload_message)

def init_logo(version: str = "UNDEFINED") -> None:
    """This function initiates the logo."""
    Logo.home()
    terminal_width, _ = os.get_terminal_size()
    print(f"Version: {version}".center(terminal_width))
    print()

def create_folder(folder, subfolders):
    """This function creates folders from a dictionary"""
    if folder:
        if not os.path.exists(folder):
            os.makedirs(folder)

    if subfolders:
        for subfolder, subsubfolders in subfolders.items():
            if folder:
                create_folder(f"{folder}/{subfolder}", subsubfolders)
            else:
                create_folder(subfolder, subsubfolders)

def create_directory() -> None:
    """This function creates the folder structure necessary for the outputs."""
    STRUCTURE = {
        'output' : {
            'csv' : None, 
            'graphs' : None
        }
    }

    create_folder(None, STRUCTURE)

def remove_old_files(remove: bool = False) -> None:
    """This function clears the output folder."""

    if not remove:
        return

    csv_path = 'output/csv'
    graphs_path = 'output/graphs'

    csv_files = glob.glob(os.path.join(csv_path, '*'))
    graphs_files = glob.glob(os.path.join(graphs_path, '*'))

    logging.info("Removed %d csv files.", len(csv_files))
    for csv_file in csv_files:
        if os.path.isfile(csv_file):
            os.remove(csv_file)

    logging.info("Removed %d graphs.", len(graphs_files))
    for graph_file in graphs_files:
        if os.path.isfile(graph_file):
            os.remove(graph_file)

def wait_icon() -> None:
    """This function takes care of the waiting icon."""
    t = 0
    while PROGRESS_BAR and any(PROGRESS_BAR):
        if not any(d != 2 for d in PROGRESS_BAR):
            break
        a = ""
        for nr, b in enumerate(PROGRESS_BAR):
            a = f"{a} {
                Loading.LOADING.value[(nr + t) % len(Loading.LOADING.value)]
                if b == 1 else Loading.DONE.value
                if b == 2 else Loading.EMPTY.value
            }"
        terminal_width, _ = os.get_terminal_size()
        a = a.strip()
        print(f"\r{a.center(terminal_width)}",end="", flush=True)
        time.sleep(0.5)
        t = t + 1 if t != 3 else 0
    if isinstance(PROGRESS_BAR, list):
        for x in Loading.LOADING.value:
            a = a.replace(x, Loading.DONE.value)
        print(f"\r{a.center(terminal_width)}",end="\n", flush=True)
    if isinstance(PROGRESS_BAR, bool):
        print(f"\033[{1}A", end='')
        for x in Loading.LOADING.value:
            a = a.replace(x, Loading.FAILED.value)
        print(f"\r{a.center(terminal_width)}",end="\n", flush=True)

#---------------------------------------------------------------------------------------------------
# Classes
#---------------------------------------------------------------------------------------------------
class BuildingStockSettings:
    """This Class is used for storing the building stock settings"""
    def __init__(
            self,
            indicator,
            detail,
            output
        ):
        """This function initiates the BuildingStockSettings"""
        self.indicator = indicator
        self.detail = detail
        self.output = output
    def __repr__(self) -> str:
        return "BuildingStockSettings"
    def __bool__(self) -> bool:
        return True

class BuildingStockData:
    """This Class is used for storing the building stock data"""
    def __init__(
            self,
            products,
            components,
            buildings,
            scenarios
        ):
        """This function initiates the BuildingStockData"""
        self.products = products
        self.components = components
        self.buildings = buildings
        self.scenarios = scenarios
    def __repr__(self) -> str:
        return "BuildingStockData"
    def __bool__(self) -> bool:
        return True

class BuildingStockCalculations:
    """This class groups together different calculations."""
    def __init__(
            self,
            file_locations: dict[str,str],
            /,
            **kwargs
        ) -> None:
        """This function initializes the calculations class."""

        assert "output" in kwargs, "Output not in settings. Calculation stopped."
        create_directory()
        init_logging('debug' in sys.argv)
        init_statistics(kwargs['reload'] if 'reload' in kwargs else False)
        init_logo(kwargs['version'] if 'version' in kwargs else "UNDEFINED")


        remove_old_files(kwargs['clear_output'] if 'clear_output' in kwargs else False)
        
        self.settings =     BuildingStockSettings(
            indicator = kwargs['indicator'] if 'indicator' in kwargs else Impact.GWP100,
            detail =    detail_requirement(kwargs['output']),
            output =    kwargs['output']
        )

        self.data =         BuildingStockData(
            *import_data(
                **file_locations,
                detail=self.settings.detail
            )
        )

        self.results =      {scenario_name:{} for scenario_name in self.data.scenarios}
        self.loading_icon = threading.Thread(target=wait_icon)
        self.threads =      {f'Thread {nr} - {scenario_name}':
                                threading.Thread (
                                target=calculation,
                                args=(
                                    (
                                        copy.deepcopy(self.data.products),
                                        copy.deepcopy(self.data.buildings)
                                    ),
                                    scenario,
                                    self.results[scenario_name],
                                    copy.deepcopy(self.settings.detail),
                                    copy.deepcopy(self.settings.indicator)),
                                name=f'{nr}'
                            ) for nr, (scenario_name, scenario)
                            in enumerate(self.data.scenarios.items())
                            }
        thread_message = 'Threads' if len(self.threads) > 1 else 'Thread'
        logging.getLogger(__name__).thread("%d %s prepared for calculation", len(self.threads), thread_message)

    def run(self, multi_threaded_: bool = True) -> None:
        """This functions runs the different scenarios for the Building Stock Calculation class. \n
        For debugging purposses: \n
        multi_threaded_ (bool): Setting Variable that specifies weather the programm should run on 
                                multiple threads. Defaults to True."""
        global PROGRESS_BAR
        PROGRESS_BAR = [0 for _ in range(len(self.threads) + 2)]
        PROGRESS_BAR[0] = 1

        try:
            self.loading_icon.start()
            PROGRESS_BAR[0] = 2

            if not multi_threaded_:
                thread_message = 'Threads in a row' if len(self.threads) > 1 else 'Thread'
                logging.getLogger(__name__).thread("Starting %d %s",len(self.threads), thread_message)
                for nr,thread in  enumerate(self.threads.values()):
                    PROGRESS_BAR[nr+1] = 1
                    thread.start()
                    logging.getLogger(__name__).thread("Started Thread %d", nr)
                    thread.join()
                    logging.getLogger(__name__).thread("Joined Thread %d", nr)
                    PROGRESS_BAR[nr+1] = 2

            if multi_threaded_:
                thread_message = 'Threads in parallel' if len(self.threads) > 1 else 'Thread'
                logging.getLogger(__name__).thread("Starting %d %s",len(self.threads), thread_message)
                for nr,thread in  enumerate(self.threads.values()):
                    PROGRESS_BAR[nr+1] = 1
                    thread.start()
                    logging.getLogger(__name__).thread("Started Thread %d", nr)
                logging.info("%d THREADS STARTED", nr+1)
                for nr, thread in enumerate(self.threads.values()):
                    thread.join()
                    PROGRESS_BAR[nr+1] = 2
                    logging.getLogger(__name__).thread("Joined Thread %d", nr)
                logging.getLogger(__name__).thread("%d THREADS JOINED", nr+1)

            logging.info("Calculations finished")
            PROGRESS_BAR[-1] = 1
            self.output()
            PROGRESS_BAR[-1] = 2
            self.loading_icon.join()
            Logo.done()
            logging.info("Programm terminated gracefully!")

        except KeyboardInterrupt:
            logging.critical("Got interrupted")
            PROGRESS_BAR = False
            self.loading_icon.join()
            Logo.error()
            sys.exit(-1)

    def output(self) -> None:
        """This function deals with the output of the information, so the graphing and the csv 
        exporting."""
        logging.info("Output started")
        for scenario, data in self.results.items():
            if not data:
                continue
            for type_ in self.settings.output:
                assert type_ in GRAPH_OPTIONS, f"{type_} is not a valid option"
            for nr, type_ in enumerate(['numbers', 'products', 'energy', 'lca']):
                if type_ in self.settings.output and type_ in data:
                    temp_ = Graph(
                        data[type_],
                        kind = nr,
                        buildings=self.data.buildings,
                        scenario=scenario,
                        impact=self.settings.indicator
                    )
                    for setup in self.settings.output[type_]:
                        temp_.plot(**setup)
        if 'compare' in self.settings.output:
            if self.results[list(self.results.keys())[0]]:
                temp_= Graph(
                    self.results,
                    kind = 4,
                    buildings=self.data.buildings,
                    scenario="",
                    impact=self.settings.indicator
                )
                for setup in self.settings.output['compare']:
                    temp_.plot(**setup)
        logging.info("Output finished")

def detail_requirement(settings: dict) -> dict:
    """This function calculates the detail requirement"""

    requirements = {
        "numbers" : Detail.NO_CALC,
        "products" : Detail.NO_CALC,
        "recycling" : Detail.NO_CALC,
        "energy" : Detail.NO_CALC,
        "lca" : Detail.NO_CALC
    }
    
    if settings['compare']:
        logging.debug("Detail requirement: Compare")
        requirements["numbers"] = Detail.TYPOLOGY
        requirements["products"] = Detail.COMPONENT
        requirements["energy"] = Detail.PRODUCT
        requirements["lca"] = Detail.PRODUCT

    elif settings['lca']:
        logging.debug("Detail requirement: LCA")
        requirements["numbers"] = Detail.TYPOLOGY
        requirements["products"] = Detail.COMPONENT
        requirements["energy"] = Detail.PRODUCT
        requirements["lca"] = Detail.PRODUCT

    elif settings['energy']:
        logging.debug("Detail requirement: Energy")
        requirements["numbers"] = Detail.TYPOLOGY
        if settings['products']:
            requirements["products"] = Detail.COMPONENT
        requirements["energy"] = Detail.PRODUCT

    elif settings['products']:
        logging.debug("Detail requirement: Products")
        requirements["numbers"] = Detail.TYPOLOGY
        requirements["products"] = Detail.COMPONENT

    elif settings['numbers']:
        logging.debug("Detail requirement: Numbers")
        requirements["numbers"] = Detail.TYPOLOGY
    
    return requirements
