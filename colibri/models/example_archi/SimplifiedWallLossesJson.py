
from colibri.core.model import Model

from colibri.utils.enums_utils import (Roles,Units)

# M1a
class SimplifiedWallLossesJson(Model):

    def __init__(self, name: str):
        self.name = name

        self.Qwall = self.field("Qwall", {}, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

    def initialize(self):
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

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        self.print_outputs()