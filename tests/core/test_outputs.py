# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from core.outputs  import Outputs
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

def test_outputs():
    # Create variables
    variable_1 = Variable("variable_1", 2.5)
    # Create Outputs
    outputs = Outputs().add(variable_1)
    # Test Outputs
    assert isinstance(outputs, Outputs)
    assert isinstance(outputs, ContainerVariables)
    assert hasattr(outputs, "add")
    assert hasattr(outputs, "variable_1")
    assert outputs.variable_1 is variable_1
    assert outputs.__str__() == "Outputs().add(Variable(variable_1, 2.5, Units.UNITLESS, Sorry, no description yet., None))"
    assert outputs.__repr__() == outputs.__str__()


if __name__ == "__main__":
    test_outputs()
