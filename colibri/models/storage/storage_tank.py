# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import numpy

# ========================================
# Internal imports
# ========================================

from colibri.core.templates.inputs import Inputs
from colibri.core.model        import Model
from colibri.core.templates.parameters import Parameters
from colibri.core.templates.outputs import Outputs
from colibri.core.variables.field import Field
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

class StorageTank(Model):

    def __init__(self, name: str):
        super(StorageTank, self).__init__(name)
        self.name                        = name
        self.project                     = None
        self.initial_temperature = self.field("initial_temperature", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.inlet_temperature_1 = self.field("inlet_temperature_1", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.inlet_temperature_2 = self.field("inlet_temperature_2", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.height_fraction_of_inlet_1 = self.field("height_fraction_of_inlet_1", 0.2, Roles.INPUTS, unit = Units.UNITLESS)
        self.height_fraction_of_inlet_2 = self.field("height_fraction_of_inlet_2", 0.2, Roles.INPUTS, unit = Units.UNITLESS)
        self.inlet_flow_rate_1 = self.field("inlet_flow_rate_1", 100, Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.inlet_flow_rate_2 = self.field("inlet_flow_rate_2", 100, Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.height_fraction_of_outlet_1 = self.field("height_fraction_of_outlet_1", 0.2, Roles.OUTPUTS, unit = Units.UNITLESS)
        self.height_fraction_of_outlet_2 = self.field("height_fraction_of_outlet_2", 0.2, Roles.OUTPUTS, unit = Units.UNITLESS)
        self.outlet_temperature_1 = self.field("outlet_temperature_1", 40, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.outlet_temperature_2 = self.field("outlet_temperature_2", 40, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.outlet_flow_rate_1 = self.field("outlet_flow_rate_1", 100, Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.outlet_flow_rate_2 = self.field("outlet_flow_rate_2", 100, Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.height_node_1 = self.field("height_node_1", 0.2, Roles.PARAMETERS, unit=Units.METER)
        self.height_node_2 = self.field("height_node_2", 0.2, Roles.PARAMETERS, unit=Units.METER)
        self.number_of_nodes = self.field(
                                                    name      = "number_of_nodes",
                                                    default_value     = 2,
                                                    role      = Roles.PARAMETERS,
                                                    unit      = Units.UNITLESS,
                                                    linked_to = [
                                                                    Field("height_fraction_of_inlet", 0.2, Roles.INPUTS, unit=Units.UNITLESS),
                                                                    Field("inlet_temperature", 40, Roles.INPUTS, unit=Units.DEGREE_CELSIUS),
                                                                    Field("inlet_flow_rate", 100, Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR),
                                                                    Field("height_fraction_of_outlet", 0.2, Roles.OUTPUTS, unit = Units.UNITLESS),
                                                                    Field("outlet_temperature", 40, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS),
                                                                    Field("outlet_flow_rate", 100, Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR),
                                                                    Field("height_node", 0.2, Roles.PARAMETERS, unit=Units.METER),
                                                                 ],
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
        self._node_temperatures[:]   = self.inlet_temperature_1
        self._node_temperatures[:-1] = self.outlet_temperature_2

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
