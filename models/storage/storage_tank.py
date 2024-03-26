# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import numpy

# ========================================
# Internal imports
# ========================================

from core.templates.inputs import Inputs
from core.model        import Model
from core.templates.parameters import Parameters
from core.templates.outputs import Outputs
from core.variables.variable import Variable
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

class StorageTank(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                        = name
        self.project                     = None
        self.inputs                      = [] if inputs is None else inputs.to_list()
        self.outputs                     = [] if outputs is None else outputs.to_list()
        self.parameters                  = [] if parameters is None else parameters.to_list()
        self.initial_temperature         = Variable("initial_temperature", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.inlet_temperature_1         = Variable("inlet_temperature_1", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.inlet_temperature_2         = Variable("inlet_temperature_2", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.height_fraction_of_inlet_1  = Variable("height_fraction_of_inlet_1", 0.2, Roles.INPUTS, unit = Units.UNITLESS)
        self.height_fraction_of_inlet_2  = Variable("height_fraction_of_inlet_2", 0.2, Roles.INPUTS, unit = Units.UNITLESS)
        self.inlet_flow_rate_1           = Variable("inlet_flow_rate_1", 100, Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.inlet_flow_rate_2           = Variable("inlet_flow_rate_2", 100, Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.height_fraction_of_outlet_1 = Variable("height_fraction_of_outlet_1", 0.2, Roles.OUTPUTS, unit = Units.UNITLESS)
        self.height_fraction_of_outlet_2 = Variable("height_fraction_of_outlet_2", 0.2, Roles.OUTPUTS, unit = Units.UNITLESS)
        self.outlet_temperature_1        = Variable("outlet_temperature_1", 40, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.outlet_temperature_2        = Variable("outlet_temperature_2", 40, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.outlet_flow_rate_1          = Variable("outlet_flow_rate_1", 100, Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.outlet_flow_rate_2          = Variable("outlet_flow_rate_2", 100, Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.height_node_1               = Variable("height_node_1", 0.2, Roles.PARAMETERS, unit=Units.METER)
        self.height_node_2               = Variable("height_node_2", 0.2, Roles.PARAMETERS, unit=Units.METER)
        self.number_of_nodes             = Variable(
                                                    name      = "number_of_nodes",
                                                    value     = 2,
                                                    role      = Roles.PARAMETERS,
                                                    unit      = Units.UNITLESS,
                                                    linked_to = [
                                                                    Variable("height_fraction_of_inlet", 0.2, Roles.INPUTS, unit=Units.UNITLESS),
                                                                    Variable("inlet_temperature", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS),
                                                                    Variable("inlet_flow_rate", 100, Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR),
                                                                    Variable("height_fraction_of_outlet", 0.2, Roles.OUTPUTS, unit = Units.UNITLESS),
                                                                    Variable("outlet_temperature", 40, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS),
                                                                    Variable("outlet_flow_rate", 100, Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR),
                                                                    Variable("height_node", 0.2, Roles.PARAMETERS, unit=Units.METER),
                                                                 ],
                                                    model     = self,
                                                    )

    def initialize(self) -> None:
        self._node_temperatures = numpy.ones(self.number_of_nodes) * self.initial_temperature

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        self.outlet_flow_rate_1      = self.inlet_flow_rate_1
        self.outlet_flow_rate_2      = self.inlet_flow_rate_2
        self.outlet_temperature_1    = self.inlet_temperature_1
        self.outlet_temperature_2    = self.inlet_temperature_2
        self._node_temperatures[:]   = self.get_input("inlet_temperature_1").value
        self._node_temperatures[:-1] = self.get_output("outlet_temperature_1").value

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass

# ========================================
# Functions
# ========================================
