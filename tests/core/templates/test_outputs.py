# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from core.templates.outputs import Outputs
from core.variables.variable import (
                                  Variable,
                                  ContainerVariables,
                              )
from utils.enums_utils import Roles

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
def test_outputs():
    variable_1 = Variable("variable_1", 2.5, Roles.OUTPUTS)
    outputs = Outputs().add(variable_1)
    assert isinstance(outputs, Outputs)
    assert isinstance(outputs, ContainerVariables)
    assert hasattr(outputs, "add")
    assert hasattr(outputs, "variable_1")
    assert outputs.variable_1 is variable_1
    assert outputs.__str__() == "Outputs().add(Variable(variable_1, 2.5, Roles.OUTPUTS, Units.UNITLESS, Sorry, no description yet., None))"
    assert outputs.__repr__() == outputs.__str__()


if __name__ == "__main__":
    test_outputs()