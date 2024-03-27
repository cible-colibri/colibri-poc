# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.templates.inputs import Inputs
from colibri.core.variables.variable import (
                                  Variable,
                                  ContainerVariables,
                              )
from colibri.utils.enums_utils import Roles

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
def test_inputs():
    variable_1 = Variable("variable_1", 2.5, Roles.INPUTS)
    inputs = Inputs().add(variable_1)
    assert isinstance(inputs, Inputs)
    assert isinstance(inputs, ContainerVariables)
    assert hasattr(inputs, "add")
    assert hasattr(inputs, "variable_1")
    assert inputs.variable_1 is variable_1
    assert inputs.__str__() == "Inputs().add(Variable(variable_1, 2.5, Roles.INPUTS, Units.UNITLESS, Sorry, no description yet., None))"
    assert inputs.__repr__() == inputs.__str__()


if __name__ == "__main__":
    test_inputs()
