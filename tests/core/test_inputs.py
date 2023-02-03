# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from core.inputs   import Inputs
from core.variable import (
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

def test_inputs():
    # Create variables
    variable_1 = Variable("variable_1", 2.5)
    # Create Inputs
    inputs = Inputs().add(variable_1)
    # Test Inputs
    assert isinstance(inputs, Inputs)
    assert isinstance(inputs, ContainerVariables)
    assert hasattr(inputs, "add")
    assert hasattr(inputs, "variable_1")
    assert inputs.variable_1 is variable_1
    assert inputs.__str__() == "Inputs().add(Variable(variable_1, 2.5, Units.UNITLESS, Sorry, no description yet., None))"
    assert inputs.__repr__() == inputs.__str__()


if __name__ == "__main__":
    test_inputs()
