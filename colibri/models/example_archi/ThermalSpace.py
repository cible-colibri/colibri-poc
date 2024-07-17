from colibri.config.constants import DENSITY_AIR
from colibri.core.model import Model
from colibri.core.variables.field import Field
from colibri.utils.enums_utils import (Roles,Units)

class ThermalSpaceSimplified(Model):

    def __init__(self, name: str):
        self.name = name
        super(ThermalSpaceSimplified, self).__init__(name)

        self.Spaces = self.field("Spaces", [], role=Roles.INPUTS, unit=Units.UNITLESS,
                                   structure = [
                                       Field('Tint', 0, Roles.INPUTS, Units.DEGREE_CELSIUS),
                                       Field("setpoint_heating", 0.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS),
                                       Field('emitter.Qprovided', 0, Roles.INPUTS),
                                       Field('surface', 0, Roles.PARAMETERS, Units.SQUARE_METER),
                                       Field('height', 0, Roles.PARAMETERS, Units.METER)
                                   ])

        self.Qwall = self.field("Qwall", {}, role=Roles.INPUTS)

        self.Tint = self.field("Tint", {}, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.QNeeds = self.field("QNeeds", {}, role=Roles.OUTPUTS)
        self.AnnualNeeds = self.field("AnnualNeeds", 0.0, role=Roles.OUTPUTS,)
        pass

    def initialize(self):
        for space in self.Spaces:
            space.Tint = 20.0
            space.previousTint = 20.0

        self.tempAnnualNeeds = 0.0

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        pass
        for space in self.Spaces:
            qWall = 0
            for wall_label in [b.label for b in space.boundaries]:
                if wall_label in self.Qwall:
                    qWall += self.Qwall[wall_label]

            self.QNeeds[space.label] = (space.set_point_heating - space.previous_set_point_heating) * (DENSITY_AIR * space.reference_area * space.height) + qWall - space.qOccGains
            self.tempAnnualNeeds = ((space.set_point_heating - space.previous_set_point_heating) * (DENSITY_AIR * space.reference_area * space.height) + qWall - space.qOccGains) / space.reference_area
            qProvided = sum([e.qProvided for e in space.emitters])
            qEffective = qProvided + space.qOccGains - qWall
            self.Tint[space.label] = space.previousTint + qEffective / (DENSITY_AIR * space.reference_area * space.height)

    def simulation_done(self, time_step: int = 0):
        self.AnnualNeeds = self.tempAnnualNeeds

        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        for space in self.Spaces:
            space.previous_set_point_heating = space.set_point_heating
            space.previousTint = space.Tint
        self.AnnualNeeds += self.tempAnnualNeeds


    def simulation_done(self, time_step: int = 0):
        pass

        print(f"{self.name}:")
        for output in self.get_fields(Roles.OUTPUTS):
            print(f"{output.name}={getattr(self, output.name)}")


