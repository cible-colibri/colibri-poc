# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from utils.unit_utils import (
                                Dimension,
                                UnitConverter,
                                Unit,
                              )

# ========================================
# Constants
# ========================================

from data.constants import (
                                SOLAR_CONSTANT_OF_THE_EARTH,
                                UNIT_CONVERTER,
                              )

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
def test_constants():
    assert isinstance(SOLAR_CONSTANT_OF_THE_EARTH, float)
    assert SOLAR_CONSTANT_OF_THE_EARTH == 1367.0
    assert isinstance(UNIT_CONVERTER, UnitConverter)
    assert isinstance(UNIT_CONVERTER.dimensions, list)
    for dimension in UNIT_CONVERTER.dimensions:
        assert isinstance(dimension, Dimension)
        assert isinstance(dimension.base_unit, Unit)
        if dimension.equivalent_units:
            for equivalent_unit in dimension.equivalent_units:
                assert isinstance(equivalent_unit, Unit)


if __name__ == "__main__":
    test_constants()
