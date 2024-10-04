"""
colors.py
---------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

Description: This file stores a collection of different special characters for use in graphs.
"""

# --------------------------------------------------------------------------------------------------
# Global Imports
# --------------------------------------------------------------------------------------------------
import random

# --------------------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------------------
def combine_colors(*colors: str) -> str:
    """This function combines an arbitrary amount of colors"""
    temp_colors = [hex_rgb(color) for color in colors]
    n_c = len(colors)
    if n_c == 0:
        return rgb_hex(0, 0, 0)

    t_r, t_g, t_b = [sum(color[i] for color in temp_colors) for i in range(3)]
    c_r, c_g, c_b = t_r // n_c, t_g // n_c, t_b // n_c

    return rgb_hex(c_r, c_g, c_b)


def rgb_hex(r: int, g: int, b: int) -> str:
    """This function transfers rgp to hex,"""
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_rgb(color: str):
    """This function transfers hex to rgb."""
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def color_range(start: str, end: str, steps: int) -> list[str]:
    """This function creates a color range from color 'start' to color 'end' with 'steps' amount of
    steps."""
    assert len(start) == 7, "TET"
    assert len(end) == 7, "TET"
    if steps == 1:
        return [end]
    a_r, a_g, a_b = hex_rgb(start)
    b_r, b_g, b_b = hex_rgb(end)
    return [
        rgb_hex(
            int(a_r + (b_r - a_r) / (steps - 1) * i + 0.5),
            int(a_g + (b_g - a_g) / (steps - 1) * i + 0.5),
            int(a_b + (b_b - a_b) / (steps - 1) * i + 0.5),
        )
        for i in range(steps)
    ]


def color_rand(number, seed=1234) -> list[str]:
    """This function creates a list of random colors of length number"""
    random.seed(seed)
    return [
        rgb_hex(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        for _ in range(number)
    ]


def hex_to_rgba(hex_color, alpha: float = 1.0) -> str:
    """This function turns a hex code to a rgb code."""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
