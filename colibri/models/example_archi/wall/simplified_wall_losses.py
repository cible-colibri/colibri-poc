from colibri.core.variables.field import Field
from colibri.models.example_archi.wall.wall import Wall
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class SimplifiedWallLosses(Wall):

    def __init__(self, name: str):
        self.name = name

        self.Boundaries = self.field("Boundaries", [], role=Roles.INPUTS, unit=Units.UNITLESS,
                                   structure = [
                                       Field('u_value', 0, Roles.PARAMETERS, Units.WATT_PER_SQUARE_METER_PER_KELVIN),
                                       Field('area', 0, Roles.PARAMETERS, Units.SQUARE_METER)
                                   ])


    def initialize(self):
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qwall = {}
        for boundary in self.Boundaries:
            space = boundary.space
            if boundary.space.label in self.Tint:
                Tint = self.Tint[space.label]
            else:
                Tint = space.Tint
            Qwall[boundary.label] = boundary.u_value * boundary.area * (Tint - self.Text)

        self.Qwall = Qwall

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        self.print_outputs()
