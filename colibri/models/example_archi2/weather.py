import numpy as np
from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)

class WeatherModel(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name
        self.Text = self.field("Text", 0.0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.altitude = self.field("altitude", np.array(()), role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.TextScenario = self.field("TextScenario", np.array([5, 8, 7, 6, 9]), role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

    def initialize(self):
        mean_altitude = sum(self.altitude)
        tempDiminutionWithAltitude = 0.006
        self.TextScenarioCorrected = self.TextScenario - (tempDiminutionWithAltitude * mean_altitude)


    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        self.Text = self.TextScenarioCorrected[time_step]

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









