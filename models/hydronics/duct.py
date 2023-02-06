# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import math

# ========================================
# Internal imports
# ========================================

from core.model        import Model
from core.variable     import Variable
from utils.enums_utils import (
                                Roles,
                                Units,
                               )

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


class Duct(Model):

    def _define_variables(self) -> None:
        self.loss_coefficient    = Variable("loss_coefficient", 3.0, role=Roles.INPUTS, unit=Units.KILO_JOULE_PER_HOUR)
        self.cp_fluid            = Variable("cp_fluid", 4.186, role=Roles.INPUTS, unit=Units.JOULE_PER_GRAM_PER_DEGREE_CELCIUS)
        self.inlet_flow_rate     = Variable("inlet_flow_rate", 100, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.inlet_temperature   = Variable("inlet_temperature", 40, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.outside_temperature = Variable("outside_temperature", 20, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.outlet_flow_rate    = Variable("outlet_flow_rate", 0.0, role=Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.outlet_temperature  = Variable("outlet_temperature", 0.0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.loss_factor         = Variable("loss_factor", 0.0, role=Roles.PARAMETERS, unit=Units.UNITLESS)

    def initialize(self) -> None:
        self.loss_factor = 1.0 - math.exp(- self.loss_coefficient / (self.inlet_flow_rate * self.cp_fluid))

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0):
        self.outlet_flow_rate   = self.inlet_flow_rate
        self.outlet_temperature = (1.0 - self.loss_factor) * self.inlet_temperature + self.loss_factor * self.outside_temperature

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass

# ========================================
# Functions
# ========================================
