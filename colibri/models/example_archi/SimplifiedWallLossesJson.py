from colibri.core.templates.inputs import Inputs
from colibri.core.model import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.field import Field
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class SimplifiedWallLossesJson(Model):

    def __init__(self, name: str, inputs: Inputs = None, parameters: Parameters = None):
        self.name = name
        super(SimplifiedWallLossesJson, self).__init__(name)

        self.Qwall = self.field("Qwall", {}, role=Roles.OUTPUTS, unit=Units.UNITLESS)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qwall = {}
        for boundary_id, boundary in self.inputs['boundary_collection'].items():
            Tint = None
            for space_id, space in self.inputs['nodes_collection']['space_collection'].items():
                if boundary['side_1'] == space_id or boundary['side_2'] == space_id:
                    Tint = space['Tint']

            if Tint:
                Qwall[boundary_id] = boundary['u_value'] * boundary['area'] * (Tint - self.inputs['Text'])

        self.Qwall = Qwall

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.get_fields(Roles.OUTPUTS):
            print(f"{output.name}={getattr(self, output.name)}")
