import numpy as np

from colibri.config.constants import DENSITY_AIR, CP_AIR
from colibri.core.model import Model
from colibri.core.variables.field import Field
from colibri.utils.enums_utils import (Roles,Units)

class ThermalSpaceSimplified(Model):

    def __init__(self, name: str):
        self.name = name

        self.Qprovided = self.field('Qprovided', {}, role=Roles.INPUTS, unit=Units.WATT_HOUR, key = 'Spaces.label')

        self.Spaces = self.field("Spaces", [], role=Roles.INPUTS, unit=Units.UNITLESS,
                                   structure = [
                                       Field('Tint', 0, Roles.PARAMETERS, Units.DEGREE_CELSIUS),
                                       Field("setpoint_heating", 0.0, role=Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS),
                                       Field('surface', 0, Roles.PARAMETERS, Units.SQUARE_METER),
                                       Field('height', 0, Roles.PARAMETERS, Units.METER)
                                   ])

        self.Qwall = self.field("Qwall", {}, role=Roles.INPUTS)

        self.Tint = self.field("Tint", {}, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS, key = 'Spaces.label')
        self.Qneeds = self.field("Qneeds", {}, role=Roles.OUTPUTS)
        self.AnnualNeeds = self.field("AnnualNeeds", 0.0, role=Roles.OUTPUTS,)

    def initialize(self):
        self.tempAnnualNeeds = 0.0

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        for space in self.Spaces:
            qWall = 0
            for wall_label in [b.label for b in space.boundaries]:
                if wall_label in self.Qwall:
                    qWall += self.Qwall[wall_label]

            self.Qneeds[space.label] = (space.set_point_heating - space.previous_set_point_heating) * (DENSITY_AIR * space.reference_area * space.height) + qWall - space.qOccGains
            self.tempAnnualNeeds = ((space.set_point_heating - space.previous_set_point_heating) * (DENSITY_AIR * space.reference_area * space.height) + qWall - space.qOccGains) / space.reference_area

            qProvided = 0
            if space.label in self.Qprovided:
                qProvided = self.Qprovided[space.label]

            qEffective = qProvided + space.qOccGains - qWall
            if time_step > 1 and space.label in self.Tint_series[time_step-1]:
                previousTint = self.Tint_series[time_step-1][space.label]
            else:
                previousTint = space.Tint

            self.Tint[space.label] = previousTint + qEffective / (DENSITY_AIR * CP_AIR * space.reference_area * space.height)

    def iteration_done(self, time_step: int = 0):
        self.Tint_dict_last = self.Tint

    def timestep_done(self, time_step: int = 0):
        for space in self.Spaces:
            space.previous_set_point_heating = space.set_point_heating
        self.AnnualNeeds += self.tempAnnualNeeds


    def simulation_done(self, time_step: int = 0):
        self.AnnualNeeds = self.tempAnnualNeeds

        self.print_outputs()

