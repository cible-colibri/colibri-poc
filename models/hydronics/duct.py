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
from utils.enums_utils import Units

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

    # TODO: Define variables here, with information inside the Variable class about where it belongs (inputs, outputs, etc.), then
    #       add them to the proper lists instead of starting from the list then setting the variables (as attributes)
    #       The Model class will be less complex (_define_inputs, _define_outputs, etc.) will be removed, keeping only _define_variables
    def _define_variables(self) -> None:
        self.loss_coefficient    = None
        self.cp_fluid            = None
        self.inlet_flow_rate     = None
        self.inlet_temperature   = None
        self.outside_temperature = None
        self.outlet_flow_rate    = None
        self.outlet_temperature  = None

    def _define_inputs(self) -> list:
        inputs = [
                       Variable("loss_coefficient", 3.0, unit=Units.KILO_JOULE_PER_HOUR),
                       Variable("cp_fluid", 4.186, unit=Units.JOULE_PER_GRAM_PER_DEGREE_CELCIUS),
                       Variable("inlet_flow_rate", 100, unit=Units.KILOGRAM_PER_HOUR),
                       Variable("inlet_temperature", 40, unit=Units.DEGREE_CELSIUS),
                       Variable("outside_temperature", 20, unit=Units.DEGREE_CELSIUS),
                  ]
        return inputs

    def _define_outputs(self) -> list:
        outputs = [
                       Variable("outlet_flow_rate", unit=Units.KILOGRAM_PER_HOUR),
                       Variable("outlet_temperature", unit=Units.DEGREE_CELSIUS),
                   ]
        return outputs

    def _define_conditions(self) -> list:
        conditions = []
        return conditions

    def _define_parameters(self) -> list:
        parameters = [
                           Variable("loss_factor", 0.0, Units.UNITLESS),
                      ]
        return parameters

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
