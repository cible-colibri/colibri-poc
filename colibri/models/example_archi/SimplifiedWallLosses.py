from colibri.core.model import Model
from colibri.core.variables.field import Field
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class SimplifiedWallLosses(Model):

    def __init__(self, name: str):
        self.name = name
        super(SimplifiedWallLosses, self).__init__(name)

        self.Text = self.field("Text", 10.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Tint = self.field("Tint", {}, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Boundaries = self.field("Boundaries", [], role=Roles.INPUTS, unit=Units.UNITLESS,
                                   structure = [
                                       Field('u_value', 0, Roles.PARAMETERS, Units.WATT_PER_SQUARE_METER_PER_KELVIN),
                                       Field('area', 0, Roles.PARAMETERS, Units.WATT_PER_SQUARE_METER_PER_KELVIN),
                                       Field('space.Tint', 0, Roles.INPUTS, Units.DEGREE_CELSIUS)
                                   ])

        self.Qwall = self.field("Qwall", {}, role=Roles.OUTPUTS, unit=Units.UNITLESS)

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
