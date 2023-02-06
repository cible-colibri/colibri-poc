# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from core.conditions   import Conditions
from core.model        import Model
from core.parameters   import Parameters
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

class FlatPlateCollector(Model):

    # TODO: Define variables here, with information inside the Variable class about where it belongs (inputs, outputs, etc.), then
    #       add them to the proper lists instead of starting from the list then setting the variables (as attributes)
    #       The Model class will be less complex (_define_inputs, _define_outputs, etc.) will be removed, keeping only _define_variables
    def _define_variables(self) -> None:
        self.inlet_flow_rate = None
        self.inlet_temperature = None
        self.outside_air_temperature = None
        self.total_solar_incident_radiation = None
        self.outlet_flow_rate = None
        self.outlet_temperature = None

    def _define_inputs(self) -> list:
        inputs = [
                        Variable("inlet_flow_rate", 100.0, Units.KILOGRAM_PER_HOUR),
                        Variable("inlet_temperature", 40.0, Units.DEGREE_CELSIUS),
                        Variable("outside_air_temperature", 20.0, Units.DEGREE_CELSIUS),
                        Variable("total_solar_incident_radiation", 0.0, )
                  ]
        return inputs

    def _define_outputs(self) -> list:
        outputs = [
                        Variable("outlet_flow_rate", 100.0, Units.KILOGRAM_PER_HOUR),
                        Variable("outlet_temperature", 40.0, Units.DEGREE_CELSIUS),
                   ]
        return outputs

    def _define_conditions(self) -> list:
        conditions = []
        return conditions

    def _define_parameters(self) -> list:
        parameters = [
                        Variable("area", 1.0, Units.SQUARE_METER),
                        Variable("specific_heat_capacity", ),
                        Variable("linear_loss_coefficient", 4.0, Units.WATT_PER_SQUARE_METER_PER_KELVIN),
                        Variable("optical_efficiency", 0.7, Units.UNITLESS),
                        Variable("quadratic_loss_coefficient", 0.007, Units.WATT_PER_SQUARE_METER_PER_SQUARE_KELVIN),
                      ]
        return parameters

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0) -> None:
        # Rename variables from physics point of view
        a_0         = self.optical_efficiency
        a_1         = self.linear_loss_coefficient
        a_2         = self.quadratic_loss_coefficient
        g_total     = self.total_solar_incident_radiation
        delta_theta = (self.inlet_temperature + self.outlet_temperature) / 2 - self.outside_air_temperature
        theta_in    = self.inlet_temperature
        cp          = self.specific_heat_capacity
        m_dot_in    = self.inlet_flow_rate
        # Compute collector efficiency:  n = a_0 - a_1 x (ΔΘ / G_tot) - a_2 x - (ΔΘ² / G_tot)
        if g_total > 0:
            eta = a_0 - a_1 * (delta_theta / g_total) - (a_2 * delta_theta ** 2 / g_total)
        else:
            eta = 0
        # Compute fluid temperature at the flat-plate solar collector's outlet
        if (eta > 0) and ((cp * m_dot_in) > 0):
            self.outlet_temperature.value = theta_in + ((eta * self.area.value * g_total) / (cp * m_dot_in))
        else:
            self.outlet_temperature.value = theta_in
        # Set the mass flow rate at the outlet equal to the mass flow rate at the inlet
        self.outlet_flow_rate.value   = m_dot_in
        import random
        self.outlet_temperature.value = random.randint(0, 50)

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









