# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import numpy

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

class StorageTank(Model):

    # TODO: Define variables here, with information inside the Variable class about where it belongs (inputs, outputs, etc.), then
    #       add them to the proper lists instead of starting from the list then setting the variables (as attributes)
    #       The Model class will be less complex (_define_inputs, _define_outputs, etc.) will be removed, keeping only _define_variables
    def _define_variables(self) -> None:
        self.initial_temperature         = None
        self.inlet_temperature_1         = None
        self.inlet_temperature_2         = None
        self.height_fraction_of_inlet_1  = None
        self.height_fraction_of_inlet_2  = None
        self.inlet_flow_rate_1           = None
        self.inlet_flow_rate_2           = None
        self.height_fraction_of_outlet_1 = None
        self.height_fraction_of_outlet_2 = None
        self.outlet_temperature_1        = None
        self.outlet_temperature_2        = None
        self.outlet_flow_rate_1          = None
        self.outlet_flow_rate_2          = None
        self.height_node_1               = None
        self.height_node_2               = None

    def _define_inputs(self) -> list:
        inputs = [
                       Variable(
                                name      = "number_of_nodes",
                                value     = 2,
                                unit      = Units.UNITLESS,
                                linked_to = [
                                                ("inputs", Variable("height_fraction_of_inlet", 0.2, unit = Units.UNITLESS)),
                                                ("inputs", Variable("inlet_temperature", 40, unit=Units.DEGREE_CELSIUS)),
                                                ("inputs", Variable("inlet_flow_rate", 100, unit=Units.KILOGRAM_PER_HOUR)),
                                                ("outputs", Variable("height_fraction_of_outlet", 0.2, unit = Units.UNITLESS)),
                                                ("outputs", Variable("outlet_temperature", 40, unit=Units.DEGREE_CELSIUS)),
                                                ("outputs", Variable("outlet_flow_rate", 100, unit=Units.KILOGRAM_PER_HOUR)),
                                                ("parameters", Variable("height_node", 0.2, unit=Units.METER)),
                                             ],
                                model     = self,
                                )
                  ]
        return inputs

    def _define_outputs(self) -> list:
        outputs = []
        return outputs

    def _define_conditions(self) -> list:
        conditions = [
                        Variable("initial_temperature", 35, unit=Units.DEGREE_CELSIUS),
                      ]
        return conditions

    def _define_parameters(self) -> list:
        parameters = []
        return parameters

    def initialize(self) -> None:
        self._node_temperatures = numpy.ones(self.number_of_nodes.value) * self.initial_temperature.value

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0):
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
