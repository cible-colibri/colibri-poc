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

        self.Qwall = Variable("Qwall", 0.0, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qwall = {}
        for i, boundary in enumerate(self.project.building_data.boundary_list):
            space = self.project.building_data.space_for_boundary(boundary)
            if space:
                Tint = space.Tint
                Qwall[boundary.label] = boundary.u_value * boundary.area * (Tint - self.Text)
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









