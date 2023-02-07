# -*- coding: utf-8 -*-

#========================================
# External imports
#========================================

import pytest

#========================================
# Internal imports
#========================================

from utils.enums_utils import Units

#========================================
# Constants
#========================================


#========================================
# Variables
#========================================


#========================================
# Classes
#========================================


#========================================
# Functions
#========================================

@pytest.mark.short_test
def test_units() -> None:
    assert len([enum for enum in Units]) == 24
    assert Units.JOULE.value == "J"
    assert Units.JOULE.name == "JOULE"


if __name__ == "__main__":
    test_units()