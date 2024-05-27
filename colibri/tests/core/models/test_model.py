# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.models.model        import Model
from colibri.core.variables.variable import Variable
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
def test_models():
    # Create a model from Model
    class ModelChild(Model):

        def _assign_same_instance_variables(self) -> None:
            self.var_1 = Variable("var_1", 2, role = Roles.INPUTS)

        def check_units(self) -> None:
            pass

        def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
            pass

        def iteration_done(self, time_step: int = 0) -> None:
            pass

        def timestep_done(self, time_step: int = 0) -> None:
            pass

        def simulation_done(self, time_step: int = 0) -> None:
            pass

        def initialize(self) -> None:
            pass

    model = ModelChild("child")
    assert isinstance(model, ModelChild)
    assert isinstance(model, Model)
    assert isinstance(model.inputs, list)
    assert isinstance(model.outputs, list)
    assert isinstance(model.parameters, list)
    assert isinstance(model.get_variable("var_1"), Variable)
    assert model.var_1.value == 2
    model.var_1 = 4
    assert isinstance(model.get_variable("var_1"), Variable)
    assert model.var_1.value == 4
    assert model.inputs[0] == model.var_1
    assert model.__str__() == "ModelChild(name = 'child')"
    assert model.__repr__() == model.__str__()

if __name__ == "__main__":
    test_models()
