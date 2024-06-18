from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)

class ThermalSpace(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name

        self.Tint = Variable("Tint", 0.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qwall = Variable("Qwall", 0.0, role=Roles.INPUTS, unit=Units.WATT_HOUR)
        self.Tcons = Variable("Tcons", 0.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qprovided = Variable("Qprovided", 0.0, role=Roles.INPUTS, unit=Units.WATT_HOUR)
        self.OccGains = Variable("OccGains", 0.0, role=Roles.INPUTS, unit=Units.WATT_HOUR)

        self.Tint = Variable("Tint", 0.0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qneeds = Variable("Qneeds", 0.0, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.AnnualNeeds = Variable("AnnualNeeds", 0.0, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass









