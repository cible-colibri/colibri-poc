import numpy as np

from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles, Units)

class InfinitePowerGenerator(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        self.Qneeds = Variable("Qneeds", 0.0, role=Roles.INPUTS, unit=Units.WATT)
        self.Qprovided = Variable("Qprovided", 0.0, role=Roles.INPUTS, unit=Units.WATT)
        self.Qconsumed = Variable("Qconsumed", 0.0, role=Roles.INPUTS, unit=Units.WATT)
        self.Efficiency = Variable("Efficiency", 0.0, role=Roles.PARAMETERS, unit=Units.UNITLESS)

    def initialize(self):
        pass

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









