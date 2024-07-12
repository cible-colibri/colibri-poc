# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


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

class FlatPlateCollector(Model):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name                           = name
        self.project                        = None
        self.inputs                         = [] if inputs is None else inputs.to_list()
        self.outputs                        = [] if outputs is None else outputs.to_list()
        self.parameters                     = [] if parameters is None else parameters.to_list()
        self.inlet_flow_rate = self.field("inlet_flow_rate", 100.0, role=Roles.INPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.inlet_temperature = self.field("inlet_temperature", 40.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.outside_air_temperature = self.field("outside_air_temperature", 20.0, role=Roles.INPUTS, unit=Units.DEGREE_CELSIUS)
        self.total_solar_incident_radiation = self.field("total_solar_incident_radiation", 0.0, role=Roles.INPUTS)
        self.outlet_flow_rate = self.field("outlet_flow_rate", 100.0, role=Roles.OUTPUTS, unit=Units.KILOGRAM_PER_HOUR)
        self.outlet_temperature = self.field("outlet_temperature", 40.0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.area = self.field("area", 1.0, role=Roles.PARAMETERS, unit=Units.SQUARE_METER)
        self.specific_heat_capacity = self.field("specific_heat_capacity", 4.186, role=Roles.PARAMETERS, )
        self.linear_loss_coefficient = self.field("linear_loss_coefficient", 4.0, role=Roles.PARAMETERS, unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN)
        self.optical_efficiency = self.field("optical_efficiency", 0.7, role=Roles.PARAMETERS, unit=Units.UNITLESS)
        self.quadratic_loss_coefficient = self.field("quadratic_loss_coefficient", 0.007, role=Roles.PARAMETERS, unit=Units.WATT_PER_SQUARE_METER_PER_SQUARE_KELVIN)

    def initialize(self):
        pass

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
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
            self.outlet_temperature = theta_in + ((eta * self.area * g_total) / (cp * m_dot_in))
        else:
            self.outlet_temperature = theta_in
        # Set the mass flow rate at the outlet equal to the mass flow rate at the inlet
        self.outlet_flow_rate = m_dot_in
        import random
        self.outlet_temperature = random.randint(0, 50)

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









