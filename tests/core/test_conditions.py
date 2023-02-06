# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from core.conditions import Conditions
from core.variable   import (
                                Variable,
                                ContainerVariables,
                            )

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

@pytest.mark.short_test
def test_conditions():
    variable_1 = Variable("variable_1", 2.5)
    conditions = Conditions().add(variable_1)
    assert isinstance(conditions, Conditions)
    assert isinstance(conditions, ContainerVariables)
    assert hasattr(conditions, "add")
    assert hasattr(conditions, "variable_1")
    assert conditions.variable_1 is variable_1
    assert conditions.__str__() == "Conditions().add(Variable(variable_1, 2.5, Units.UNITLESS, Sorry, no description yet., None))"
    assert conditions.__repr__() == conditions.__str__()


if __name__ == "__main__":
    test_conditions()
