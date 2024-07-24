from colibri.core.variables.field import Field
from colibri.models.example_archi.wall.Wall import Wall
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class LayerWallLosses(Wall):

    def __init__(self, name: str):
        self.name = name

        self.Boundaries = self.field("Boundaries", [], role=Roles.INPUTS, unit=Units.UNITLESS,
                                   structure = [
                                       Field('thermal_conductivity', [1], Roles.PARAMETERS, Units.WATT_PER_SQUARE_METER_PER_KELVIN),
                                       Field('thickness', [1], Roles.PARAMETERS, Units.METER),
                                       Field('area', 5, Roles.PARAMETERS, Units.SQUARE_METER),
                                       Field('space.Tint', 19, Roles.INPUTS, Units.DEGREE_CELSIUS),
                                       Field('label', "boundary_0", Roles.PARAMETERS, Units.UNITLESS),
                                   ])



    def initialize(self):
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qwall = {}
        for boundary in self.Boundaries:
            space = boundary.space
            if space:
                if boundary.space.label in self.Tint:
                    Tint = self.Tint[space.label]
                else:
                    Tint = space.Tint

                e = boundary.thickness
                Lambda = boundary.thermal_conductivity

                R = sum(e1 / Lambda1 for e1, Lambda1 in zip(e, Lambda))
                U = 1 / R

                Qwall[boundary.label] = U * boundary.area * (Tint - self.Text)

        self.Qwall = Qwall


    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        self.print_outputs()

