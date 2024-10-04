"""
ascii.py
--------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description:  This file is where everything related to different ascii codes is strored. In case 
                you want to change something about logos or loading screens, it would be done here.

ASCII art created using:  https://patorjk.com/software/taag
"""

# --------------------------------------------------------------------------------------------------
# Imports Global Libraries
# --------------------------------------------------------------------------------------------------
from enum import Enum

# --------------------------------------------------------------------------------------------------
# Imports Local Libraries
# --------------------------------------------------------------------------------------------------
from .globals import TERMINAL_WIDTH

# --------------------------------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------------------------------
def print_list(l: list, centered=True) -> None:
    """This function prints a list as individual lines."""
    print()
    for l_ in l:
        if centered:
            print(l_.center(TERMINAL_WIDTH))
        else:
            print(l_)
    print()


# --------------------------------------------------------------------------------------------------
# ASCII Art
# --------------------------------------------------------------------------------------------------


class Loading(Enum):
    """This class is used for the progress bar. If you want to change the progress bar you can do it
    here."""
    LOADING = [
        "◐",
        "◓",
        "◑",
        "◒",
    ]  # The length of the list is irrelevant, as long as it is a list.
    EMPTY = "◯"
    DONE = "●"
    FAILED = "☹"


class Logo:
    """This is a class to print Logos"""

    def home():
        """This function prints the main logo"""
        print_list(LOGO_A_1)

    def done():
        """This function prints the done logo"""
        print_list(DONE_)

    def error():
        """This function prints the error logo"""
        print_list(ERROR_)


LOGO_A_1 = [
    "██████╗ ██╗   ██╗██╗     ███████╗███████╗",
    "██╔══██╗██║   ██║██║     ██╔════╝██╔════╝",
    "██████╔╝██║   ██║██║     ███████╗█████╗  ",
    "██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  ",
    "██║     ╚██████╔╝███████╗███████║███████╗",
    "╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝",
]

DONE_ = [
    "██████╗  ██████╗ ███╗   ██╗███████╗",
    "██╔══██╗██╔═══██╗████╗  ██║██╔════╝",
    "██║  ██║██║   ██║██╔██╗ ██║█████╗  ",
    "██║  ██║██║   ██║██║╚██╗██║██╔══╝  ",
    "██████╔╝╚██████╔╝██║ ╚████║███████╗",
    "╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝",
]

ERROR_ = [
    "▓█████  ██▀███   ██▀███   ▒█████   ██▀███  ",
    "▓█   ▀ ▓██ ▒ ██▒▓██ ▒ ██▒▒██▒  ██▒▓██ ▒ ██▒",
    "▒███   ▓██ ░▄█ ▒▓██ ░▄█ ▒▒██░  ██▒▓██ ░▄█ ▒",
    "▒▓█  ▄ ▒██▀▀█▄  ▒██▀▀█▄  ▒██   ██░▒██▀▀█▄  ",
    "░▒████▒░██▓ ▒██▒░██▓ ▒██▒░ ████▓▒░░██▓ ▒██▒",
    "░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░",
    " ░ ░  ░  ░▒ ░ ▒░  ░▒ ░ ▒░  ░ ▒ ▒░   ░▒ ░ ▒░",
    "   ░     ░░   ░   ░░   ░ ░ ░ ░ ▒    ░░   ░ ",
    "   ░  ░   ░        ░         ░ ░     ░     ",
]
