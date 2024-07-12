# -*- coding: utf-8 -*-

#========================================
# External imports
#========================================

import pytest

#========================================
# Internal imports
#========================================

from colibri.utils.enums_utils import Units

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
    assert Units.JOULE == "J"
    assert Units.JOULE.name == "JOULE"


if __name__ == "__main__":
    test_units()
