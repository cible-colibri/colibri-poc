import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)


class ThermalSpace(Model):

    def __init__(self, name: str):
        self.name = name

        self.Tint = self.field("Tint", np.array(()), role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qwall = self.field("Qwall", np.array(()), role=Roles.INPUTS, unit=Units.WATT_HOUR)
        self.Tcons = self.field("Tcons", 0.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qprovided = self.field("Qprovided", 0.0, role=Roles.INPUTS, unit=Units.WATT_HOUR)
        self.OccGains = self.field("OccGains", 0.0, role=Roles.INPUTS, unit=Units.WATT_HOUR)

        self.Tint = self.field("Tint", np.array(()), role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qneeds = self.field("Qneeds", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.AnnualNeeds = self.field("AnnualNeeds", np.array(()), role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

        self.spaceSurface = self.field("spaceSurface", np.array(()), role=Roles.PARAMETERS, unit=Units.SQUARE_METER)
        self.spaceHeight = self.field("spaceHeights", np.array(()), role=Roles.PARAMETERS, unit=Units.METER)

    def initialize(self):
        self.Tint = np.array([20 for _ in range()])

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









