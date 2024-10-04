"""
reducers.py
-----------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""

from .globals import Detail


def find_detail(data):
    """This function can calculate the detail of a given dictionary

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not isinstance(data, dict):
        return 0
    if len(data) == 0:
        return 1
    depths = [find_detail(value) for value in data.values()]
    return max(depths) + 1


def reduce_detail(data) -> dict | int:
    """This function reduces the detail of an lca dictionary by one!"""
    if isinstance(data, dict) and data == {}:
        return 0
    if isinstance(data, dict) and isinstance(list(data.values())[0], dict):
        r_ = {}
        for key, data_ in data.items():
            r_[key] = reduce_detail(data_)
        return r_
    if isinstance(data, dict):
        r_ = 0
        for key, data_ in data.items():
            if not data_:
                continue
            if not r_:
                r_ = data_
            else:
                r_ += data_
        return r_
    return data


def adapt_detail(data: dict | int, goal_detail: Detail):
    """This function adapts the detail of a dictionary."""
    if data == {}:
        return 0
    current_detail = find_detail(data)
    if current_detail + 1 < goal_detail.value:
        #raise TypeError
        return data
    while current_detail + 1 > goal_detail.value:
        data = reduce_detail(data)
        current_detail -= 1
    return data


def remove_empty(data):
    """This function removes empty entries in dictionaries.

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    if isinstance(data, dict):
        return {
            key: remove_empty(data_)
            for key, data_ in data.items()
            if remove_empty(data_)
        }
    if isinstance(data, list):
        return data if any(data) else None
    if isinstance(data, int):
        return data
    if isinstance(data, float):
        return data
    return data
