# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib

# ========================================
# Internal imports
# ========================================


# ========================================
# Constants
# ========================================

from utils.files_utils import read_json_file

# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


# ========================================
# Functions
# ========================================

def test_data():
    # Read units file
    # TODO: Modify when we wil have a package structure
    colibrisuce_path = pathlib.Path(__file__).parents[2]
    units_file_path  = colibrisuce_path / "config" / "data" / "units" / "units.json"
    units            = read_json_file(units_file_path)
    # Check format of the units file
    assert isinstance(units, dict)
    assert isinstance(units["dimensions"], list)
    assert len(units["dimensions"]) == 66
    for unit in units["dimensions"]:
        assert isinstance(unit["name"], str)
        assert isinstance(unit["definition"], str)
        assert isinstance(unit["base_unit"], dict)
        assert isinstance(unit["equivalent_units"], list)
    # TODO: Add test for weather files


if __name__ == "__main__":
    test_data()
