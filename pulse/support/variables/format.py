"""
format.py
---------

Author: Benedict Schwark 
Supervision: Nicolas Alaux
Other contributors: See README.md
License: See LICENSE.md

"""


def int_empty(x) -> int:
    """This function creates an integer from a string with whitespaces."""
    return int(x) if x.replace(" ", "") != "" else 0


def float_point(x) -> float:
    """This function creates a float from a string and prevents dots."""
    return float(x) if "." != x else float(0)


def float_dash(x) -> float:
    """This function creates a float from a string and prevents dashes and dots"""
    return float_point(x) if "-" not in x else 0


def float_komma(x) -> float:
    """This function creates a float from a string and prevents dashes, dots and kommas"""
    return float_dash(x.replace(",", ""))


def float_empty(x) -> float:
    """This function creates a float from a string and prevents dashed, dots, kommas and
    empty strings"""
    return float_komma(x) if x not in (""," ") else 0


def float_dash_split(x):
    """This function either returns a float or a list of integers, depending on weather
    the input has dashes"""
    return float_empty(x) if "-" not in x else [int_empty(y) for y in x.split("-")]


def int_dash(x) -> int:
    """This function returns an int and prevents dashes"""
    return int(float(x.strip())) if "-" not in x else 0


def list_strip(x: list) -> list:
    """This function returns a list of stripped strings."""
    return [y.strip() if y.strip() != "-" and y.strip() != '0' else "N/A" for y in x]


def int_komma(x) -> int:
    """This function returns an int and prevents dashes and komma"""
    return int_dash(x.replace(",", "")) if x != "" else 0


def list_int_komma(x) -> list:
    """This function returns a list of int and prevents dashes and komma"""
    return [int_komma(y) for y in x]


def list_float(x: list) -> list:
    """This function returns a list of floats."""
    return [float(y) for y in x]


def percent(data: dict) -> list:
    """This function transfers a dict of strings to a list of percentages"""
    data, unit = tuple(data.values())
    assert unit in ("%", "/"), f"ERROR: Wrong unit type, should be % is {unit}"
    return [round(float(d.strip().replace("%", "")) / 100, 4) for d in data]


def distribute_fully(total: int, distribution: dict) -> dict:
    """This function distributes a whole number onto a list of distributions wholely.
    It looses some accuracy."""
    if total == 0:
        return {k: 0 for k in distribution}
    number_distr = {year: int(d * total + 0.5) for year, d in distribution.items()}
    difference = sum(number_distr.values()) - total
    if not difference:
        return number_distr
    ordered = list(
        dict(
            sorted(distribution.items(), key=lambda item: item[1], reverse=True)
        ).keys()
    )
    multiplier = 1 if difference < 0 else -1
    for i in range(abs(difference)):
        assert (
            number_distr[ordered[i % len(ordered)]] >= 0
        ), f"Trying to subtract from 0 where it shouldnt be done {number_distr}"
        number_distr[ordered[i % len(ordered)]] += multiplier
    return number_distr


def remove_available(to_be_removed, amount) -> tuple[dict | list | int , int | list]:
    """This function removes the availble"""
    assert type(to_be_removed) is type(
        amount
    ), f"{type(to_be_removed) } vs. {type(amount)}"
    if isinstance(to_be_removed, int):
        to_be_removed -= amount
        if to_be_removed < 0:
            r = 0 - to_be_removed
            to_be_removed = 0
            return to_be_removed, r
        return to_be_removed, 0
    if isinstance(to_be_removed, list):
        overflow = []
        for pos_, (a, b) in enumerate(zip(to_be_removed, amount)):
            to_be_removed[pos_], c = remove_available(a, b)
            overflow.append(c)
        return to_be_removed, overflow
    if isinstance(to_be_removed, dict):
        overflow = []
        for pos_, ((a, b), c) in enumerate(zip(to_be_removed.items(), amount.values())):
            to_be_removed[a], d = remove_available(b, c)
            overflow.append(d)
        return to_be_removed, (
            overflow
            if (isinstance(overflow, list) and any(overflow))
            or (isinstance(overflow, int) and overflow)
            else 0
        )
    raise TypeError(f"NOOO, {type(to_be_removed)}")


def distribute_in_relation(total: int, reference: dict) -> dict:
    """This function distributes a number along a certain length."""
    return distribute_fully(
        total=total,
        distribution={
            a: b / sum(reference.values()) if sum(reference.values()) else b / 1
            for a, b in reference.items()
        },
    )


def add_available(to_be_added: dict, amount: dict, overflow: list[int]):
    """This function adds the available in amount to to_be_added."""
    return (
        {
            key: to_be_added[key] + amount[key] - over
            for key, over in zip(amount, overflow)
        }
        if overflow
        else {key: to_be_added[key] + amount[key] for key in amount}
    )


def get_share_of_used(
    distribution: list, use_of_empty: list, usage: str, code: str
) -> float:
    """This function combines the current use of empty dwellings, secondary homes and units with the
    correct scenario aspects.\n
    Arguments:
    ----------
    distribution (list):
        This is a list of 3 float numbers defining the share of occupied, empty and optionally
        secondary units.
    use_of_empty (list):
        This is a list of 3 float numbers defining the share of empty dwellings, secondary dwellings
        and empty units, that is to be reappropriated.
    usage (str):
        This is an indicator what type of building this is. Must either be "Residential" or
        "Non-residential"
    Return:
    -------
    (float)
        A float number between 0 and 1 describing the share of buildings that are being used, based
        on the scenario.
    """
    assert len(distribution) == 3 and len(use_of_empty) == 3, "Good Blei"
    assert (
        round(sum(distribution), 3) == 1
    ), f"Error, The share of used buildings for {code} does not add to 1" +\
       f"({distribution[0]},{distribution[1]},{distribution[2]})" + \
       f"{sum(distribution)}"
    if usage == "Residential":
        return (
            distribution[0]
            + distribution[1] * (use_of_empty[0] if use_of_empty[0] else 0)
            + distribution[2] * (use_of_empty[1] if use_of_empty[1] else 0)
        )
    if usage == "Non-residential":
        return distribution[0] + distribution[1] * (
            use_of_empty[2] if use_of_empty[2] else 0
        )
    raise NotImplementedError("There are currently no other options than res and non-res supported")


def prime(n: int) -> bool:
    """This function figures out if a number is a prime number."""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
