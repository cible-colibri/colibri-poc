# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.model        import Model
from colibri.core.templates.inputs import Inputs
from colibri.core.templates.outputs import Outputs
from colibri.core.templates.parameters import Parameters
from colibri.core.variables.field import Field
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import Roles, Units


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
            self.var_1 = self.field("var_1", 2, role = Roles.INPUTS)

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

    class M1(Model):
        def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None, parameters: Parameters = None):
            self.name = name
            super(M1, self).__init__(name)

            self.V1 = self.field("V1", 42, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
            self.objects1 = self.field("objects1", 42, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS,
                                  structure = [
                                      Field(name='o1v1', unit=Units.DEGREE_CELSIUS, role=Roles.INPUTS, default_value=42),
                                      Field(name='o1v2', unit=Units.DEGREE_CELSIUS, role=Roles.INPUTS, default_value=42),
                                  ])
            self.V2 = self.field("V2", 43, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
            self.V3 = self.field("V3", 44, role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS)
            self.V4 = self.field("V4", 45, role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS)

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

    m1 = M1("m1")
    v = m1.get_field_value("V1")
    assert v == 42

    f = m1.get_field("V2")
    assert f.name == "V2"

    print(m1.input_template())

if __name__ == "__main__":
    test_models()
