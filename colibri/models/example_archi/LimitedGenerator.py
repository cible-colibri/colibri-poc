from colibri.core.model import Model
from colibri.core.variables.field import Field
from colibri.utils.enums_utils import (Roles,Units)

class LimitedGenerator(Model):

    def __init__(self, name: str):
        self.name = name

        self.Qneeds = self.field("Qneeds", {}, role=Roles.INPUTS)

        self.Spaces = self.field('Spaces', [], role=Roles.INPUTS, structure = [
            Field("emitter.efficiency", 0.9, role=Roles.PARAMETERS, unit=Units.UNITLESS),
            Field("emitter.maxQ", 0.9, role=Roles.PARAMETERS, unit=Units.UNITLESS),
            Field("emitter.name", "1", role=Roles.PARAMETERS, unit=Units.UNITLESS)
        ])

        self.Qgenerator = self.field("Qgenerator", {}, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.Qprovided = self.field("Qprovided", {}, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)
        self.Qconsumed = self.field("Qconsumed", {}, role=Roles.OUTPUTS, unit=Units.WATT_HOUR)

    def initialize(self):
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        Qprovided = {}
        Qconsumed = {}

        for space in self.Spaces:
            space_count_emitter = len (space.emitters)
            maxQ = sum([e.maxQ for e in space.emitters])
            Qneeds = 0
            if space.label in self.Qneeds:
                Qneeds = self.Qneeds[space.label]
            qTotalProvided = min(maxQ, Qneeds)
            for emitter in space.emitters:
                Qconsumed[space.label] = qTotalProvided / (emitter.maxQ / maxQ * emitter.efficiency)
                Qprovided[space.label] = qTotalProvided / (emitter.maxQ / maxQ)

        self.Qprovided = Qprovided
        self.Qconsumed = Qconsumed


    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        self.print_outputs()
