# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib

# ========================================
# Internal imports
# ========================================

from utils.files_utils     import read_json_file
from utils.unit_dictionary import UnitDictionary

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


# ========================================
# Functions
# ========================================

# Return an object to convert from one unit to another (containing all unit conversion factors)
def get_unit_converter() -> UnitDictionary:
    """Return an object to convert from one unit to another (containing all unit conversion factors)

    Parameters
    ----------

    Returns
    -------
    unit_converter : UnitDictionary
        UnitDictionary object to convert from one unit to another (containing all unit conversion factors)

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # TODO : Modify when we wil have a package structure
    colibrisuce_path = pathlib.Path(__file__).parents[1]
    units_file_path  = colibrisuce_path / "config" / "data" / "units" / "units.json"
    units            = read_json_file(units_file_path)
    unit_converter   = UnitDictionary(**units)
    return unit_converter
