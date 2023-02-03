# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


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

def test_conditions():
    # Create variables
    variable_1 = Variable("variable_1", 2.5)
    # Create conditions
    conditions = Conditions().add(variable_1)
    # Test conditions
    assert isinstance(conditions, Conditions)
    assert isinstance(conditions, ContainerVariables)
    assert hasattr(conditions, "add")
    assert hasattr(conditions, "variable_1")
    assert conditions.variable_1 is variable_1
    assert conditions.__str__() == "Conditions().add(Variable(variable_1, 2.5, Units.UNITLESS, Sorry, no description yet., None))"
    assert conditions.__repr__() == conditions.__str__()


if __name__ == "__main__":
    test_conditions()
