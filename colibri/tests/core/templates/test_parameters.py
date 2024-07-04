# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.templates.parameters import Parameters
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
def test_parameters():
    variable_1 = Variable("variable_1", 2.5, Roles.PARAMETERS)
    parameters = Parameters().add(variable_1)
    assert isinstance(parameters, Parameters)
    assert isinstance(parameters, ContainerVariables)
    assert hasattr(parameters, "add")
    assert hasattr(parameters, "variable_1")
    assert parameters.variable_1 is variable_1
    assert parameters.__str__() == "Parameters().add(Variable(variable_1, 2.5, Roles.PARAMETERS, Units.UNITLESS, , None))"
    assert parameters.__repr__() == parameters.__str__()


if __name__ == "__main__":
    test_parameters()
