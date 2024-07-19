import numpy as np

from colibri.config.constants import DENSITY_AIR
from colibri.core.model import Model
from colibri.core.variables.field import Field
from colibri.utils.enums_utils import (Roles,Units)

class ThermalSpaceSimplified(Model):

    def __init__(self, name: str):
        self.name = name

        self.Qprovided = self.field('Qprovided', {}, role=Roles.INPUTS)

        self.Spaces = self.field("Spaces", [], role=Roles.INPUTS, unit=Units.UNITLESS,
                                   structure = [
                                       Field('Tint', 0, Roles.INPUTS, Units.DEGREE_CELSIUS),
                                       Field("setpoint_heating", 0.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS),
                                       Field('surface', 0, Roles.PARAMETERS, Units.SQUARE_METER),
                                       Field('height', 0, Roles.PARAMETERS, Units.METER)
                                   ])

        self.Qwall = self.field("Qwall", {}, role=Roles.INPUTS)

        self.Tint = self.field("Tint", {}, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.Qneeds = self.field("Qneeds", {}, role=Roles.OUTPUTS)
        self.AnnualNeeds = self.field("AnnualNeeds", 0.0, role=Roles.OUTPUTS,)
        pass

    def initialize(self):
        for space in self.Spaces:
            space.Tint = 20.0
            space.previousTint = 20.0

        self.tempAnnualNeeds = 0.0

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        pass
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

            self.Tint[space.label] = previousTint + qEffective / (DENSITY_AIR * space.reference_area * space.height)

            self.project._has_converged = self.calc_convergence(threshold=0.5)

    def iteration_done(self, time_step: int = 0):
        self.Tint_dict_last = self.Tint

    def timestep_done(self, time_step: int = 0):
        for space in self.Spaces:
            space.previous_set_point_heating = space.set_point_heating
        self.AnnualNeeds += self.tempAnnualNeeds


    def simulation_done(self, time_step: int = 0):
        self.AnnualNeeds = self.tempAnnualNeeds

        self.print_outputs()

    # temporary convergence control; will be in backbone, but does not work yet for dictionaries
    def calc_convergence(self, threshold=1e-3):
        if not hasattr(self, 'Tint_dict_last') or not len(self.Tint) == len(self.Tint_dict_last):
            return
        tint = self.Tint.values()
        tint_last = self.Tint_dict_last.values()
        self.has_converged = np.max(np.abs(np.array(list(tint)) - np.array(list(tint_last)))) <= threshold
