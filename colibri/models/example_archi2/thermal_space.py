import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)


class ThermalSpace(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name

        self.Tint = Variable("Tint", np.array(()), role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qwall = Variable("Qwall", np.array(()), role=Roles.INPUTS, unit=Units.WATT_HOUR)
        self.Tcons = Variable("Tcons", 0.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qprovided = Variable("Qprovided", 0.0, role=Roles.INPUTS, unit=Units.WATT_HOUR)
        self.OccGains = Variable("OccGains", 0.0, role=Roles.INPUTS, unit=Units.WATT_HOUR)

        self.Tint = Variable("Tint", np.array(()), role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qneeds = Variable("Qneeds", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.AnnualNeeds = Variable("AnnualNeeds", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

        self.spaceSurface = Variable("spaceSurface", np.array(()), role=Roles.PARAMETERS, unit=Units.SQUARE_METER)
        self.spaceHeight = Variable("spaceHeights", np.array(()), role=Roles.PARAMETERS, unit=Units.METER)

    def initialize(self):
        self.Tint.value = np.array([20 for _ in range()])

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        pass

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass









