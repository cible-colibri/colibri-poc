from colibri.core.model import Model
from colibri.utils.enums_utils import (Roles,Units)

class Occupants(Model):

    def __init__(self, name: str):
        self.name = name

        self.Tcons = self.field("Tcons", 0.0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.QoccGains = self.field("QoccGains", 0.0, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

    def initialize(self):
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")
