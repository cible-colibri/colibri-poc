from colibri.core.model import Model
from colibri.core.variables.field import Field
from colibri.utils.enums_utils import (Roles,Units)

# M1a
class Wall(Model):

    def __init__(self, name: str):
        self.name = name

        self.Text = self.field("Text", 10.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.Tint = self.field("Tint", {}, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)

        self.Qwall = self.field("Qwall", {}, role=Roles.OUTPUTS, unit=Units.UNITLESS)

    def initialize(self):
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass

