# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from core.model    import Model
from core.variable import Variable

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

        def _define_variables(self) -> None:
            pass

        def check_units(self) -> None:
            pass

        def run(self, time_step: int = 0) -> None:
            pass

        def iteration_done(self, time_step: int = 0) -> None:
            pass

        def timestep_done(self, time_step: int = 0) -> None:
            pass

        def simulation_done(self, time_step: int = 0) -> None:
            pass

        def _define_outputs(self) -> list:
            pass

        def _define_conditions(self) -> list:
            pass

        def _define_parameters(self) -> list:
            pass

        def initialize(self) -> None:
            pass

        def _define_inputs(self) -> list:
            inputs = [Variable("var_1", 2)]
            return inputs

    model = ModelChild("child")
    assert isinstance(model, ModelChild)
    assert isinstance(model, Model)
    assert isinstance(model.inputs, list)
    assert isinstance(model.outputs, list)
    assert isinstance(model.parameters, list)
    assert isinstance(model.conditions, list)
    assert isinstance(model.get_variable("var_1"), Variable)
    assert model.var_1.value == 2
    model.var_1 = 4
    assert isinstance(model.get_variable("var_1"), Variable)
    assert model.var_1.value == 4
    assert model.__str__() == "ModelChild(name = 'child')"
    assert model.__repr__() == model.__str__()

if __name__ == "__main__":
    test_models()
