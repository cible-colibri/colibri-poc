# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from core.parameters import Parameters
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

def test_parameters():
    # Create variables
    variable_1 = Variable("variable_1", 2.5)
    # Create parameters
    parameters = Parameters().add(variable_1)
    # Test parameters
    assert isinstance(parameters, Parameters)
    assert isinstance(parameters, ContainerVariables)
    assert hasattr(parameters, "add")
    assert hasattr(parameters, "variable_1")
    assert parameters.variable_1 is variable_1
    assert parameters.__str__() == "Parameters().add(Variable(variable_1, 2.5, Units.UNITLESS, Sorry, no description yet., None))"
    assert parameters.__repr__() == parameters.__str__()


if __name__ == "__main__":
    test_parameters()
