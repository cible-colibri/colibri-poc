from colibri.core.model import Model
from colibri.core.variables.field import Field
from colibri.utils.enums_utils import (Roles,Units)

class LimitedGenerator(Model):

    def __init__(self, name: str):
        self.name = name
        super(LimitedGenerator, self).__init__(name)

        self.Spaces = self.field('Boundaries', [], role=Roles.INPUTS, structure = [
            Field("Qneeds", 0, role=Roles.INPUTS, unit = Units.WATT_HOUR),
            Field("emitter.efficiency", 0.9, role=Roles.PARAMETERS, unit=Units.UNITLESS),
            Field("emitter.maxQ", 0.9, role=Roles.PARAMETERS, unit=Units.UNITLESS),
            Field("emitter.name", "1", role=Roles.PARAMETERS, unit=Units.UNITLESS)
        ])

        self.Qgenerator = self.field("Qgenerator", {}, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.Qprovided = self.field("Qprovided", {}, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.Qconsumed = self.field("Qconsumed", {}, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qprovided = {}
        Qconsumed = {}

        for space in self.Spaces:
            space_count_emitter = len (space.emitters)
            maxQ = sum([e.maxQ for e in space.emitters])
            qTotalProvided = min(maxQ, space.Qneeds)
            for emitter in space.emitters:
                Qconsumed[emitter.label] = qTotalProvided / (emitter.maxQ / maxQ * emitter.efficiency)
                Qprovided[emitter.label] = qTotalProvided / (emitter.maxQ / maxQ)

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.Qprovided:
            print(f"{output.name}={getattr(self, output.name)}")
        for output in self.Qconsumed:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass









