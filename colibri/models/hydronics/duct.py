# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import math

# ========================================
# Internal imports
# ========================================

from colibri.core.templates.inputs import Inputs
from colibri.core.model        import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import (
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

    def __init__(self, name: str):
        self.name                = name
        super(Duct, self).__init__(name)

        self.project             = None

        self.loss_coefficient    = self.field("loss_coefficient", 3.0, role=Roles.INPUTS, unit=Units.KILO_JOULE_PER_HOUR)
        self.cp_fluid            = self.field("cp_fluid", 4.186, role=Roles.INPUTS, unit=Units.JOULE_PER_GRAM_PER_DEGREE_CELCIUS)
        self.inlet_flow_rate     = self.field("inlet_flow_rate", 100, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.inlet_temperature   = self.field("inlet_temperature", 40, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.outside_temperature = self.field("outside_temperature", 20, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)

        self.outlet_flow_rate    = self.field("outlet_flow_rate", 0.0, role=Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.outlet_temperature  = self.field("outlet_temperature", 0.0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)

        self.loss_factor         = self.field("loss_factor", 0.0, role=Roles.PARAMETERS, unit=Units.UNITLESS)

    def initialize(self) -> None:
        self.loss_factor = 1.0 - math.exp(- self.loss_coefficient / (self.inlet_flow_rate * self.cp_fluid))

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
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
