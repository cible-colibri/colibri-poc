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
from utils.enums_utils import (
                                FlowUnits,
                                LengthUnits,
                                TemperatureUnits,
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

    def _define_inputs(self) -> list:
        inputs = [
                       Variable(
                                name      = "number_of_nodes",
                                value     = 2,
                                unit      = Units.UNITLESS,
                                linked_to = [
                                                ("inputs", Variable("height_nodefraction_of_inlet", 0.2, unit = Units.UNITLESS)),
                                                ("inputs", Variable("inlet_temperature", 40, unit=TemperatureUnits.DEGREE_CELSIUS)),
                                                ("inputs", Variable("inlet_flow_rate", 100, unit=FlowUnits.KILOGRAM_PER_HOUR)),
                                                ("outputs", Variable("height_fraction_of_outlet", 0.2, unit = Units.UNITLESS)),
                                                ("outputs", Variable("outlet_temperature", 40, unit=TemperatureUnits.DEGREE_CELSIUS)),
                                                ("outputs", Variable("outlet_flow_rate", 100, unit=FlowUnits.KILOGRAM_PER_HOUR)),
                                                ("parameters", Variable("height_node", 0.2, unit=LengthUnits.METER)),
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
                        Variable("initial_temperature", 35, unit=TemperatureUnits.DEGREE_CELSIUS),
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
