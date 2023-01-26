# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import numpy

# ========================================
# Internal imports
# ========================================

from core.model        import Model
from core.conditions   import Conditions
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

class Pipe(Model):

    # Density
    # It could be calculated from temperatures (for each segment and temperature), but we avoid that with a constant value
    # TODO: Should it be in an object "Fluid" or something like that (because it will differ between air and water for example)
    DENSITY = 1_000.0

    def __init__(self, name: str, parameters: Parameters = None, conditions: Conditions = None):

        self.name       = name
        self.conditions = conditions
        self.inputs     = [
                                Variable("inlet_flow_rate", 0.0, Units.KILOGRAM_PER_SECOND, "Flow rate of the pump"),
                                Variable("inlet_temperature", 0.0, Units.DEGREE_CELCIUS, "Temperature of the flow rate of the pump"),
                           ]
        self.outputs    = [
                               Variable("Outlet flow"),
                               Variable("Outlet temperature"),
                           ]
        self.parameters = parameters


    def run(self, time_step) -> None:
        has_converged = False
        while not has_converged:
            self.compute_friction_coefficient()
            self.compute_pressure_drop()
            convergence_criterion   = numpy.abs(previous_friction_coefficient - self.friction_coefficient)
            covergence_successful   = convergence_criterion <= convergence_threshold
            has_iterations_exceeded = iteration > iteration_max
            if (covergence_successful is True) or (has_iterations_exceeded is True):
                has_converged = True
            previous_friction_coefficient = self.friction_coefficient
            iteration += 1


    def compute_pressure_drop(self, lambda_tube, internal_diameter, flow_rate):
        """
        function to calculate the pressure drop in a tube segment  based on the flow rate

        :param lamb_tube: Lambda value of the tube
        :param diameter_internal: Internal diameter of the tube
        :param flowrate: Flow rate in the tube
        :return:
        """
        # Do all calculations for positive value of flow rate
        flow_rate       = abs(flow_rate)
        # Calculate velocity from flow rate in [kg/s]
        velocity        = flow_rate / self.DENSITY / (internal_diameter ** 2 / 4.0 * numpy.pi)
        # Pressure drop in [Pa]
        pressure_drop_m = lambda_tube * self.DENSITY * velocity ** 2 / (2.0 * internal_diameter)

        return pressure_drop_m, velocity


    def compute_friction_coefficient(self):
        # TODO: If it is too anoying to do self.x.value, maybe we can do y = self.x.value, then use y
        # TODO: See to put it in constants.py (see where it goes)
        # Get the kinematic viscosity factors
        kinematic_viscosity_factors = self._get_kinematic_viscosity_factors()
        # Do all calculations for positive value of flow rate
        inlet_flow_rate             = abs(self.inlet_flow_rate.value)
        # Simple polynomial to define kinematic viscosity
        kinematic_viscosity         = kinematic_viscosity_factors[0] * self.inlet_temperature.value ** 3 \
                                      + kinematic_viscosity_factors[1] * self.inlet_temperature.value ** 2 \
                                      + kinematic_viscosity_factors[2] * self.inlet_temperature.value \
                                      + kinematic_viscosity_factors[3]
        # Reynolds number
        Re              = 4.0 * self.inlet_flow_rate.value / (self.internal_diameter.value * numpy.pi) / (kinematic_viscosity * self.DENSITY)
        not_converged_lambda = True
        lamb_tube_0 = lamb_tube

        has_converged = False
        while not has_converged:
            self.compute_friction_coefficient()
            self.compute_pressure_drop()
            convergence_criterion   = numpy.abs(previous_friction_coefficient - self.friction_coefficient)
            covergence_successful   = convergence_criterion <= convergence_threshold
            has_iterations_exceeded = iteration > iteration_max
            if (covergence_successful is True) or (has_iterations_exceeded is True):
                has_converged = True
            previous_friction_coefficient = self.friction_coefficient
            iteration += 1


        while not_converged_lambda:
            if inlet_flow_rate > 0:
                if Re < 2320.:  # laminary flow
                    lamb_tube = 64. / Re
                elif Re < 2500.:  # transitory flow so interpolate between laminar value and turbulent one (continuous function to avoid oscillation)
                    lambada_turb = (1. / (2. * numpy.log10(2.51 / (Re * lamb_tube ** 0.5) + k / (3.71 * internal_diameter)))) ** 2
                    lambada_lam = 64. / Re
                    lamb_tube = lambada_lam + (lambada_turb - lambada_lam) * (Re - 2320) / (2500. - 2320.)
                else:  # turbulent flow with colebrook equation
                    lamb_tube = (1. / (2. * numpy.log10(2.51 / (Re * lamb_tube ** 0.5) + k / (3.71 * internal_diameter)))) ** 2
            else:  # keep last lamb_tube
                pass
            delta_lambda = (lamb_tube - lamb_tube_0) / lamb_tube
            if delta_lambda < 1e-9:
                not_converged_lambda = False
            else:
                lamb_tube_0 = lamb_tube

        return lamb_tube

    @staticmethod
    def _get_kinematic_viscosity_factors():
        temperatures                = numpy.array([10, 20, 30, 40, 50, 60, 70, 80, 90])
        kinematic_viscosity_factors = numpy.array([1.308, 1.004, 0.801, 0.658, 0.554, 0.475, 0.414, 0.365, 0.326]) * 1e-6
        # kinematic viscosities = f(temperature) : array of factors using least squares polynomial fit of degree 3 (cubic equation)
        kinematic_viscosity_factors = numpy.polyfit(temperatures, kinematic_viscosity_factors, 3)
        return kinematic_viscosity_factors


