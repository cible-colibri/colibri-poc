# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import numpy

from scipy.interpolate import interp1d

# ========================================
# Internal imports
# ========================================

from core.conditions   import Conditions
from core.model        import Model
from core.parameters   import Parameters
from core.variable     import Variable
from utils.enums_utils  import Units

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class Pump(Model):

    def __init__(self, name: str, parameters: Parameters = None, conditions: Conditions = None):

        self.name       = name
        self.conditions = conditions
        self.inputs     = [
                                Variable("inlet_flow_rate"),
                                Variable("inlet_pressure"),
                                Variable("pump_speed"),

                           ]
        self.outputs    = [
                               Variable("outlet_flow_rate"),
                               Variable("power")
                           ]
        if parameters is None:
            parameters = Parameters().add(Variable("efficiency", 0.25, Units.METER))
        self.parameters = parameters

    # Run the pump model
    def run(self) -> None:
        """Run the pump model

        Parameters
        ----------

        Returns
        -------
        None

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # Generate pump performance curves as a numpy table
        pump_performance_curves = self._get_pump_perfomance_curves()
        # Split pump performance curves into flow rates and pressure drops
        pump_flow_rates         = pump_performance_curves[:, 0]
        pump_pressure_drops     = pump_performance_curves[:, 1]
        # Calculate flow-dp for grid from Cnetwork based on last time step
        # Coefficient with data of last time step
        # Inlet pressure corresponds to the pressure drop calculate from the balance
        cnetwork                = self.inlet_pressure / self.inlet_flow_rate ** 2
        dp_grid_table           = cnetwork * pump_flow_rates ** 2
        # Find closest result for pump-grid crossing
        teou                    = numpy.argwhere(numpy.abs(dp_grid_table - pump_pressure_drops) == numpy.min(numpy.abs((dp_grid_table - pump_pressure_drops))))
        # Get flow rate that corresponds to the crossing point
        self.outlet_flow_rate   = float(pump_flow_rates[teou])
        # Set outlet pressure to 0 (pressure_drop x 0)
        self.outlet_pressure    = 0
        # Pump efficiency is pump and motor efficiency product - typical values between 10 - 60 %
        self.power              = 9.81 * self.inlet_pressure / 1e4 * self.outlet_flow_rate / self.efficiency

    # Generate pump performance curves (characteristics of the pump based on the nominal flow rate) as a numpy table
    @staticmethod
    def _get_pump_perfomance_curves(nominal_flow_rate: float = 1.0) -> numpy.ndarray:
        """Generate pump performance curves (characteristics of the pump based on the nominal flow rate) as a numpy table

        Parameters
        ----------
        nominal_flow_rate : float
            Nominal flow rate of the pump [kg/s]

        Returns
        -------
        pump_perfomance_curves : numpy.ndarray
            Pump performance curves (characteristics of the pump based on the nominal flow rate)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # Table with ((flow_rate_1, dp_1), ... (flow_rate_n, dp_n))
        data_matrix = numpy.array([
                                    [0.0,  6.0],
                                    [2.0,  4.0],
                                    [4.0,  2.75],
                                    [6.0,  1.7],
                                    [8.0,  0.75],
                                    [10.0, 0.4],
                                    [11.0, 0.0],
                                  ])
        # Scale for flow rate [kg/s]
        x_coeff = 1.0 / 60.0 * nominal_flow_rate
        # Scale for pump head [Pa]
        y_coeff = 1e4
        # Covert first column to [kg/s] and second column to [Pa]
        data_matrix[:, 0] *= x_coeff
        data_matrix[:, 1] *= y_coeff
        # Compute maximum flow rate of pump
        flow_rate_max = numpy.max(data_matrix[:, 0])
        n_discret = 100  # generate n points
        # Create empty table
        pump_perfomance_curves = numpy.zeros((n_discret + 1, 2))
        # Generate flow rates in new table
        pump_perfomance_curves[:, 0] = numpy.array(range(0, n_discret + 1)) / n_discret * flow_rate_max
        # Can use quadratic interpolation with kind='quadratic'
        interpolate = interp1d(data_matrix[:, 0], data_matrix[:, 1])
        pump_perfomance_curves[:, 1] = interpolate(pump_perfomance_curves[:, 0])
        return pump_perfomance_curves
