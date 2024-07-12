import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles, Units)


class SimplifiedWallLosses(Model):

    def __init__(self, name: str):
        self.name = name
        self.Tint = self.field("Tint", np.array(()), role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Text = self.field("Text", 10.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qwall = self.field("Qwall", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.U = self.field("U", np.array(()), role=Roles.PARAMETERS, unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN)
        self.S = self.field("S", np.array(()), role=Roles.PARAMETERS, unit=Units.SQUARE_METER)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        self.Qwall = np.multiply(np.multiply(self.U, self.S), (self.Tint - self.Text))

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass
