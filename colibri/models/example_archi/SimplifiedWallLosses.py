from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class SimplifiedWallLosses(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name = name

        self.Text = Variable("Text", 10.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Boundaries = Variable("Boundaries", [], role=Roles.INPUTS, unit=Units.OBJECT_LIST)

        self.Qwall = Variable("Qwall", {}, role=Roles.OUTPUTS, unit=Units.DICTIONARY)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qwall = {}
        for boundary in self.Boundaries.value:
            space = boundary.space
            Tint = space.Tint
            Qwall[boundary.label] = boundary.u_value * boundary.area * (Tint - self.Text)

        self.Qwall.value = Qwall

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









