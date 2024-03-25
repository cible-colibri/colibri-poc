# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib
import os
import pytest

# ========================================
# Internal imports
# ========================================


# ========================================
# Constants
# ========================================
from pkg_resources import resource_filename

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

@pytest.mark.short_test
def test_data():
    # TODO: Modify when we wil have a package structure
    data_path = resource_filename('data')
    units_file_path  = os.path.join(data_path, "units", "units.json")
    units            = read_json_file(units_file_path)
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
